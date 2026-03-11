from abc import ABC, abstractmethod

class AIProvider(ABC):
    """The 'Contract'. Any AI tool must have these methods."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass