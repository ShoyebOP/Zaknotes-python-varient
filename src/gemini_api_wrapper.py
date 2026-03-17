import time
import httpx
import logging
import json
import os
import asyncio
from typing import Optional, List, Dict, Any
from src.gemini_auth_service import GeminiAuthService, GeminiCliAuthRecord
from src.usage_tracker import UsageTracker
from src.audio_processor import AudioProcessor

logger = logging.getLogger(__name__)

class BackoffManager:
    """Manages exponential backoff for API retries and delays."""
    def __init__(self, initial_delay: float = 10.0, max_delay: float = 60.0, factor: float = 2.0):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.factor = factor

    def get_delay(self, attempt: int) -> float:
        """Calculates the delay for a given attempt number."""
        delay = self.initial_delay * (self.factor ** attempt)
        return min(delay, self.max_delay)

    async def async_sleep(self, attempt: int):
        """Asynchronously sleeps for the delay calculated for the given attempt."""
        delay = self.get_delay(attempt)
        logger.debug(f"Async backoff sleep: {delay}s (Attempt {attempt})")
        await asyncio.sleep(delay)

    def sync_sleep(self, attempt: int):
        """Synchronously sleeps for the delay calculated for the given attempt."""
        delay = self.get_delay(attempt)
        logger.debug(f"Sync backoff sleep: {delay}s (Attempt {attempt})")
        time.sleep(delay)

