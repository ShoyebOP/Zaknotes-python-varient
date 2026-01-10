import json
import os
from typing import Any, Dict, Optional

class ConfigManager:
    DEFAULT_CONFIG = {
        "transcription_model": "gemini-2.5-flash",
        "note_generation_model": "gemini-3-pro-preview"
    }

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_file):
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                config = self.DEFAULT_CONFIG.copy()
                config.update(loaded_config)
                return config
        except (json.JSONDecodeError, IOError):
            return self.DEFAULT_CONFIG.copy()

    def save(self) -> None:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value
