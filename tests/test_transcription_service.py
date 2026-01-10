import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.transcription_service import TranscriptionService

@pytest.fixture
def output_file(tmp_path):
    return str(tmp_path / "transcript.txt")

@patch('src.gemini_wrapper.GeminiCLIWrapper.run_command')
def test_transcribe_chunks_success(mock_run, output_file):
    """Test successful transcription of multiple chunks."""
    mock_run.side_effect = [
        {"success": True, "stdout": json.dumps({"response": "Part 1"})},
        {"success": True, "stdout": json.dumps({"response": "Part 2"})}
    ]
    
    chunks = ["chunk1.mp3", "chunk2.mp3"]
    success = TranscriptionService.transcribe_chunks(chunks, "model-x", output_file)
    
    assert success is True
    assert mock_run.call_count == 2
    
    with open(output_file, 'r') as f:
        content = f.read()
    # Updated to match the new format: double newline and final newline
    assert "Part 1\n\nPart 2\n\n" == content

@patch('src.gemini_wrapper.GeminiCLIWrapper.run_command')
def test_transcribe_chunks_failure(mock_run, output_file):
    """Test failure in one chunk stops process."""
    mock_run.return_value = {"success": False, "stderr": "error", "stdout": ""}
    
    chunks = ["chunk1.mp3", "chunk2.mp3"]
    success = TranscriptionService.transcribe_chunks(chunks, "model-x", output_file)
    
    assert success is False
