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

    def __init__(self, key_manager=None, config=None):
        from src.config_manager import ConfigManager
        self.key_manager = key_manager or APIKeyManager()
        self.config = config or ConfigManager()
        
        self.api_timeout = self.config.get("api_timeout", 300)
        self.api_max_retries = self.config.get("api_max_retries", 3)
        self.api_retry_delay = self.config.get("api_retry_delay", 10)

    def _get_client(self, model_name):
        api_key = self.key_manager.get_available_key(model_name)
        if not api_key:
            raise Exception(f"No API keys available with remaining quota for model {model_name}")
        
        # Configure client with timeout
        return genai.Client(
            api_key=api_key,
            http_options={'timeout': self.api_timeout}
        ), api_key

    def generate_content(self, prompt, model_type="note", system_instruction=None):
        model_name = self.MODELS.get(model_type, self.MODELS["note"])
        
        while True:
            client, api_key = self._get_client(model_name)
            masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "****"
            
            # Retry loop for timeouts on the SAME key
            for attempt in range(self.api_max_retries + 1):
                # Increment quota proactively before each unique request (not per retry of the same request)
                # But here, if we retry, we might want to count it as another attempt if it reached the server.
                # However, the spec says "retry using the same API key (to avoid burning another key's quota for the same task prematurely)".
                # Let's record usage once per while loop iteration (per key selection).
                if attempt == 0:
                    self.key_manager.record_usage(api_key, model_name)
                
                logger.info(f"Gemini API Request - Type: {model_type}, Model: {model_name}, Key: {masked_key} (Attempt: {attempt + 1})")
                if system_instruction:
                    logger.info(f"System Instruction (truncated): {str(system_instruction)[:100]}...")
                logger.info(f"Prompt (truncated): {str(prompt)[:100]}...")
                
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
                    logger.info(f"Response (truncated): {text_out[:100]}...")
                    return text_out
                except httpx.TimeoutException as e:
                    duration = time.time() - start_time
                    logger.warning(f"Gemini API Timeout - Duration: {duration:.2f}s - Error: {str(e)}")
                    if attempt < self.api_max_retries:
                        logger.info(f"Retrying in {self.api_retry_delay}s... ({attempt + 1}/{self.api_max_retries})")
                        time.sleep(self.api_retry_delay)
                        continue
                    else:
                        logger.error(f"Max retries reached for key {masked_key}. Marking as exhausted.")
                        self.key_manager.mark_exhausted(api_key, model_name)
                        break # Break retry loop, while loop will get new client/key
                except errors.ClientError as e:
                    duration = time.time() - start_time
                    logger.error(f"Gemini API Response - ClientError - Duration: {duration:.2f}s - Code: {e.code}")
                    if e.code == 429:
                        self.key_manager.mark_exhausted(api_key, model_name)
                        break # Break retry loop, while loop will get new client/key
                    if e.code == 503:
                        logger.warning("Model overloaded (503). Waiting 10 minutes before retry...")
                        time.sleep(600)
                        continue # Retry on SAME key for 503 as per existing logic
                    raise
                except httpx.HTTPStatusError as e:
                    duration = time.time() - start_time
                    logger.error(f"Gemini API Response - HTTPStatusError - Duration: {duration:.2f}s - Status: {e.response.status_code}")
                    if e.response.status_code == 429:
                        self.key_manager.mark_exhausted(api_key, model_name)
                        break # Break retry loop, while loop will get new client/key
                    if e.response.status_code == 503:
                        logger.warning("Model overloaded (503). Waiting 10 minutes before retry...")
                        time.sleep(600)
                        continue # Retry on SAME key for 503
                    raise
                except Exception as e:
                    duration = time.time() - start_time
                    logger.error(f"Gemini API Response - Exception - Duration: {duration:.2f}s - Error: {str(e)}")
                    
                    # Check for timeout wrapped in Exception
                    if "timeout" in str(e).lower():
                        if attempt < self.api_max_retries:
                            logger.info(f"Timeout detected in Exception. Retrying in {self.api_retry_delay}s... ({attempt + 1}/{self.api_max_retries})")
                            time.sleep(self.api_retry_delay)
                            continue
                        else:
                            self.key_manager.mark_exhausted(api_key, model_name)
                            break
                    
                    # Check for 503 in general exceptions
                    code = getattr(e, 'code', getattr(getattr(e, 'response', None), 'status_code', None))
                    if code == 503:
                        logger.warning("Model overloaded (503). Waiting 10 minutes before retry...")
                        time.sleep(600)
                        continue
                    raise

    def generate_content_with_file(self, file_path, prompt, model_type="transcription", system_instruction=None):
        model_name = self.MODELS.get(model_type, self.MODELS["transcription"])
        
        while True:
            client, api_key = self._get_client(model_name)
            masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "****"
            
            # Retry loop for timeouts on the SAME key
            for attempt in range(self.api_max_retries + 1):
                if attempt == 0:
                    self.key_manager.record_usage(api_key, model_name)
                
                logger.info(f"Gemini API Request (with file) - Type: {model_type}, Model: {model_name}, Key: {masked_key}, File: {file_path} (Attempt: {attempt + 1})")
                if system_instruction:
                    logger.info(f"System Instruction (truncated): {str(system_instruction)[:100]}...")
                logger.info(f"Prompt (truncated): {str(prompt)[:100]}...")

                start_time = time.time()
                try:
                    # Upload file
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
                    logger.info(f"Response (truncated): {text_out[:100]}...")
                    return text_out
                except httpx.TimeoutException as e:
                    duration = time.time() - start_time
                    logger.warning(f"Gemini API Timeout (file) - Duration: {duration:.2f}s - Error: {str(e)}")
                    if attempt < self.api_max_retries:
                        logger.info(f"Retrying in {self.api_retry_delay}s... ({attempt + 1}/{self.api_max_retries})")
                        time.sleep(self.api_retry_delay)
                        continue
                    else:
                        logger.error(f"Max retries reached for key {masked_key}. Marking as exhausted.")
                        self.key_manager.mark_exhausted(api_key, model_name)
                        break
                except errors.ClientError as e:
                    duration = time.time() - start_time
                    logger.error(f"Gemini API Response - ClientError - Duration: {duration:.2f}s - Code: {e.code}")
                    if e.code == 429:
                        self.key_manager.mark_exhausted(api_key, model_name)
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
                        self.key_manager.mark_exhausted(api_key, model_name)
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
                            self.key_manager.mark_exhausted(api_key, model_name)
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
