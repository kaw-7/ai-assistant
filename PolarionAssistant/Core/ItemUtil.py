import traceback
from polarion import polarion
from dataclasses import dataclass

class ItemUtil():
    @staticmethod
    def find_heading_item_by_name(document, heading_name):
        """Simple iterative search - NO complex API calls"""
    
        try:
            # Get ALL work items from document (returns list)
            all_workitems = document.getWorkitems()  # Direct property
        
            for wi in all_workitems:
                if wi.title == heading_name:
                    # print(f"✅ Found '{heading_name}' ID: {wi.id}")
                    return wi
        
            print(f"❌ '{heading_name}' heading not found")
            return None
        
        except Exception as e:
            full_error = traceback.format_exc()
            print(f"❌ Error searching: {full_error}")
            return None


