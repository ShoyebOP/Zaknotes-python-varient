import json
import os
from typing import List
from src.gemini_wrapper import GeminiCLIWrapper

class TranscriptionService:
    @staticmethod
    def transcribe_chunks(chunks: List[str], model: str, output_file: str) -> bool:
        """
        Transcribes a list of audio chunks and appends text to output_file.
        Returns True if all chunks succeeded, False otherwise.
        """
        # Ensure directory exists
        out_dir = os.path.dirname(output_file)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # Clear output file first
        if os.path.exists(output_file):
            os.remove(output_file)

        for chunk in chunks:
            prompt = f"Transcribe this audio @{chunk} exactly as spoken. Output *only* the transcript text, no explanation, no translation."
            args = [
                "-m", model,
                "--output-format", "json",
                prompt
            ]
            
            result = GeminiCLIWrapper.run_command(args)
            
            if not result['success']:
                print(f"Transcription failed for chunk {chunk}: {result.get('stderr')}")
                return False
                
            try:
                data = json.loads(result['stdout'])
                text = data.get("response", "")
                if text:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(text)
                else:
                    print(f"Warning: Empty response for chunk {chunk}")
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON from gemini for chunk {chunk}")
                return False
                
        return True