class GeminiAPIWrapper:
    CODE_ASSIST_ENDPOINT = "https://cloudcode-pa.googleapis.com"
    GEMINI_CLI_HEADERS = {
        "User-Agent": "google-cloud-sdk vscode_cloudshelleditor/0.1",
        "X-Goog-Api-Client": "gl-node/22.17.0",
        "Client-Metadata": json.dumps({
            "ideType": "IDE_UNSPECIFIED",
            "platform": "PLATFORM_UNSPECIFIED",
            "pluginType": "GEMINI",
        }),
    }

    def __init__(self, config=None, auth_service=None, usage_tracker=None):
        from src.config_manager import ConfigManager
        self.config = config or ConfigManager()
        self.auth_service = auth_service or GeminiAuthService()
        self.usage_tracker = usage_tracker or UsageTracker()
        
        self.api_timeout = self.config.get("api_timeout", 300)
        self.api_max_retries = self.config.get("api_max_retries", 3)
        self.api_retry_delay = self.config.get("api_retry_delay", 10)
        
        self.backoff_manager = BackoffManager(
            initial_delay=float(self.api_retry_delay),
            max_delay=float(self.config.get("api_max_delay", 60.0))
        )
        
        self.error_file = "error.json"

    def _log_error(self, request_body: Any, response_data: Any):
        """Logs the full request and response to error.json with truncation for large data."""
        
        def truncate_recursive(data):
            if isinstance(data, dict):
                return {k: truncate_recursive(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [truncate_recursive(i) for i in data]
            elif isinstance(data, str) and len(data) > 200:
                return data[:100] + "... [TRUNCATED] ..." + data[-50:]
            return data

        truncated_request = truncate_recursive(request_body)
        
        error_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "request": truncated_request,
            "response": response_data
        }
        
        errors = []
        if os.path.exists(self.error_file):
            try:
                with open(self.error_file, 'r') as f:
                    errors = json.load(f)
                    if not isinstance(errors, list):
                        errors = []
            except Exception:
                errors = []
        
        errors.append(error_entry)
        # Keep last 50 errors to avoid massive file
        errors = errors[-50:]
        
        with open(self.error_file, 'w') as f:
            json.dump(errors, f, indent=4)

    async def generate_content_async(self, prompt: str, audio_base64: Optional[str] = None, model_type: str = "note", system_instruction: Optional[str] = None) -> str:
        # Map 'note' to 'note_generation' to match config key
        config_prefix = "note_generation" if model_type == "note" else model_type
        model_name = self.config.get(f"{config_prefix}_model") or "gemini-2.0-flash"
        
        max_accounts_to_try = len(self.auth_service.accounts) or 1
        accounts_tried = 0
        
        while accounts_tried < max_accounts_to_try:
            accounts_tried += 1
            auth_record = self.auth_service.get_next_account()
            if not auth_record:
                raise Exception("No Gemini CLI accounts configured. Please add an account first.")
            
            # Ensure token is valid
            try:
                auth_record = await self.auth_service.get_valid_account(auth_record)
            except Exception as e:
                logger.error(f"Failed to refresh token for {auth_record.get('email')}: {e}")
                continue # Try next account

            # Prepare parts
            parts = []
            if audio_base64:
                parts.append({"inline_data": {"mime_type": "audio/mp3", "data": audio_base64}})
            parts.append({"text": prompt})

            request_id = f"pi-{int(time.time()*1000)}-{os.urandom(4).hex()}"
            request_body = {
                "project": auth_record["projectId"],
                "model": model_name,
                "request": {
                    "contents": [
                        {
                            "role": "user",
                            "parts": parts,
                        },
                    ],
                },
                "userAgent": "pi-cli-standalone",
                "requestId": request_id,
            }

            # Add systemInstruction inside 'request' with camelCase
            if system_instruction:
                request_body["request"]["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }

            for attempt in range(self.api_max_retries + 1):
                logger.info(f"Gemini API Request - Account: {auth_record['email']}, Type: {model_type}, Model: {model_name} (Attempt: {attempt + 1})")
                
                start_time = time.time()
                try:
                    async with httpx.AsyncClient(timeout=self.api_timeout) as client:
                        resp = await client.post(
                            f"{self.CODE_ASSIST_ENDPOINT}/v1internal:streamGenerateContent?alt=sse",
                            headers={
                                "Authorization": f"Bearer {auth_record['access']}",
                                "Content-Type": "application/json",
                                "Accept": "text/event-stream",
                                **self.GEMINI_CLI_HEADERS,
                            },
                            json=request_body
                        )

                        if resp.status_code != 200:
                            error_payload = resp.text
                            try:
                                error_payload = resp.json()
                            except: pass
                            
                            self._log_error(request_body, error_payload)
                            logger.error(f"Gemini API Error ({resp.status_code}) for {auth_record['email']}")
                            
                            if resp.status_code == 429:
                                backoff_429 = BackoffManager(initial_delay=30, max_delay=300)
                                logger.warning(f"Rate limit (429) for {auth_record['email']}. Waiting and retrying indefinitely...")
                                await backoff_429.async_sleep(attempt)
                                accounts_tried = 0 # Reset safety to allow indefinite retries
                                break # Move to next account (or same if only one)
                            
                            if resp.status_code in [401, 403]:
                                break # Move to next account
                            
                            if resp.status_code == 503:
                                logger.warning("Service Unavailable (503). Retrying...")
                                await self.backoff_manager.async_sleep(attempt)
                                continue
                            
                            raise Exception(f"API Error {resp.status_code}: {resp.text}")

                        # Process SSE stream
                        full_text = ""
                        for line in resp.iter_lines():
                            # Ensure line is a string for startswith and slicing
                            if isinstance(line, bytes):
                                line = line.decode('utf-8')
                                
                            if line.startswith("data:"):
                                json_str = line[5:].strip()
                                if not json_str: continue
                                try:
                                    chunk = json.loads(json_str)
                                    candidates = chunk.get("response", {}).get("candidates", [])
                                    if candidates:
                                        parts_resp = candidates[0].get("content", {}).get("parts", [])
                                        for p in parts_resp:
                                            if "text" in p:
                                                full_text += p["text"]
                                except Exception:
                                    continue

                        duration = time.time() - start_time
                        logger.info(f"Gemini API Response - Success - Duration: {duration:.2f}s")
                        
                        # Record usage
                        self.usage_tracker.record_usage(auth_record["email"] or "unknown", model_name)
                        return full_text

                except httpx.TimeoutException:
                    logger.warning(f"Gemini API Timeout (Attempt {attempt+1})")
                    if attempt >= self.api_max_retries:
                        break # Try next account
                    await self.backoff_manager.async_sleep(attempt)
                except Exception as e:
                    logger.error(f"Gemini API Exception ({type(e).__name__}): {e}")
                    self._log_error(request_body, f"{type(e).__name__}: {str(e)}")
                    if attempt >= self.api_max_retries:
                        break # Try next account
                    await self.backoff_manager.async_sleep(attempt)

        raise Exception("All configured Gemini CLI accounts failed or were skipped.")

    # Synchronous wrappers for existing pipeline
    def generate_content(self, prompt, model_type="note", system_instruction=None):
        import asyncio
        return asyncio.run(self.generate_content_async(prompt, model_type=model_type, system_instruction=system_instruction))

    def generate_content_with_file(self, file_path, prompt, model_type="transcription", system_instruction=None):
        import asyncio
        audio_base64 = AudioProcessor.encode_to_base64(file_path)
        return asyncio.run(self.generate_content_async(prompt, audio_base64=audio_base64, model_type=model_type, system_instruction=system_instruction))

    def _wait_for_file_active(self, client, file_obj):
        """Waits for the uploaded file to be in ACTIVE state."""
        while file_obj.state == "PROCESSING":
            time.sleep(2)
            file_obj = client.files.get(name=file_obj.name)
        
        if file_obj.state != "ACTIVE":
            raise Exception(f"File {file_obj.name} failed to process with state {file_obj.state}")
