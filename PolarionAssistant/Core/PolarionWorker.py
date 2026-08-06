from abc import ABC
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

        