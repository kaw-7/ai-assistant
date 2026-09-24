from dataclasses import dataclass
from typing import Optional
from enum import StrEnum

class SourceDTO(StrEnum):
    KNOWN_PROBLEM_BY_VENDOR = "KNOWN_PROBLEM_BY_VENDOR"
    KNOWN_PROBLEM_3RD_PARTY = "KNOWN_PROBLEM_3RD_PARTY"
    CORRECTION_IN_REL_NOTES = "CORRECTION_IN_REL_NOTES"
    KNOWN_PROBLEM_IN_NEWER_VERS = "KNOWN_PROBLEM_IN_NEWER_VERS"
    OCCURED_AT_OTTOBOCK = "OCCURED_AT_OTTOBOCK"
    OTHER_SOURCE = "OTHER_SOURCE"

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
    source: Optional[str] = SourceDTO.KNOWN_PROBLEM_BY_VENDOR.value
    status: Optional[str] = "NOT_EVALUATED"
    
    def __post_init__(self):
        """Ensure snake_case access matches Python conventions"""
        # Optional: auto-convert camelCase if needed
        pass
    
    def __str__(self):
        return f"""🔍 **Issue Summary**
        📛 ID: {self.defect_id}
        👤 Author: {self.author_name} ({self.author_email})
        📝 Description: {self.description[:100]}{'...' if len(self.description) > 100 else ''}
        ⚠️  Risk: {self.status.upper()} | Source: {self.source.replace('knownBug', 'Known Bug').replace('fixedInNewerVersion', 'Fixed in newer version')}
        📊 Assessment: {self.risk_assessment[:120]}{'...' if len(self.risk_assessment) > 120 else ''}"""


