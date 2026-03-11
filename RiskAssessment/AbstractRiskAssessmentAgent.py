from abc import ABC, abstractmethod


class AbstractRiskAssessmentAgent(ABC):
    """The 'Contract'. Any AbstractRiskAssessmentAgent must have these methods."""

    @abstractmethod
    def process_issues(self):
        pass