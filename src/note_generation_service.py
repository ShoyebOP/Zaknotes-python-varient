import json
import os
from src.gemini_wrapper import GeminiCLIWrapper

class NoteGenerationService:
    @staticmethod
    def generate(transcript_path: str, model: str, output_path: str, prompt_template_path: str = "demo/note generation prompt.txt") -> bool:
        """
        Generates notes from a transcript file using the specified model and prompt template.
        Saves the notes to output_path.
        """
        if not os.path.exists(transcript_path):
            print(f"Error: Transcript file not found: {transcript_path}")
            return False

        if not os.path.exists(prompt_template_path):
            print(f"Error: Prompt template not found: {prompt_template_path}")
            return False

        try:
            with open(prompt_template_path, 'r') as f:
                prompt_template = f.read()
        except IOError as e:
            print(f"Error reading prompt template: {e}")
            return False

        # Replace placeholder with file reference format for CLI
        # We replace it with "@{transcript_path}" so the CLI tool expands it.
        prompt = prompt_template.replace("@transcription/file/location", f"@{transcript_path}")
        
        args = [
            "-m", model,
            "--output-format", "json",
            prompt
        ]
        
        result = GeminiCLIWrapper.run_command(args)
        
        if not result['success']:
            print(f"Note generation failed: {result.get('stderr')}")
            return False
            
        try:
            data = json.loads(result['stdout'])
            notes = data.get("response", "")
            if notes:
                # Ensure output dir exists
                out_dir = os.path.dirname(output_path)
                if out_dir and not os.path.exists(out_dir):
                    os.makedirs(out_dir, exist_ok=True)
                    
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(notes)
                return True
            else:
                print("Warning: Empty response for note generation")
                return False
        except json.JSONDecodeError:
            print("Error: Invalid JSON from gemini for note generation")
            return False
