"""
app/ai/providers/base.py
Abstract base class for AI Providers.
Enables provider-neutral AI governance and offline testing mocks.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.ai.schemas import AIAnalysisResponse


class AIProvider(ABC):
    """
    Abstract AI Provider Interface.
    All AI providers (Gemini, local mocks, etc.) MUST implement this interface.
    """

    PROVIDER_NAME: str = "UNKNOWN"

    @abstractmethod
    async def analyze(
        self,
        system_instruction: str,
        user_question: str,
        structured_context: Dict[str, Any],
        model_name: Optional[str] = None
    ) -> AIAnalysisResponse:
        """
        Execute AI security analysis over structured, tenant-authorized security context.
        Returns a validated AIAnalysisResponse schema.
        """
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Check if provider credentials/API connectivity are valid."""
        ...
