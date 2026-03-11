from abc import ABC, abstractmethod

class AIContext(ABC):
    """The 'Contract'. Any AI context tool must have these methods."""

    @abstractmethod
    def save_question(self, prompt: str):
        pass

    @abstractmethod
    def save_response(self, prompt: str):
        pass

    @abstractmethod
    def retrieve_context(self) -> str:
        pass