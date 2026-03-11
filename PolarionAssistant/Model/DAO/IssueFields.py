from enum import StrEnum

class IssueStatus(StrEnum):
    RISK = "risk_exists"
    NO_RISK = "no_risk"
    NOT_EVALUATED = "not_evaluated"

class IssueSource(StrEnum):
    KNOWN_PROBLEM_BY_VENDOR = "knownBug"
    KNOWN_PROBLEM_3RD_PARTY = "3rdPartyBug"
    CORRECTION_IN_REL_NOTES = "fixedInNewerVersion"
    KNOWN_PROBLEM_IN_NEWER_VERS = "knownBugNewerVersion"
    OCCURED_AT_OTTOBOCK = "ottobock"
    OTHER_SOURCE = "otherSource"