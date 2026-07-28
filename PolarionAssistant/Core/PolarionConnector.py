import traceback
import os
from dotenv import load_dotenv
from polarion import polarion

class PolarionConnector:
    def __init__(self):
        """Initialize with config values - no connection yet."""
        self.client = None
        self.polarion_username = None
    
    def connect(self):
        if self.is_connected():
            return self.client

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
    
    def is_connected(self):
        """Check if client is ready."""
        return self.client is not None
    
    def disconnect(self):
        """Clean shutdown."""
        self.client = None
        print("🔌 Disconnected from Polarion")


