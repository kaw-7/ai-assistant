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
                            if hasattr(req.description, 'content') and req.description.content is not None:
                                self._ModifyATestCase(linked_item, req.description.content)
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
            desc_text = self._CreateDescription(requirement_desc)
            test_case.setDescription(desc_text)
            
    def _CreateDescription(self, test_description):
        test_action = self._CreateTestAction(test_description)
        test_action_lower = test_action[0].lower()+test_action[1:]
        TEST_STR = f'''<span style="font-weight: bold;font-size: 10pt;line-height: 1.5;">Check if {test_action_lower}</span><br/>
<br/>
<span style="font-size: 10pt;line-height: 1.5;">Phase: Operational qualification </span><br/>\n
<table id="polarion_wiki macro name=table" style="width: 712px;margin-left: auto;margin-right: auto;border: 1px solid #CCCCCC;empty-cells: show;border-collapse: collapse;">
  <tbody>
    <tr>
      <th style="font-weight: bold;background-color: #F0F0F0;text-align: left;vertical-align: top;width: 51px;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">Step</th>
      <th style="font-weight: bold;background-color: #F0F0F0;text-align: left;vertical-align: top;width: 295px;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">Input / Action</th>
      <th style="font-weight: bold;background-color: #F0F0F0;text-align: left;vertical-align: top;width: 332px;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">Expected Result</th>
    </tr>
    <tr>
      <td style="text-align: left;vertical-align: top;width: 51px;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">1</td>
      <td style="text-align: left;vertical-align: top;width: 295px;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">{test_description}</td>
      <td style="text-align: left;vertical-align: top;width: 332px;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">{test_action}</td>
    </tr>
  </tbody>
</table>\n'''
         

        return TEST_STR
    
    def _CreateTestAction(self, test_description):
        p01 = test_description.find("should")
        p02 = test_description.find("could")
        p0 = min(p01, p02)
        if(p0 == -1):
            p0 = max(p01, p02)

            if(p0 == -1):
                return test_description
        
        p1 = test_description.find(' ', p0)
        p2 = test_description.find(' ', p1+1)
        result = test_description[:p2] + 's' + test_description[p2:]
        word = ' should'
        if(p02 == p0):
            word = ' could'
        result = result.replace(word, "", 1)  # only first "one"
        
        return result