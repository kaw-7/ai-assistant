from abc import ABC, abstractmethod
# TO DO: add the general implementation for some of the Provider;s methods here as those are the same/similar for
# save_question save_response retrieve_context _get_key_from_env
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