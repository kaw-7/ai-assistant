#!/usr/bin/env python3
"""
Polarion Python Client - Connection Test
Install: pip install polarion
"""

from PolarionAssistant.Model.IssueDTO import IssueDTO
from PolarionAssistant.Model.DAO.IssueFields import *  #IssueStatus, IssueSource
from PolarionAssistant.Core.PolarionConnector import PolarionConnector
from PolarionAssistant.Core.ItemUtil import ItemUtil
from PolarionAssistant.Core.IssueDAOFactory import IssueDAOFactory
from PolarionAssistant.Core.IssueParser import IssueParser
import config as PConf
import time


def polarionImport():
    # Create instance
    connector = PolarionConnector()
    
    # Connect (like polarion_connect())
    client = connector.connect()
    if client is None:
        print("❌ Could not connect to polarion server!")
        exit(1)
    
    # Get document (like get_polarion_doc())
    doc = connector.get_document()
    if doc is None:
        print("❌ Document " + PConf.DOC_NAME + " not found!")
        exit(1)
          
    print("🎉 Ready to create issues!")

    heading_item = ItemUtil.find_heading_item_by_name(doc, PConf.DOC_INPUT_HEADING)
    if heading_item is None:
        print(f"❌ Could not find heading: {PConf.DOC_INPUT_HEADING}!")
        exit(1)

    full_name, email = connector.get_current_user_info()
    if full_name is None or email is None:
        print(f"❌ Could not find full name or email of the author: {connector.polarion_username}!")
        exit(1)
    
    create_total = 0
    move_total = 0
    parser = IssueParser(PConf.ISSUE_INPUT_FILE)
    parser.read_file()
    for issueDTO in parser.issues:
        start_create = time.perf_counter()
        issueDTO.author_name = full_name
        issueDTO.author_email = email
        issueDTO.polarion_username = connector.polarion_username
        print(issueDTO)
        new_issue = IssueDAOFactory.create(connector, issueDTO)
        end_create = time.perf_counter()
        create_total += (end_create - start_create)
        if new_issue is not None:
            start_move = time.perf_counter()
            with new_issue as wi:  # Buffers changes
                wi.moveToDocument(doc, heading_item)
            end_move = time.perf_counter()
            move_total += (end_move - start_move)
        else:
            print(f"❌ issueDTO with id: {issueDTO.defect_id} skipped!")

    print(f"Elapsed create: {(create_total):.3f} seconds")
    print(f"Elapsed move: {(move_total):.3f} seconds")

if __name__ == "__main__":
    polarionImport()
    
    
    #issue = IssueDTO(
    #    author_name=full_name, 
    #    author_email=email, 
    #    polarion_username=connector.polarion_username,
    #    defect_id="id06", 
    #    source=IssueSource.KNOWN_PROBLEM_IN_NEWER_VERS, 
    #    status=IssueStatus.RISK,
    #    description="short description1",
    #    defect_description="This is very very long long description...",
    #    risk_assessment="Issue is of medium risk!")
    

#custom_fields = wi.customFields
#if custom_fields:
#    for field in custom_fields:
#        value = wi.getCustomField(field)
#        print(f"   - {field}: {value}")d: {str(e)}")


