import traceback
import os
from dotenv import load_dotenv
from polarion import polarion

import config as PConf

class PolarionConnector:
    def __init__(self):
        """Initialize with config values - no connection yet."""
        self.client = None
        self.project = None
        self.doc = None
        self.polarion_username = None
    
    def connect(self):
        """Equivalent to polarion_connect()"""
        print("🔍 Connecting to Polarion server...")
        load_dotenv(dotenv_path=".polarion.env")
        # Now fetch the variables
        url = os.getenv("POLARION_URL")
        username = os.getenv("POLARION_USER")
        password = os.getenv("POLARION_PASS")
        self.polarion_username = username

        try:
            print(f"Connecting to {url} as {username}...")
            self.client = polarion.Polarion(url, username, password)
            print("✅ Connection successful!")
            return self.client
        except Exception:
            full_error = traceback.format_exc()
            print(f"❌ Connection failed: {full_error}")
            return None
    
    def get_current_user_info(self):
        """Fetches the full name and email of the currently connected user."""
        full_name = None
        email = None
        if self.client is None:
            print("❌ Cannot fetch user: Not connected to Polarion yet!")
            return full_name, email
            
        try:
            # 1. Grab the Project service from the client
            project_service = self.client.getService('Project')
            
            # 2. Ask the service for the user using your login ID
            user = project_service.getUser(self.polarion_username)
            
            # 3. Extract the attributes
            # (Using getattr is a safe way to grab them just in case the 
            # fields are blank in the Polarion database)
            full_name = getattr(user, 'name', 'No Name Set')
            email = getattr(user, 'email', 'No Email Set')
            
            # print(f"👤 Logged in as: {full_name} ({email})")
            
            # 3. Return them as a tuple so you can use them in your script
            return full_name, email
            
        except Exception:
            print(f"❌ Failed to fetch user info: {traceback.format_exc()}")
            return full_name, email

    def get_document(self, doc_name: str = None):
        """Equivalent to get_polarion_doc() - loads project + document"""
        if not self.client:
            print("❌ Client not connected. Call connect() first.")
            return None
        
        try:
            # Get project
            self.project = self.client.getProject(PConf.PROJECT_ID)
            
            # Build document path
            doc_name = doc_name or PConf.DOC_NAME
            doc_path = f"{doc_name}"
            
            # Get document
            self.doc = self.project.getDocument(doc_path)
            if self.doc is None:
                print(f"❌ Document '{doc_path}' not found")
                return None
            print(f"✅ Loaded '{self.doc.title}'")
            return self.doc
            
        except Exception:
            full_error = traceback.format_exc()
            print(f"❌ Document load failed: {full_error}")
            return None
    
    def is_connected(self):
        """Check if client and document are ready."""
        return self.client is not None and self.doc is not None
    
    def disconnect(self):
        """Clean shutdown."""
        self.client = None
        self.project = None
        self.doc = None
        print("🔌 Disconnected from Polarion")


