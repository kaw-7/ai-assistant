import TestSpec.testspec_config as ts_conf
from Core.PolarionWorker import PolarionWorker
from typing_extensions import override

class TestSpecDebugger(PolarionWorker):
    def __init__(self):
        super().__init__()
    
    @override
    def PrintDocDetails(self):
        # 1. Connect to Polarion and get your project
        project = self._client.getProject(ts_conf.PROJECT_ID)
        
        # 2. Get the test spec and scan for linked sub items
        test_spec = project.getDocument(ts_conf.TEST_DOCU)
        
        # 3. Retrieve all items from the Test Spec
        items = test_spec.getWorkitems()
        print(f"Scanning {len(items)} items to debug...\n")
        
        self._PrintDocStatus(items)
        self._PrintItems(items)
    
    def _PrintDocStatus(self, items):
        # Iterate through items and discover docStatus item
        docStatus = None
        for item in items:
            if(item.type and item.type.id == 'docstatus_vertestspec'):
                docStatus = item
                print(item)
        
        # Check for correct item attributes
        if not hasattr(item, 'title') or docStatus.description is None:
            raise("Polarion item of type Doc Status has no description!! Please fix manually!!")
        if not hasattr(docStatus.description, 'content'):
            raise("Polarion item of type Doc Status has no content!!! Please fix manually!!!")
            
        docStatus_text = docStatus.title
        new_text = docStatus_text.replace(ts_conf.PLACEHOLDER_DOCSTATUS, ts_conf.TOOL_NAME)
        print(f"DocStatus title:{new_text}")
        # docStatus.title = new_text
    
    def _PrintItems(self, items):
        # Check for correct test attributes
        for item in items:
            if not hasattr(item, 'description') or item.description is None:
                continue # skip
            print(item.description)
            if not hasattr(item.description, 'content') or item.description.content is None:
                continue # skip
                
            item_text = item.description.content
            new_text = item_text.replace(ts_conf.PLACEHOLDER, ts_conf.TOOL_NAME)
            print(f"Test content:{new_text}")
            # item.description.content = new_text
   
   