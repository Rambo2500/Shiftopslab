from abc import ABC, abstractmethod
from typing import Dict, Any

class ModelAdapter(ABC):
    """
    Abstract Base Class for LLM Adapters.
    Ensures a consistent interface for intent drafting and context harvesting.
    """

    @abstractmethod
    def draft_intent(self, user_request: str) -> Dict[str, Any]:
        """
        Translates a natural language request into a valid Intent JSON.
        """
        pass

    @abstractmethod
    def harvest_context(self, query: str) -> str:
        """
        Gathers contextual information based on a query.
        """
        pass
