import os
import sys
import json
import pytest
from unittest.mock import patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.note_generation_service import NoteGenerationService

@pytest.fixture
def prompt_template(tmp_path):
    p = tmp_path / "prompt_template.txt"
    p.write_text("Generate notes for @transcription/file/location")
    return str(p)

@pytest.fixture
def transcript_file(tmp_path):
    p = tmp_path / "transcript.txt"
    p.write_text("This is the transcript.")
    return str(p)

@pytest.fixture
def output_md(tmp_path):
    return str(tmp_path / "notes.md")

@patch('src.gemini_wrapper.GeminiCLIWrapper.run_command')
def test_generate_success(mock_run, transcript_file, output_md, prompt_template):
    """Test successful note generation."""
    mock_run.return_value = {
        "success": True, 
        "stdout": json.dumps({"response": "# Notes\nContent"})
    }
    
    success = NoteGenerationService.generate(
        transcript_path=transcript_file,
        model="model-y",
        output_path=output_md,
        prompt_template_path=prompt_template
    )
    
    assert success is True
    
    # Verify prompt construction
    # args[0] is the list of arguments passed to run_command
    args = mock_run.call_args[0][0]
    # The service should replace the placeholder with @filepath
    expected_prompt_arg = f"Generate notes for @{transcript_file}"
    assert expected_prompt_arg in args
    
    with open(output_md, 'r') as f:
        assert f.read() == "# Notes\nContent"

@patch('src.gemini_wrapper.GeminiCLIWrapper.run_command')
def test_generate_failure(mock_run, transcript_file, output_md, prompt_template):
    """Test failure in note generation."""
    mock_run.return_value = {"success": False, "stderr": "error"}
    
    success = NoteGenerationService.generate(
        transcript_path=transcript_file,
        model="model-y",
        output_path=output_md,
        prompt_template_path=prompt_template
    )
    
    assert success is False
    assert not os.path.exists(output_md)
