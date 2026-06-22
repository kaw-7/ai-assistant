import re
from dataclasses import dataclass
import os
import sys
from typing import List
import traceback

import config as PConf
from PolarionAssistant.Model.IssueDTO import IssueDTO
from PolarionAssistant.Model.DAO.IssueFields import *

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

        options = {IssueStatus.RISK, IssueStatus.NO_RISK, IssueStatus.NOT_EVALUATED}
        if issue.status in options:
            return
        else:
            value_pattern = rf"no.?risk.*"
            match = re.search(value_pattern, issue.status, re.DOTALL | re.IGNORECASE)
            if match:
                issue.status = IssueStatus.NO_RISK
                return
            value_pattern = rf"risk.?exist.*"
            match = re.search(value_pattern, issue.status, re.DOTALL | re.IGNORECASE)
            if match:
                issue.status = IssueStatus.RISK
                return
            issue.status = IssueStatus.NOT_EVALUATED
          
    @staticmethod
    def _fix_source(issue: IssueDTO):

        options = {IssueSource.KNOWN_PROBLEM_BY_VENDOR, 
                   IssueSource.KNOWN_PROBLEM_3RD_PARTY, 
                   IssueSource.CORRECTION_IN_REL_NOTES, 
                   IssueSource.KNOWN_PROBLEM_IN_NEWER_VERS, 
                   IssueSource.OCCURED_AT_OTTOBOCK,
                   IssueSource.OTHER_SOURCE}
        if issue.source in options:
            return
        else:
            issue.source = IssueSource.KNOWN_PROBLEM_BY_VENDOR