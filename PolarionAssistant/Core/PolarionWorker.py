from abc import ABC, abstractmethod
import sys
try:
    from PolarionAssistant.Core.PolarionConnector import PolarionConnector
except:
    from Core.PolarionConnector import PolarionConnector
    
connector = PolarionConnector()

class PolarionWorker(ABC):
    def __init__(self):
        self._connector = connector
        
        self._client = self._connector.connect()
        if self._client is None:
            print("❌ Could not connect to polarion server!")
            sys.exit(1)
    
    @abstractmethod
    def PrintDocDetails(self):
        pass
    
    def getTemplate(self, proj_id, template_path):
        # 1. Get your project
        project = self._client.getProject(proj_id)
        
        # 2. Get the template
        template = project.getDocument(template_path)
        
        return template
        
    def _ModifyItems(self, items, placeholder, substitute):
        # Check for correct test attributes
        for item in items:
            if not hasattr(item, 'description') or item.description is None:
                continue # skip
            if not hasattr(item.description, 'content') or item.description.content is None:
                continue # skip
                
            item_text = item.description.content
            new_text = item_text.replace(placeholder, substitute)
            print(f"Test content:{new_text}")
            item.description.content = new_text
            item.save()
            
    def _moveChildren(self, document, workitem, target_parent):
        """Move all descendants of `workitem` under `target_parent`, in the same document."""
        children = document.getChildren(workitem)
        for child in list(children):
            if child == target_parent:
                continue
            self._moveChildren(document, child, target_parent)
            print(f"Moving {child.id}|{child.title} under {target_parent.title}")
            child.moveToDocument(document, target_parent)
    