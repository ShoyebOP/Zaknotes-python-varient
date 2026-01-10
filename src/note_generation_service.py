import os
from src.gemini_wrapper import GeminiCLIWrapper
from src.prompts import NOTE_GENERATION_PROMPT

class NoteGenerationService:
    @staticmethod
    def generate(transcript_path: str, model: str, output_path: str, prompt_text: str = None) -> bool:
        """
        Generates notes from a transcript file.
        Saves the notes to output_path.
        """
        if not os.path.exists(transcript_path):
            print(f"      ❌ Transcript file not found: {transcript_path}")
            return False

        if prompt_text is None:
            prompt_text = NOTE_GENERATION_PROMPT

        prompt = prompt_text.replace("@transcription/file/location", f"@{transcript_path}")
        args = ["-m", model, "--output-format", "json", prompt]
        
        result = GeminiCLIWrapper.run_command(args)
        
        # Use robust extraction
        notes = GeminiCLIWrapper.extract_response_content(result['stdout'])
        
        if notes:
            out_dir = os.path.dirname(output_path)
            if out_dir and not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)
                
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(notes)
            
            if len(result['stdout']) >= 65000:
                print(f"      ⚠️ Warning: Note output was very large and likely truncated.")
            return True
        else:
            if not result['success']:
                print(f"      ❌ Note generation failed: {result.get('stderr')}")
            else:
                print("      ⚠️ Warning: No notes extracted.")
            return False