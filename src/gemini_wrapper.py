import subprocess
import json
import re
from typing import List, Dict, Any

class GeminiCLIWrapper:
    @staticmethod
    def run_command(args: List[str]) -> Dict[str, Any]:
        """
        Runs the gemini CLI with the provided arguments.
        Returns a dictionary with success status, stdout (string), and stderr.
        """
        if args and args[0] == "gemini":
            command = args
        else:
            command = ["gemini"] + args
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=False,
                check=True
            )
            # result.stdout/stderr are bytes here because text=False
            stdout = result.stdout.decode('utf-8', errors='ignore')
            stderr = result.stderr.decode('utf-8', errors='ignore')
            
            return {
                "success": True,
                "stdout": stdout,
                "stderr": stderr
            }
        except subprocess.CalledProcessError as e:
            # e.stdout/stderr might be None or bytes
            stdout = e.stdout.decode('utf-8', errors='ignore') if e.stdout else ""
            stderr = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
            return {
                "success": False,
                "stdout": stdout,
                "stderr": stderr
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e)
            }

    @staticmethod
    def extract_response_content(raw_stdout: str) -> str:
        """
        Attempts to extract the content of the "response" field.
        Handles both valid JSON and truncated/broken JSON using regex fallback.
        """
        if not raw_stdout:
            return ""

        # 1. Try normal JSON parsing first
        try:
            data = json.loads(raw_stdout)
            if isinstance(data, dict) and "response" in data:
                return data["response"]
        except json.JSONDecodeError:
            pass

        # 2. Fallback: extraction for truncated JSON
        marker = '"response": "'
        idx = raw_stdout.find(marker)
        if idx == -1:
            if not raw_stdout.strip().startswith('{'):
                return raw_stdout.strip()
            return ""

        content_start = idx + len(marker)
        content = raw_stdout[content_start:]
        
        # Find the closing quote that isn't escaped
        end_idx = -1
        escaped = False
        for i in range(len(content)):
            char = content[i]
            if char == '\\' and not escaped:
                escaped = True
            elif char == '"' and not escaped:
                end_idx = i
                break
            else:
                escaped = False
                
        if end_idx != -1:
            content = content[:end_idx]
        
        # Unescape common JSON escapes manually
        content = content.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
        
        return content