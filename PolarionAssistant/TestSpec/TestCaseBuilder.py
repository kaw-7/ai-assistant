import TestSpec.testspec_config as ts_conf
from PolarionFactory import PolarionFactory
 
class TestCaseBuilder(PolarionFactory):
    
    def __init__(self):
        super().__init__()
        
    def MoveTestCases(self):
    
        # 1. Connect to Polarion and get your project
        
        project = self._client.getProject(ts_conf.PROJECT_ID)
        
        # 2. Get the source and target documents
        # Format usually follows: 'space_name/document_name'
        val_plan = project.getDocument(ts_conf.PLAN_DOCU)
        test_spec = project.getDocument(ts_conf.TEST_DOCU)
        
        # Get the root element of the Test Spec document to use as the parent node
        test_spec_root = test_spec.getTopLevelWorkitem()
        
        # 3. Retrieve all items (requirements) from the Validation Plan
        requirements = val_plan.getWorkitems()
        print(f"Scanning {len(requirements)} requirements for floating test cases...")
        
        # 4. Iterate through requirements and discover linked test cases
        for req in requirements:
            # getLinkedItemWithRoles() returns a list of tuples: [('link_role_id', Workitem), ...]
            # This automatically includes both incoming and outgoing links.
            links = req.getLinkedItemWithRoles()
            
            for role, linked_item in links:
                # Check if the linked item is a Test Case (verify the exact type ID in your system)
                if linked_item.type.id == 'testcase':
                    print(f"Found floating Test Case {linked_item.id} linked to {req.id} via '{role}'")
                    
                    # 5. "Plug" the test case into the Test Specification document
                    try:
                        # Syntax based on the formal class reference: moveToDocument(document, parent)
                        linked_item.moveToDocument(test_spec, test_spec_root)
                        print(f"Successfully moved {linked_item.id} into the Test Specification.")
                    except Exception as e:
                        print(f"Failed to move {linked_item.id}: {e}")
        
        # 6. Save the Test Specification document changes
        test_spec.save()
        print("Document sync complete!")