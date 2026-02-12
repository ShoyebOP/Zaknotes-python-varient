import json
import os
from typing import Any, Dict, Optional

class ConfigManager:
    DEFAULT_CONFIG = {
        "transcription_model": "gemini-2.5-flash",
        "note_generation_model": "gemini-3-pro-preview",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "api_timeout": 300,
        "api_max_retries": 3,
        "api_retry_delay": 10,
        "notion_integration_enabled": False
    }

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        # Auto-profile if performance_profile is missing
        if "performance_profile" not in self.config:
            cores, ram_gb = self.detect_system_resources()
            profile = self.map_resources_to_profile(cores, ram_gb)
            self.set("performance_profile", profile)
            self.save()

    def detect_system_resources(self):
        """Detects CPU cores and total RAM in GB."""
        cores = os.cpu_count() or 1
        try:
            # For Linux
            mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
            ram_gb = mem_bytes / (1024**3)
        except (AttributeError, ValueError):
            # Fallback for non-Linux or failures
            ram_gb = 4.0 # Default assumption
        return cores, ram_gb

    def map_resources_to_profile(self, cores: int, ram_gb: float) -> str:
        """Maps detected resources to a performance profile."""
        if cores >= 8 or ram_gb >= 12:
            return "high"
        if cores >= 4 or ram_gb >= 6:
            return "balanced"
        return "low"

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
