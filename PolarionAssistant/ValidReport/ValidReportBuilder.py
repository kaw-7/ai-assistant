import ValidReport.valid_report_config as vr_conf
from Core.PolarionWorker import PolarionWorker
from typing_extensions import override
import traceback
import sys

class ValidReportBuilder(PolarionWorker):
    def __init__(self):
        super().__init__()
    
    @override
    def PrintDocDetails(self):
        pass
    
    def createFinalDoc(self):
        try:
            new_doc = self._createDoc()
            if(new_doc is None):
                raise("Could not create a stand alone copy of the template!")
            self._changeDocToolName(new_doc)
        except Exception:
            full_error = traceback.format_exc()
            print(f"❌ Error during polarion manipulation: {full_error}")
            sys.exit(1)
            
    def _createDoc(self):
        # Reuse the template
        return self.getTemplate(vr_conf.PROJECT_ID, vr_conf.VALID_REPORT_TEMPLATE).reuse(
            vr_conf.PROJECT_ID,
            vr_conf.TARGET_LOCATION,
            vr_conf.TARGET_NAME_ID,
            vr_conf.TARGET_TITLE,
            link_role=vr_conf.LINK_ROLE,
            derived_fields=None,
        )
        
    def _changeDocToolName(self, valid_report):        
        # Retrieve all items from the validation report
        items = valid_report.getWorkitems()
        print(f"Scanning {len(items)} items to debug...\n")
        
        self._ChangeDocStatus(items)
        self._ChangeItems(items)
        valid_report.save()
    
    def _ChangeDocStatus(self, items):
        # Iterate through items and discover docStatus item
        docStatus = None
        for item in items:
            print(item)
            if(item.type and item.type.id == 'docstatus_sds'):
                docStatus = item
                print(item)
        
        # Check if item exists
        if(docStatus is None):
            print("Polarion item of type Doc Status is missing!! Please fix manually!!")
            return
        
        # Check for correct item attributes
        if not hasattr(docStatus, 'title') or docStatus.title is None:
            raise("Polarion item of type Doc Status has no title!! Please fix manually!!")
            
        docStatus_text = docStatus.title
        new_text = docStatus_text.replace(vr_conf.PLACEHOLDER_DOCSTATUS, vr_conf.TOOL_NAME)
        print(f"DocStatus title:{new_text}")
        docStatus.title = new_text
        docStatus.save()
    
    def _ChangeItems(self, items):
        self._ModifyItems(items, vr_conf.PLACEHOLDER, vr_conf.TOOL_NAME)
        

