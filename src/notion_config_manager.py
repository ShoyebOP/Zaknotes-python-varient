import os
import json

class NotionConfigManager:
    DEFAULT_KEYS_FILE = "keys/notion_keys.json"

    def __init__(self, keys_file=None):
        self.keys_file = keys_file or self.DEFAULT_KEYS_FILE
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            "NOTION_SECRET": "",
            "DATABASE_ID": ""
        }

    def _save_data(self):
        parent_dir = os.path.dirname(self.keys_file)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        try:
            with open(self.keys_file, 'w') as f:
                json.dump(self.data, f, indent=4)
        except IOError as e:
            print(f"Error saving notion keys: {e}")

    def get_credentials(self):
        return self.data.get("NOTION_SECRET", ""), self.data.get("DATABASE_ID", "")

    def set_credentials(self, secret, db_id):
        self.data["NOTION_SECRET"] = secret
        self.data["DATABASE_ID"] = db_id
        self._save_data()
