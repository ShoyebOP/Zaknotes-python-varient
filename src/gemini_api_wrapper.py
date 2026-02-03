import time
import httpx
from google import genai
from google.genai import types, errors
from src.api_key_manager import APIKeyManager

class GeminiAPIWrapper:
    MODELS = {
        "transcription": "gemini-2.5-flash",
        "note": "gemini-3-flash-preview"
    }

    def __init__(self, key_manager=None):
        self.key_manager = key_manager or APIKeyManager()

    def _get_client(self, model_name):
        api_key = self.key_manager.get_available_key(model_name)
        if not api_key:
            raise Exception(f"No API keys available with remaining quota for model {model_name}")
        
        return genai.Client(api_key=api_key), api_key

    def generate_content(self, prompt, model_type="note"):
        model_name = self.MODELS.get(model_type, self.MODELS["note"])
        
        while True:
            client, api_key = self._get_client(model_name)
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                self.key_manager.record_usage(api_key, model_name)
                return response.text
            except errors.ClientError as e:
                if e.code == 429:
                    self.key_manager.mark_exhausted(api_key, model_name)
                    continue
                raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    self.key_manager.mark_exhausted(api_key, model_name)
                    continue
                raise
            except Exception:
                raise

    def generate_content_with_file(self, file_path, prompt, model_type="transcription"):
        model_name = self.MODELS.get(model_type, self.MODELS["transcription"])
        
        while True:
            client, api_key = self._get_client(model_name)
            try:
                # Upload file
                file_obj = client.files.upload(file=file_path)
                self._wait_for_file_active(client, file_obj)
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=[file_obj, prompt]
                )
                self.key_manager.record_usage(api_key, model_name)
                return response.text
            except errors.ClientError as e:
                if e.code == 429:
                    self.key_manager.mark_exhausted(api_key, model_name)
                    continue
                raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    self.key_manager.mark_exhausted(api_key, model_name)
                    continue
                raise
            except Exception:
                raise

    def _wait_for_file_active(self, client, file_obj):
        """Waits for the uploaded file to be in ACTIVE state."""
        while file_obj.state == "PROCESSING":
            time.sleep(2)
            file_obj = client.files.get(name=file_obj.name)
        
        if file_obj.state != "ACTIVE":
            raise Exception(f"File {file_obj.name} failed to process with state {file_obj.state}")
