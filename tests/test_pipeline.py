import os
import sys
import pytest
from unittest.mock import patch, MagicMock, ANY

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import ProcessingPipeline

@pytest.fixture
def mock_config():
    config = MagicMock()
    # Default values for models
    def get_mock(key, default=None):
        if "transcription" in key: return "model-trans"
        if "note" in key: return "model-note"
        if "segment_time" in key: return 1800
        return default
    
    config.get.side_effect = get_mock
    return config

@pytest.fixture
def job():
    return {"id": "123", "name": "Test Job", "url": "http://example.com", "status": "queue"}

@patch('src.pipeline.download_audio')
@patch('src.pipeline.AudioProcessor.process_for_transcription')
@patch('src.pipeline.GeminiAPIWrapper')
@patch('src.pipeline.NoteGenerationService.generate')
def test_execute_job_success(mock_notes, mock_api_class, mock_audio, mock_down, mock_config, job):
    """Test successful execution of the full pipeline."""
    # Setup mocks
    mock_down.return_value = "downloads/Test_Job.mp3"
    mock_audio.return_value = ["temp/chunk1.mp3"]
    mock_notes.return_value = True
    
    mock_api = mock_api_class.return_value
    mock_api.generate_content_with_file.return_value = "Transcript text"
    
    pipeline = ProcessingPipeline(mock_config)
    
    # Mock filesystem interactions
    with patch('os.path.exists', return_value=True), \
         patch('os.remove') as mock_remove, \
         patch('os.makedirs'), \
         patch('builtins.open', MagicMock()):
        
        success = pipeline.execute_job(job)
        
        assert success is True
        assert job['status'] == 'completed'
        mock_down.assert_called_once()
        # Verify it was called with threads parameter
        mock_audio.assert_called_once_with(
            "downloads/Test_Job.mp3",
            segment_time=1800,
            output_dir="temp",
            threads=0 # default balanced -> 0
        )
        mock_api.generate_content_with_file.assert_called_once()
        mock_notes.assert_called_once()


@patch('src.pipeline.download_audio')
def test_execute_job_download_failure(mock_down, mock_config, job):
    """Test pipeline failure when download fails."""
    mock_down.return_value = None
    
    pipeline = ProcessingPipeline(mock_config)
    success = pipeline.execute_job(job)
    
    assert success is False
    assert job['status'] == 'failed'