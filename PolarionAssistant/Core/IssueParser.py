import re
from dataclasses import dataclass
import os
import sys
from typing import List
import traceback

import PolarionAssistant.issue_importer_config as PConf
from PolarionAssistant.Model.IssueDTO import IssueDTO, SourceDTO, StatusDTO
from PolarionAssistant.Model.DAO.IssueFields import IssueStatus, IssueSource

class IssueParser():
    """IssueParser parser parses issues generated from AI
    which are in a structured format within/from a file (file_path)
    into Issue Data Transfer Object (IssueDTO) type"""

    def __init__(self, file_path = None):
        self.file_path = file_path
        self.issues_as_string = None
        self.issues = []

    def read_file(self):
        if(self.file_path is None):
            return
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
                self.issues_as_string = f.read()
            self.preprocess_initial_string_issues()
            self.issues = IssueParser.parse_markdown_to_dto(self.issues_as_string)
        except Exception:
            print(f"❌ IssueParser: An error occurred:\n{traceback.format_exc()}")
    
    def preprocess_initial_string_issues(self):
        if(self.issues_as_string is None):
            return
        
        start_index = self.issues_as_string.find(PConf.ISSUE_MARKER_BEG)
        # Find the index of the last occurrence of "]]"
        end_index = self.issues_as_string.rfind(PConf.ISSUE_MARKER_END)

        if start_index != -1 and end_index != -1 and start_index < end_index:
            # Add the length of the end marker to include it in the slice
            self.issues_as_string = self.issues_as_string[start_index : end_index + len(PConf.ISSUE_MARKER_END)]
            # print(result) # Output: [[asdf]] [[gewr]]
        else:
            print("Markers not found in correct order")

    @staticmethod
    def parse_markdown_to_dto(raw_text: str) -> List[IssueDTO]:
        # Split the text into individual blocks based on the END marker
        blocks = raw_text.split(PConf.ISSUE_END_MARKER)
        issues = []

        # Regex to find content between [[ Field Name ]] and the next field or newline
        # Mapping the Markdown header to the IssueDTO attribute name
        field_map = {
            "Description": "description",
            "Defect ID": "defect_id",
            "Defect Description": "defect_description",
            "Source": "source",
            "Risk Assessment": "risk_assessment",
            "Status": "status"
        }

        for block in blocks:
            if not block.strip():
                continue
            
            data = {}
            for header, attr in field_map.items():
                # Pattern: matches the header, then captures everything until the next '[['
                pattern = rf"\[\[ {header} \]\]\n?(.*?)(?=\n?\[\[|$)"
                match = re.search(pattern, block, re.DOTALL)
                if match:
                    data[attr] = match.group(1).strip()

            if data:
                current_issue = IssueDTO(**data)
                IssueParser._fix_status(current_issue)
                IssueParser._fix_source(current_issue)
                issues.append(current_issue)
                
        return issues
    
    @staticmethod
    def _fix_status(issue: IssueDTO):

        options = {StatusDTO.RISK, StatusDTO.NO_RISK, StatusDTO.NOT_EVALUATED}
        if issue.status in options:
            issue.status = IssueStatus[issue.status].value
            return
        else:
            # the risk instructions ask for free text: "Risk Exists" / "No risk"
            value_pattern = rf"no.?risk.*"
            match = re.search(value_pattern, issue.status, re.DOTALL | re.IGNORECASE)
            if match:
                issue.status = IssueStatus.NO_RISK.value
                return
            value_pattern = rf"risk.?exist.*"
            match = re.search(value_pattern, issue.status, re.DOTALL | re.IGNORECASE)
            if match:
                issue.status = IssueStatus.RISK.value
                return
            issue.status = IssueStatus.NOT_EVALUATED.value
          
    @staticmethod
    def _fix_source(issue: IssueDTO):
        options = {SourceDTO.KNOWN_PROBLEM_BY_VENDOR, 
                   SourceDTO.KNOWN_PROBLEM_3RD_PARTY, 
                   SourceDTO.CORRECTION_IN_REL_NOTES, 
                   SourceDTO.KNOWN_PROBLEM_IN_NEWER_VERS, 
                   SourceDTO.OCCURED_AT_OTTOBOCK,
                   SourceDTO.OTHER_SOURCE}
        polarion_ids = {member.value for member in IssueSource}
        if issue.source in options:
            issue.source = IssueSource[issue.source].value
            return
        elif issue.source in polarion_ids:
            return          # a report that was imported once already
        else:
            issue.source = IssueSource.KNOWN_PROBLEM_BY_VENDOR.value