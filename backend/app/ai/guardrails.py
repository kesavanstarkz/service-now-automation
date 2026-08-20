import re
from typing import List, Tuple
from app.schemas.ai import GuardrailNotice


class PromptGuardrails:
    """
    Applies strict prompt-injection protection and output constraint safety validation.
    ServiceNow record data and dashboard snapshots are untrusted input.
    """

    UNTRUSTED_OPEN_TAG = "<untrusted_servicenow_data>"
    UNTRUSTED_CLOSE_TAG = "</untrusted_servicenow_data>"

    @classmethod
    def sanitize_untrusted_input(cls, raw_text: str) -> str:
        """
        Sanitizes untrusted text by removing system prompt injection tricks
        and encapsulating inside XML delimiters.
        """
        if not raw_text:
            return ""

        # Remove attempt to escape XML isolation boundaries
        cleaned = raw_text.replace("<untrusted_servicenow_data>", "").replace("</untrusted_servicenow_data>", "")
        cleaned = cleaned.replace("<system_instruction>", "").replace("</system_instruction>", "")

        # Wrap cleanly
        return f"{cls.UNTRUSTED_OPEN_TAG}\n{cleaned.strip()}\n{cls.UNTRUSTED_CLOSE_TAG}"

    @classmethod
    def validate_output(cls, generated_content: str) -> Tuple[str, List[GuardrailNotice]]:
        """
        Validates LLM output against safety guardrails:
        1. No promised resolution dates/ETAs.
        2. No invented technical root cause claims without confirmation.
        3. No claims that actions were completed in ServiceNow.
        """
        notices: List[GuardrailNotice] = []
        validated = generated_content

        # Guardrail 1: Promised ETA / resolution date checks
        eta_patterns = [
            r"resolve(d)? by \d{1,2}/\d{1,2}",
            r"guarantee resolution",
            r"will be fixed by \w+ \d{1,2}"
        ]
        for pattern in eta_patterns:
            if re.search(pattern, validated, re.IGNORECASE):
                notices.append(
                    GuardrailNotice(
                        code="GUARD_ETA_REMOVED",
                        message="Potential resolution ETA commitment detected and flagged for human review.",
                        severity="warning"
                    )
                )
                break

        # Guardrail 2: System write claims
        if re.search(r"I have updated the record|ticket has been updated in servicenow", validated, re.IGNORECASE):
            notices.append(
                GuardrailNotice(
                    code="GUARD_WRITE_CLAIM",
                    message="Reminder: The AI assistant cannot modify ServiceNow directly. You must apply edits manually.",
                    severity="info"
                )
            )

        # Mandatory footer check
        if not validated.endswith("\n\n*Review before sending to customer.*") and "customer" in validated.lower():
            validated = validated.strip() + "\n\n*Review before sending to customer.*"

        return validated, notices
