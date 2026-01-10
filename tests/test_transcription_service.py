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
        {"success": True, "stdout": json.dumps({"response": "Part 1 "})},
        {"success": True, "stdout": json.dumps({"response": "Part 2"})}
    ]
    
    chunks = ["chunk1.mp3", "chunk2.mp3"]
    success = TranscriptionService.transcribe_chunks(chunks, "model-x", output_file)
    
    assert success is True
    assert mock_run.call_count == 2
    
    # Verify arguments
    args1 = mock_run.call_args_list[0][0][0]
    assert "-m" in args1
    assert "model-x" in args1
    assert "@chunk1.mp3" in args1[-1]
    
    with open(output_file, 'r') as f:
        content = f.read()
    assert "Part 1 Part 2" == content

@patch('src.gemini_wrapper.GeminiCLIWrapper.run_command')
def test_transcribe_chunks_failure(mock_run, output_file):
    """Test failure in one chunk stops process."""
    mock_run.return_value = {"success": False, "stderr": "error"}
    
    chunks = ["chunk1.mp3", "chunk2.mp3"]
    success = TranscriptionService.transcribe_chunks(chunks, "model-x", output_file)
    
    assert success is False
    # Depending on implementation, file might exist but be partial, or cleaned up.
    # The spec says "Skip the failed job/chunk and move to the next one (Fail-Fast per job)".
    # This implies the whole transcription task fails.
