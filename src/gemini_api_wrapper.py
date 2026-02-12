import time
import httpx
import logging
from google import genai
from google.genai import types, errors

logger = logging.getLogger(__name__)

class GeminiAPIWrapper:
    MODELS = {
        "transcription": "gemini-2.5-flash",
        "note": "gemini-3-flash-preview"
    }

    def __init__(self, config=None):
        from src.config_manager import ConfigManager
        self.config = config or ConfigManager()
        
        self.api_timeout = self.config.get("api_timeout", 300)
        self.api_max_retries = self.config.get("api_max_retries", 3)
        self.api_retry_delay = self.config.get("api_retry_delay", 10)

    def _get_client(self, model_name):
        # Placeholder for new Gemini CLI Auth client
        # For now, this will fail if called, which is expected during this transition phase
        raise NotImplementedError("New Gemini CLI Auth client not yet implemented")

    def generate_content(self, prompt, model_type="note", system_instruction=None):
        model_name = self.MODELS.get(model_type, self.MODELS["note"])
        
        while True:
            # This will be updated in Phase 5
            client, auth_data = self._get_client(model_name)
            
            # Retry loop for timeouts
            for attempt in range(self.api_max_retries + 1):
                logger.info(f"Gemini API Request - Type: {model_type}, Model: {model_name} (Attempt: {attempt + 1})")
                if system_instruction:
                    logger.info(f"System Instruction: {str(system_instruction)}")
                logger.info(f"Prompt: {str(prompt)}")
                
                start_time = time.time()
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        ) if system_instruction else None
                    )
                    duration = time.time() - start_time
                    text_out = response.text or ""
                    logger.info(f"Gemini API Response - Success - Duration: {duration:.2f}s")
                    logger.info(f"Response: {text_out}")
                    return text_out
                except httpx.TimeoutException as e:
                    duration = time.time() - start_time
                    logger.warning(f"Gemini API Timeout - Duration: {duration:.2f}s - Error: {str(e)}")
                    if attempt < self.api_max_retries:
                        logger.info(f"Retrying in {self.api_retry_delay}s... ({attempt + 1}/{self.api_max_retries})")
                        time.sleep(self.api_retry_delay)
                        continue
                    else:
                        logger.error(f"Max retries reached for current account.")
                        break # Break retry loop, while loop will get new client/account
                except errors.ClientError as e:
                    duration = time.time() - start_time
                    logger.error(f"Gemini API Response - ClientError - Duration: {duration:.2f}s - Code: {e.code}")
                    if e.code == 429:
                        # Will be handled by account cycling in Phase 3/5
                        break
                    if e.code == 503:
                        logger.warning("Model overloaded (503). Waiting 10 minutes before retry...")
                        time.sleep(600)
                        continue
                    raise
                except httpx.HTTPStatusError as e:
                    duration = time.time() - start_time
                    logger.error(f"Gemini API Response - HTTPStatusError - Duration: {duration:.2f}s - Status: {e.response.status_code}")
                    if e.response.status_code == 429:
                        break
                    if e.response.status_code == 503:
                        logger.warning("Model overloaded (503). Waiting 10 minutes before retry...")
                        time.sleep(600)
                        continue
                    raise
                except Exception as e:
                    duration = time.time() - start_time
                    logger.error(f"Gemini API Response - Exception - Duration: {duration:.2f}s - Error: {str(e)}")
                    
                    if "timeout" in str(e).lower():
                        if attempt < self.api_max_retries:
                            logger.info(f"Timeout detected in Exception. Retrying in {self.api_retry_delay}s... ({attempt + 1}/{self.api_max_retries})")
                            time.sleep(self.api_retry_delay)
                            continue
                        else:
                            break
                    
                    code = getattr(e, 'code', getattr(getattr(e, 'response', None), 'status_code', None))
                    if code == 503:
                        logger.warning("Model overloaded (503). Waiting 10 minutes before retry...")
                        time.sleep(600)
                        continue
                    raise

    def generate_content_with_file(self, file_path, prompt, model_type="transcription", system_instruction=None):
        model_name = self.MODELS.get(model_type, self.MODELS["transcription"])
        
        while True:
            client, auth_data = self._get_client(model_name)
            
            for attempt in range(self.api_max_retries + 1):
                logger.info(f"Gemini API Request (with file) - Type: {model_type}, Model: {model_name}, File: {file_path} (Attempt: {attempt + 1})")
                if system_instruction:
                    logger.info(f"System Instruction: {str(system_instruction)}")
                logger.info(f"Prompt: {str(prompt)}")

                start_time = time.time()
                try:
                    logger.info(f"Uploading file: {file_path}")
                    file_obj = client.files.upload(file=file_path)
                    self._wait_for_file_active(client, file_obj)
                    
                    logger.info(f"Generating content for file: {file_obj.name}")
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[file_obj, prompt],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        ) if system_instruction else None
                    )
                    duration = time.time() - start_time
                    text_out = response.text or ""
                    logger.info(f"Gemini API Response - Success - Duration: {duration:.2f}s")
                    logger.info(f"Response: {text_out}")
                    return text_out
                except httpx.TimeoutException as e:
                    duration = time.time() - start_time
                    logger.warning(f"Gemini API Timeout (file) - Duration: {duration:.2f}s - Error: {str(e)}")
                    if attempt < self.api_max_retries:
                        logger.info(f"Retrying in {self.api_retry_delay}s... ({attempt + 1}/{self.api_max_retries})")
                        time.sleep(self.api_retry_delay)
                        continue
                    else:
                        break
                except errors.ClientError as e:
                    duration = time.time() - start_time
                    logger.error(f"Gemini API Response - ClientError - Duration: {duration:.2f}s - Code: {e.code}")
                    if e.code == 429:
                        break
                    if e.code == 503:
                        logger.warning("Model overloaded (503). Waiting 10 minutes before retry...")
                        time.sleep(600)
                        continue
                    raise
                except httpx.HTTPStatusError as e:
                    duration = time.time() - start_time
                    logger.error(f"Gemini API Response - HTTPStatusError - Duration: {duration:.2f}s - Status: {e.response.status_code}")
                    if e.response.status_code == 429:
                        break
                    if e.response.status_code == 503:
                        logger.warning("Model overloaded (503). Waiting 10 minutes before retry...")
                        time.sleep(600)
                        continue
                    raise
                except Exception as e:
                    duration = time.time() - start_time
                    logger.error(f"Gemini API Response - Exception - Duration: {duration:.2f}s - Error: {str(e)}")
                    
                    if "timeout" in str(e).lower():
                        if attempt < self.api_max_retries:
                            logger.info(f"Timeout detected in Exception. Retrying in {self.api_retry_delay}s... ({attempt + 1}/{self.api_max_retries})")
                            time.sleep(self.api_retry_delay)
                            continue
                        else:
                            break
                            
                    code = getattr(e, 'code', getattr(getattr(e, 'response', None), 'status_code', None))
                    if code == 503:
                        logger.warning("Model overloaded (503). Waiting 10 minutes before retry...")
                        time.sleep(600)
                        continue
                    raise

    def _wait_for_file_active(self, client, file_obj):
        """Waits for the uploaded file to be in ACTIVE state."""
        while file_obj.state == "PROCESSING":
            time.sleep(2)
            file_obj = client.files.get(name=file_obj.name)
        
        if file_obj.state != "ACTIVE":
            raise Exception(f"File {file_obj.name} failed to process with state {file_obj.state}")

    def _wait_for_file_active(self, client, file_obj):
        """Waits for the uploaded file to be in ACTIVE state."""
        while file_obj.state == "PROCESSING":
            time.sleep(2)
            file_obj = client.files.get(name=file_obj.name)
        
        if file_obj.state != "ACTIVE":
            raise Exception(f"File {file_obj.name} failed to process with state {file_obj.state}")
