import TestSpec.testspec_config as ts_conf
from Core.PolarionWorker import PolarionWorker
from typing_extensions import override
from Core.ItemUtil import ItemUtil
import traceback
import sys

class TestSpecBuilder(PolarionWorker):
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
            self._MoveDummyTestCases(new_doc)
            self._changeDocToolName(new_doc)
        except Exception:
            full_error = traceback.format_exc()
            print(f"❌ Error during polarion manipulation: {full_error}")
            sys.exit(1)
        
    @override
    def _createDoc(self):
        # Reuse the template
        return self.getTemplate(ts_conf.PROJECT_ID, ts_conf.TEST_SPEC_TEMPLATE).reuse(
            ts_conf.PROJECT_ID,
            ts_conf.TARGET_LOCATION,
            ts_conf.TARGET_NAME_ID,
            ts_conf.TARGET_TITLE,
            link_role=ts_conf.LINK_ROLE,
            derived_fields=None,
        )
        
    def _changeDocToolName(self, test_spec):
        # 1. Connect to Polarion and get your project
        # project = self._client.getProject(ts_conf.PROJECT_ID)
        
        # 2. Get the test spec and scan for linked sub items
        # test_spec = project.getDocument(ts_conf.TEST_DOCU)
        
        # 3. Retrieve all items from the Test Spec
        items = test_spec.getWorkitems()
        print(f"Scanning {len(items)} items to debug...\n")
        
        self._ChangeDocStatus(items)
        self._ChangeItems(items)
        test_spec.save()
    
    def _ChangeDocStatus(self, items):
        # Iterate through items and discover docStatus item
        docStatus = None
        for item in items:
            if(item.type and item.type.id == 'docstatus_vertestspec'):
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
        new_text = docStatus_text.replace(ts_conf.PLACEHOLDER_DOCSTATUS, ts_conf.TOOL_NAME)
        print(f"DocStatus title:{new_text}")
        docStatus.title = new_text
        docStatus.save()
    
    def _ChangeItems(self, items):
        self._ModifyItems(items, ts_conf.PLACEHOLDER, ts_conf.TOOL_NAME)
        
    def _MoveDummyTestCases(self, new_doc):
        '''Move dummy test cases to a subchapter of DOC_INPUT_HEADING (Operational Qualification)'''
        heading_item = ItemUtil.find_heading_item_by_name(new_doc, ts_conf.DOC_INPUT_HEADING)
        if heading_item is None:
            print(f"❌ Could not find heading: {ts_conf.DOC_INPUT_HEADING}! Cleaning of that heading is skipped!")
        else:
            # Create a new heading in the same document to hold discarded items
            trash_heading = new_doc.addHeading('Unused Items', parent_workitem=heading_item)
            self._moveChildren(new_doc, heading_item, trash_heading)
            new_doc.save()
