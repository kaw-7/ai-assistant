import TestSpec.testspec_config as ts_conf
from Core.PolarionWorker import PolarionWorker
from Core.ItemUtil import ItemUtil

class TestCaseBuilder(PolarionWorker):
    
    def __init__(self):
        super().__init__()
        
    def MoveTestCases(self):
    
        # 1. Connect to Polarion and get your project
        
        project = self._client.getProject(ts_conf.PROJECT_ID)
        
        # 2. Get the source and target documents
        # Format usually follows: 'space_name/document_name'
        val_plan = project.getDocument(ts_conf.PLAN_DOCU)
        test_spec = project.getDocument(ts_conf.TEST_DOCU)
        
        # Get the element of the Test Spec document to use as the parent node
        heading_item = ItemUtil.find_heading_item_by_name(test_spec, ts_conf.DOC_INPUT_HEADING)
        
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
                        if hasattr(req, 'description') and req.description is not None:
                            self._ModifyATestCase(linked_item, req.description)
                        # Syntax based on the formal class reference: moveToDocument(document, parent)
                        linked_item.moveToDocument(test_spec, heading_item)
                        print(f"Successfully moved {linked_item.id} into the Test Specification.")
                    except Exception as e:
                        print(f"Failed to move {linked_item.id}: {e}")
        
        # 6. Save the Test Specification document changes
        test_spec.save()
        print("Document sync complete!")
        
    def _ModifyATestCase(self, test_case, requirement_desc):
        
        
        if hasattr(test_case, 'description') and test_case.description is not None:
            # Extract the raw text wrapper object content (will include raw HTML strings)
            desc_text = test_case.getDescription()
            TABLE = "<table"
            pos = desc_text.find(TABLE)
            if pos == -1:
                return
            initial_str = self._CreateDescription(requirement_desc)
            desc_text = initial_str + desc_text[pos:]
            test_case.setDescription(desc_text)
            
    def _CreateDescription(self, test_description):
        TEST_STR = f'''<span style="font-weight: bold;font-size: 10pt;line-height: 1.5;">Check the possibility to {test_description}</span><br/>
            <br/>
            <span style="font-size: 10pt;line-height: 1.5;">Phase: Operational qualification </span><br/>\n
            <table id="polarion_wiki macro name=table" style="width: 712px;margin-left: auto;margin-right: auto;border: 1px solid #CCCCCC;empty-cells: show;border-collapse: collapse;">
              <tbody>
                <tr>
                  <th style="background-color: #F0F0F0;text-align: left;vertical-align: top;width: 51px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">Step</th>
                  <th style="background-color: #F0F0F0;text-align: left;vertical-align: top;width: 295px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">Input / Action</th>
                  <th style="background-color: #F0F0F0;text-align: left;vertical-align: top;width: 332px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">Expected Result</th>
                </tr>
                <tr>
                  <td style="width: 51px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">1</td>
                  <td style="width: 295px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">{test_description}</td>
                  <td style="width: 332px;height: 12px;border: 1px solid #CCCCCC;border-top: 1px solid #CCCCCC;border-bottom: 1px solid #CCCCCC;border-right: 1px solid #CCCCCC;border-left: 1px solid #CCCCCC;padding: 5px;">{test_description}</td>
                </tr>
              </tbody>
            </table>'''
         
        return TEST_STR