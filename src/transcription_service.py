import os
from typing import List
from src.gemini_wrapper import GeminiCLIWrapper
from src.prompts import TRANSCRIPTION_PROMPT

class TranscriptionService:
    @staticmethod
    def transcribe_chunks(chunks: List[str], model: str, output_file: str) -> bool:
        """
        Transcribes a list of audio chunks and appends text to output_file.
        Returns True if at least some transcription was successful.
        """
        out_dir = os.path.dirname(output_file)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        if os.path.exists(output_file):
            os.remove(output_file)

        any_success = False
        for i, chunk in enumerate(chunks):
            print(f"      - Processing chunk {i+1}/{len(chunks)}...")
            prompt = TRANSCRIPTION_PROMPT.format(chunk=chunk)
            args = ["-m", model, "--output-format", "json", prompt]
            
            result = GeminiCLIWrapper.run_command(args)
            
            # Extract content using the robust method (handles truncated JSON)
            text = GeminiCLIWrapper.extract_response_content(result['stdout'])
            
            if text:
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(text)
                    f.write("\n\n") # Double newline between chunks
                any_success = True
                if len(result['stdout']) >= 65000:
                    print(f"      ⚠️ Warning: Chunk {i+1} output was very large and likely truncated. Captured what was available.")
            else:
                if not result['success']:
                    print(f"      ❌ Failed to get transcription for chunk {i+1}: {result.get('stderr')}")
                else:
                    print(f"      ⚠️ Warning: No text extracted from chunk {i+1}")
                return False # Fail-fast on complete failure
                
        return any_success