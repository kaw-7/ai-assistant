import traceback
import time

from dataclasses import dataclass
import config as PConf
from PolarionAssistant.Model.DAO.IssueFields import *

class IssueDAOFactory():

    @staticmethod
    def create(connector, issueDTO):
        try:
            start = time.perf_counter()
            new_issue = connector.project.createWorkitem(
                workitem_type="defect_evaluation", 
                new_workitem_fields={
                    "title":issueDTO.title,
                    "author":{
                        'description': None,
                        'disabledNotifications': True,
                        'email': issueDTO.author_email,
                        'homePageContent': None,
                        'id': issueDTO.polarion_username,
                        'name': issueDTO.author_name,
                        'voteURIs': None,
                        'watcheURIs': None,
                        'uri': 'subterra:data-service:objects:/default/${User}' + issueDTO.polarion_username,
                        'unresolvable': False
                    }, 
                    "description": {
                        "type": "text/html",  # You can also use "text/plain"
                        "content": issueDTO.description,     # Put your actual description here (can include HTML tags)
                        "contentLossy": False  # Add this required boolean
                    }
                }
            )
            end = time.perf_counter()
            print(f"Elapsed create: {(end - start):.3f} seconds")
            start = time.perf_counter()
            new_issue.status = {'id': issueDTO.status.value} #risk_exists, not_evaluated, no_risk
            end = time.perf_counter()
            print(f"Elapsed status: {(end - start):.3f} seconds")
            start = time.perf_counter()
            new_issue.setCustomField("DefectID", issueDTO.defect_id)
            end = time.perf_counter()
            print(f"Elapsed set custom field: {(end - start):.3f} seconds")
            start = time.perf_counter()
            # 1. Bypass the wrapper to grab the raw Zeep client
            tracker_zeep_client = connector.client.services['Tracker']['client']

            # 2. Now ask the raw Zeep client for the Text factory!
            TextType = tracker_zeep_client.get_type('{http://ws.polarion.com/types}Text')
            EnumType = tracker_zeep_client.get_type('{http://ws.polarion.com/TrackerWebService-types}EnumOptionId')
            
            end = time.perf_counter()
            print(f"Elapsed tracker-client: {(end - start):.3f} seconds")
            start = time.perf_counter()
            
            # 3. Instantiate formal Zeep objects instead of plain dictionaries
            defect_desc_obj = TextType(
                type='text/html',
                content=issueDTO.defect_description,
                contentLossy=False
            )
    
            assessment_obj = TextType(
                type='text/html',
                content=issueDTO.risk_assessment,
                contentLossy=False
            )

            source_enum_obj = EnumType(id=issueDTO.source.value)

            # 4. Inject the strongly-typed objects into the custom fields
            new_issue.setCustomField("DefectDescription", defect_desc_obj)
            new_issue.setCustomField("Assessment", assessment_obj)
            new_issue.setCustomField('Source', source_enum_obj) #'fixedInNewerVersion' knownBug
            end = time.perf_counter()
            print(f"Elapsed field-modi: {(end - start):.3f} seconds")
            start = time.perf_counter()
            new_issue.save()
            end = time.perf_counter()
            print(f"Elapsed save: {(end - start):.3f} seconds")
            return new_issue

        except Exception:
            print(f"❌ IssueDAOFactory: An error occurred:\n{traceback.format_exc()}")
            return None

        