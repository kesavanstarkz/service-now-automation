from abc import ABC, abstractmethod
import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    @abstractmethod
    async def generate_completion(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        """
        Generates completion response from LLM provider.
        Returns tuple of (content, model_name).
        """
        pass


class MockLLMProvider(BaseLLMClient):
    """
    Mock LLM Provider for local development without live API keys.
    Returns structured, realistic responses.
    """

    async def generate_completion(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        if "summarize_incident" in user_prompt or "Executive Summary" in user_prompt:
            content = (
                "### Incident Summary\n"
                "- **Core Issue**: User reports severe performance degradation after recent update.\n"
                "- **Current Status**: Work in progress. Remote diagnostics underway.\n"
                "- **Key Work Notes History**: Diagnostic scan confirmed high memory footprint in background processes.\n"
                "- **Recommended Next Action**: Verify background startup services and schedule software patch deployment."
            )
        elif "summarize_queue" in user_prompt or "Dashboard" in user_prompt:
            content = (
                "### Queue Attention Summary\n"
                "- **High Priority Items**: 1 critical incident awaiting immediate triage.\n"
                "- **Queue Volume & SLAs**: 15 incidents active; 2 approaching SLA breach in < 1 hour.\n"
                "- **Immediate Action Recommended**: Assign unassigned ticket INC0013496 to IT Service Desk group."
            )
        elif "improve_text" in user_prompt:
            content = (
                "Dear Customer,\n\n"
                "Thank you for contacting IT Support. We have investigated the system performance issues you reported and applied corrective configuration updates. "
                "Please restart your device and verify if the issue persists.\n\n"
                "Best regards,\nIT Service Desk"
            )
        else:
            content = (
                "Dear Customer,\n\n"
                "We are currently investigating your reported issue regarding laptop performance degradation. "
                "Our engineering team has performed preliminary diagnostics and identified potential software updates required.\n\n"
                "We will provide a status update as soon as further progress is confirmed. If you have additional details to share, please reply to this update.\n\n"
                "Best regards,\nIT Support Team"
            )

        return content, "mock-dev-provider"


class GroqLLMProvider(BaseLLMClient):
    """
    Groq LLM Provider using OpenAI-compatible chat completions API endpoint.
    """

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate_completion(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        if not self.api_key:
            logger.warning("Groq API key not set. Falling back to Mock LLM Provider.")
            return await MockLLMProvider().generate_completion(system_prompt, user_prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1024
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(self.api_url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    return content, self.model
                else:
                    logger.error(f"Groq API error {res.status_code}: {res.text}")
                    raise RuntimeError(f"Groq API returned error status {res.status_code}")
        except Exception as e:
            logger.error(f"Groq API call failed: {str(e)}. Falling back to Mock provider.")
            return await MockLLMProvider().generate_completion(system_prompt, user_prompt)


def get_llm_client() -> BaseLLMClient:
    """Factory function for acquiring configured LLM provider."""
    provider = settings.LLM_PROVIDER.lower()
    if provider == "groq":
        return GroqLLMProvider()
    return MockLLMProvider()
