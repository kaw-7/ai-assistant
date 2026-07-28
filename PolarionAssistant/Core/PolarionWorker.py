from abc import ABC
from PolarionAssistant.Core.PolarionConnector import PolarionConnector
import sys
connector = PolarionConnector()

class PolarionWorker(ABC):
    def __init__(self):
        self._connector = connector
        
        self._client = self._connector.connect()
        if self._client is None:
            print("❌ Could not connect to polarion server!")
            sys.exit(1)

        