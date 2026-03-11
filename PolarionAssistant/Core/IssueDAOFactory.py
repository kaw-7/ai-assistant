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
            
            # 1. Bypass the wrapper to grab the raw Zeep client
            tracker_zeep_client = connector.client.services['Tracker']['client']

            # 2. Now ask the raw Zeep client for the Text factory!
            TextType = tracker_zeep_client.get_type('{http://ws.polarion.com/types}Text')
            EnumType = tracker_zeep_client.get_type('{http://ws.polarion.com/TrackerWebService-types}EnumOptionId')
            
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
            # Convert to Zeep object
            source_enum_obj = EnumType(id=issueDTO.source.value)
            status_enum_obj = EnumType(id=issueDTO.status.value)  

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
                    "status": status_enum_obj, #risk_exists, not_evaluated, no_risk
                    "description": {
                        "type": "text/html",  
                        "content": issueDTO.description,     
                        "contentLossy": False  
                    },
                    "customFields": {  # All custom fields at once!
                        "DefectID": issueDTO.defect_id,
                        "DefectDescription": defect_desc_obj,
                        "Assessment": assessment_obj,
                        "Source": source_enum_obj,
                        "DefectDescription": defect_desc_obj
                    }
                }
            )
            new_issue.status = status_enum_obj #risk_exists, not_evaluated, no_risk
            end = time.perf_counter()
            print(f"Elapsed create: {(end - start):.3f} seconds")
            return new_issue

        except Exception:
            print(f"❌ IssueDAOFactory: An error occurred:\n{traceback.format_exc()}")
            return None

        