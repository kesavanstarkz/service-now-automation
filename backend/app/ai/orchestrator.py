import json
import logging
from typing import Optional

from app.schemas.records import IncidentRecord
from app.schemas.ai import RecordAIRequest, DashboardAIRequest, AIResponse
from app.servicenow.client import ServiceNowClient
from app.ai.guardrails import PromptGuardrails
from app.ai.prompt_manager import PromptManager
from app.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    AI Orchestrator implementing 5-Layer Prompt Context Architecture:
    1. System instructions & safety rules
    2. Application task definition
    3. Trusted application context
    4. Untrusted ServiceNow data (Record fields / Work notes / Dashboard snapshot)
    5. User explicit prompt / request
    """

    def __init__(self, sn_client: Optional[ServiceNowClient] = None):
        self.sn_client = sn_client or ServiceNowClient()
        self.llm_client = get_llm_client()

    async def process_record_request(self, req: RecordAIRequest) -> AIResponse:
        # Step 1: Fetch authoritative record data from ServiceNow Table API
        record: IncidentRecord = await self.sn_client.get_incident(req.record_number)

        # Step 2: Format & sanitize untrusted ServiceNow content
        raw_context = (
            f"Number: {record.number}\n"
            f"Short Description: {record.short_description}\n"
            f"Description: {record.description}\n"
            f"State: {record.state}\n"
            f"Priority: {record.priority}\n"
            f"Assignment Group: {record.assignment_group}\n"
            f"Assigned To: {record.assigned_to}\n"
            f"Caller: {record.caller_id}\n"
            f"Work Notes:\n"
        )
        for note in record.work_notes:
            raw_context += f" - [{note.sys_created_on} by {note.sys_created_by}]: {note.value}\n"

        untrusted_data = PromptGuardrails.sanitize_untrusted_input(raw_context)

        # Step 3: Build user application prompt using PromptManager
        user_prompt = PromptManager.get_prompt(
            action=req.action,
            record_type=req.record_type,
            record_number=record.number,
            untrusted_data=untrusted_data,
            user_prompt=req.custom_instructions,
            text_to_improve=req.text_to_improve
        )

        # Step 4: Execute LLM completion with prompt isolation
        raw_output, model_used = await self.llm_client.generate_completion(
            system_prompt=PromptManager.SYSTEM_INSTRUCTIONS,
            user_prompt=user_prompt
        )

        # Step 5: Validate output against safety guardrails
        validated_content, notices = PromptGuardrails.validate_output(raw_output)

        return AIResponse(
            mode="record",
            action=req.action,
            content=validated_content,
            prompt_version=PromptManager.VERSION,
            model_used=model_used,
            guardrail_notices=notices,
            record_number=record.number
        )

    async def process_dashboard_request(self, req: DashboardAIRequest) -> AIResponse:
        # Step 1: Format bounded structured snapshot
        snapshot_data = {
            "mode": "dashboard",
            "widgets": [w.model_dump() for w in req.widgets],
            "visibleRows": [r.model_dump() for r in req.visibleRows]
        }
        raw_context = json.dumps(snapshot_data, indent=2)

        # Step 2: Sanitize untrusted snapshot data
        untrusted_data = PromptGuardrails.sanitize_untrusted_input(raw_context)

        # Step 3: Build prompt
        user_prompt = PromptManager.get_prompt(
            action=req.action,
            untrusted_data=untrusted_data,
            user_prompt=req.custom_instructions
        )

        # Step 4: Execute LLM completion
        raw_output, model_used = await self.llm_client.generate_completion(
            system_prompt=PromptManager.SYSTEM_INSTRUCTIONS,
            user_prompt=user_prompt
        )

        # Step 5: Validate output
        validated_content, notices = PromptGuardrails.validate_output(raw_output)

        return AIResponse(
            mode="dashboard",
            action=req.action,
            content=validated_content,
            prompt_version=PromptManager.VERSION,
            model_used=model_used,
            guardrail_notices=notices
        )
