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
from concurrent.futures import ThreadPoolExecutor

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
    
    parser = IssueParser(PConf.ISSUE_INPUT_FILE)
    parser.read_file()
    
    # Pre-set author fields (sequential, fast)
    for issueDTO in parser.issues:
        issueDTO.author_name = full_name
        issueDTO.author_email = email
        issueDTO.polarion_username = connector.polarion_username
        #print(issueDTO)
    
    # Parallel execution - fire and forget
    print(f"\n🚀 Processing {len(parser.issues)} issues in parallel...")
        
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=11) as executor:
        # Direct function calls - no partial needed!
        futures = [executor.submit(IssueDAOFactory.create, connector, issueDTO) 
                   for issueDTO in parser.issues]
        new_issues = [f.result() for f in futures if f.result()]
            
    # 2. SEQUENTIAL MOVES only (conflict-free)
    start_move = time.perf_counter()
    print("🔄 Moving issues sequentially (avoids conflicts)...")
    for new_issue in new_issues:
        new_issue.moveToDocument(doc, heading_item)
    end_move = time.perf_counter()
    print(f"⏱️  move time: {(end_move - start_move):.3f}s")
    
    end = time.perf_counter()
    print("\n🎉 Parallel complete!")
    print(f"⏱️  Total parallel time: {(end - start):.3f}s")
    

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



