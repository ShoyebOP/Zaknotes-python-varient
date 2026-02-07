import time
import httpx
import logging
from google import genai
from google.genai import types, errors
from src.api_key_manager import APIKeyManager

logger = logging.getLogger(__name__)

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
            # Increment quota proactively before the request
            self.key_manager.record_usage(api_key, model_name)
            
            masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "****"
            logger.debug(f"Gemini API Request - Type: {model_type}, Model: {model_name}, Key: {masked_key}")
            logger.debug(f"Prompt (truncated): {str(prompt)[:100]}...")
            
            start_time = time.time()
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                duration = time.time() - start_time
                text_out = response.text or ""
                logger.debug(f"Gemini API Response - Success - Duration: {duration:.2f}s")
                logger.debug(f"Response (truncated): {text_out[:100]}...")
                return text_out
            except errors.ClientError as e:
                duration = time.time() - start_time
                logger.debug(f"Gemini API Response - ClientError - Duration: {duration:.2f}s - Code: {e.code}")
                if e.code == 429:
                    self.key_manager.mark_exhausted(api_key, model_name)
                    continue
                raise
            except httpx.HTTPStatusError as e:
                duration = time.time() - start_time
                logger.debug(f"Gemini API Response - HTTPStatusError - Duration: {duration:.2f}s - Status: {e.response.status_code}")
                if e.response.status_code == 429:
                    self.key_manager.mark_exhausted(api_key, model_name)
                    continue
                raise
            except Exception as e:
                duration = time.time() - start_time
                logger.debug(f"Gemini API Response - Exception - Duration: {duration:.2f}s - Error: {str(e)}")
                raise

    def generate_content_with_file(self, file_path, prompt, model_type="transcription"):
        model_name = self.MODELS.get(model_type, self.MODELS["transcription"])
        
        while True:
            client, api_key = self._get_client(model_name)
            # Increment quota proactively before the request (counting upload + generate as one unit for now)
            self.key_manager.record_usage(api_key, model_name)
            
            masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "****"
            logger.debug(f"Gemini API Request (with file) - Type: {model_type}, Model: {model_name}, Key: {masked_key}, File: {file_path}")
            logger.debug(f"Prompt (truncated): {str(prompt)[:100]}...")

            start_time = time.time()
            try:
                # Upload file
                logger.debug(f"Uploading file: {file_path}")
                file_obj = client.files.upload(file=file_path)
                self._wait_for_file_active(client, file_obj)
                
                logger.debug(f"Generating content for file: {file_obj.name}")
                response = client.models.generate_content(
                    model=model_name,
                    contents=[file_obj, prompt]
                )
                duration = time.time() - start_time
                text_out = response.text or ""
                logger.debug(f"Gemini API Response - Success - Duration: {duration:.2f}s")
                logger.debug(f"Response (truncated): {text_out[:100]}...")
                return text_out
            except errors.ClientError as e:
                duration = time.time() - start_time
                logger.debug(f"Gemini API Response - ClientError - Duration: {duration:.2f}s - Code: {e.code}")
                if e.code == 429:
                    self.key_manager.mark_exhausted(api_key, model_name)
                    continue
                raise
            except httpx.HTTPStatusError as e:
                duration = time.time() - start_time
                logger.debug(f"Gemini API Response - HTTPStatusError - Duration: {duration:.2f}s - Status: {e.response.status_code}")
                if e.response.status_code == 429:
                    self.key_manager.mark_exhausted(api_key, model_name)
                    continue
                raise
            except Exception as e:
                duration = time.time() - start_time
                logger.debug(f"Gemini API Response - Exception - Duration: {duration:.2f}s - Error: {str(e)}")
                raise

    def _wait_for_file_active(self, client, file_obj):
        """Waits for the uploaded file to be in ACTIVE state."""
        while file_obj.state == "PROCESSING":
            time.sleep(2)
            file_obj = client.files.get(name=file_obj.name)
        
        if file_obj.state != "ACTIVE":
            raise Exception(f"File {file_obj.name} failed to process with state {file_obj.state}")
