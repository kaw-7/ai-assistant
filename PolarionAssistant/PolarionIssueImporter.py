#!/usr/bin/env python3
"""
Polarion Python Client - Connection Test
Install: pip install polarion
"""
from PolarionAssistant.Core.PolarionConnector import PolarionConnector
from PolarionAssistant.Core.PolarionWorker import PolarionWorker
from PolarionAssistant.Model.IssueDTO import IssueDTO
from PolarionAssistant.Model.DAO.IssueFields import *  #IssueStatus, IssueSource
from PolarionAssistant.Core.PolarionConnector import PolarionConnector
from PolarionAssistant.Core.ItemUtil import ItemUtil
from PolarionAssistant.Core.IssueDAOFactory import IssueDAOFactory
from PolarionAssistant.Core.IssueParser import IssueParser
import config as PConf
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import sys

class PolarionIssueImporter(PolarionWorker):
    
    def __init__(self):
        super().__init__()
    
    def GetDocItems(self) -> tuple[str, str, str, str]:
      
        # Get project
        project = self._client.getProject(PConf.PROJECT_ID)
        
        # Get document
        doc = project.getDocument(PConf.DOC_NAME)
        if doc is None:
            print(f"❌ Document '{PConf.DOC_NAME}' not found!")
            sys.exit(1)
        print(f"✅ Loaded '{doc.title}'")
              
        heading_item = ItemUtil.find_heading_item_by_name(doc, PConf.DOC_INPUT_HEADING)
        if heading_item is None:
            print(f"❌ Could not find heading: {PConf.DOC_INPUT_HEADING}!")
            sys.exit(1)
    
        full_name, email = self._connector.get_current_user_info()
        if full_name is None or email is None:
            print(f"❌ Could not find full name or email of the author: {self._connector.polarion_username}!")
            sys.exit(1)
        
        return doc, heading_item, full_name, email
    
    def ImportIssuesInPolarion(self):
        
        print("🎉 Ready to create issues!")
        parser = IssueParser(PConf.ISSUE_INPUT_FILE)
        parser.read_file()
        
        doc, heading_item, full_name, email = self.GetDocItems()
        
        # Pre-set author fields (sequential, fast)
        for issueDTO in parser.issues:
            issueDTO.author_name = full_name
            issueDTO.author_email = email
            issueDTO.polarion_username = self._connector.polarion_username
            #print(issueDTO)
        
        # Parallel execution - fire and forget
        print(f"\n🚀 Processing {len(parser.issues)} issues in parallel...")
        
        new_issues = []
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=11) as executor:
            # Direct function calls - no partial needed!
            futures = [executor.submit(IssueDAOFactory.create, self._connector, issueDTO) 
                       for issueDTO in parser.issues]
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)  # Also adds Ctrl+C safety
                    if result:
                        new_issues.append(result)
                        print(f"✅ Success: {len(new_issues)} total")
                    else:
                        print("⚠️ Result was None/empty - skipped")
                        
                except TimeoutError:  # ← ADD THIS LINE
                    print("⏰ TIMEOUT after 30s - skipping")
                    future.cancel()
                    # Optionally log traceback: import traceback; traceback.print_exc()
                
                
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
    importer = PolarionIssueImporter()
    importer.ImportIssuesInPolarion()
    
    
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



