from abc import ABC, abstractmethod

# TO DO: add the general implementation for some of the Provider;s methods here as those are the same/similar for
# save_question save_response retrieve_context _get_key_from_env
class AIProvider(ABC):
    """The 'Contract'. Any AI tool must have these methods."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass