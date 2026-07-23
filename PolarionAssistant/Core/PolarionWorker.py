from abc import ABC
from Core.PolarionConnector import PolarionConnector
import sys

class PolarionWorker(ABC):
    def __init__(self):
        self._connector = PolarionConnector()
        
        self._client = self._connector.connect()
        if self._client is None:
            print("❌ Could not connect to polarion server!")
            sys.exit(1)

        