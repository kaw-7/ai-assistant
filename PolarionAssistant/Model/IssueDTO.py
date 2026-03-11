from dataclasses import dataclass
from typing import Optional
from enum import StrEnum
from PolarionAssistant.Model.DAO.IssueFields import *  #IssueStatus, IssueSource

@dataclass
class IssueDTO:
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    polarion_username: Optional[str] = None
    title: Optional[str] = ""
    description: Optional[str] = ""
    defect_id: Optional[str] = None
    defect_description: Optional[str] = ""
    risk_assessment: Optional[str] = ""    
    source: Optional[str] = IssueSource.KNOWN_PROBLEM_BY_VENDOR
    status: Optional[str] = IssueStatus.NOT_EVALUATED
    
    def __post_init__(self):
        """Ensure snake_case access matches Python conventions"""
        # Optional: auto-convert camelCase if needed
        pass


