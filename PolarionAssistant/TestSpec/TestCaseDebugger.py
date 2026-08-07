import TestSpec.testspec_config as ts_conf
from Core.PolarionWorker import PolarionWorker

class TestCaseDebugger(PolarionWorker):
    
    def __init__(self):
        super().__init__()
        
    def PrintTestCaseDetails(self):
        # 1. Connect to Polarion and get your project
        project = self._client.getProject(ts_conf.PROJECT_ID)
        
        # 2. Get the validation plan to scan for the linked test cases
        val_plan = project.getDocument(ts_conf.PLAN_DOCU)
        
        # 3. Retrieve all items (requirements) from the Validation Plan
        requirements = val_plan.getWorkitems()
        print(f"Scanning {len(requirements)} requirements for test cases to debug...\n")
        
        # 4. Iterate through requirements and discover linked test cases
        for req in requirements:
            links = req.getLinkedItemWithRoles()
            
            for role, linked_item in links:
                if linked_item.type.id == 'testcase':
                    
                    # Debug Box Header
                    print("=" * 80)
                    print(f"📋 DEBUG DUMP FOR TEST CASE: {linked_item.id}")
                    print(f"   Linked to Requirement: {req.id} via role '{role}'")
                    print("=" * 80)
                    
                    # --- 1. PRINT TITLE ---
                    print(f"\n🔹 TITLE:\n   {linked_item.title}")
                    
                    # --- 2. PRINT DESCRIPTION ---
                    print(f"\n🔹 DESCRIPTION:")
                    if hasattr(req, 'description') and req.description is not None:
                        if hasattr(req.description, 'content') and req.description.content is not None:
                            req_desc_text = req.description.content
                            print(f"   {req_desc_text}")
                            self._ReadATestCase(linked_item, req_desc_text)
                            
                        
                    print("\n" + "=" * 80 + "\n")
                    
    def _ReadATestCase(self, test_case, requirement_desc):
        
        if hasattr(test_case, 'description') and test_case.description is not None:
            # Extract the raw text wrapper object content (will include raw HTML strings)
            desc_text = test_case.getDescription()
            with open("current.txt", mode="a+", encoding='utf-8') as cur_f:
                cur_f.write(desc_text)
            new_desc = self._CreateDescription(requirement_desc)
            with open("new.txt", mode="a+", encoding='utf-8') as new_f:
                new_f.write(new_desc)
            
            asdf = 5
            # test_case.setDescription(desc_text)
            
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
</table>'''
         

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