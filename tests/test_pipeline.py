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
    config.get.side_effect = lambda k: "model-trans" if "transcription" in k else "model-note"
    return config

@pytest.fixture
def job():
    return {"id": "123", "name": "Test Job", "url": "http://example.com", "status": "queue"}

@patch('src.pipeline.download_audio')
@patch('src.pipeline.AudioProcessor.process_for_transcription')
@patch('src.pipeline.TranscriptionService.transcribe_chunks')
@patch('src.pipeline.NoteGenerationService.generate')
@patch('src.pipeline.PdfConverter')
def test_execute_job_success(mock_pdf_class, mock_notes, mock_trans, mock_audio, mock_down, mock_config, job):
    """Test successful execution of the full pipeline."""
    # Setup mocks
    mock_down.return_value = "downloads/Test_Job.mp3"
    mock_audio.return_value = ["temp/chunk1.mp3"]
    mock_trans.return_value = True
    mock_notes.return_value = True
    
    # Mock PDF converter instance methods
    mock_pdf_instance = mock_pdf_class.return_value
    
    pipeline = ProcessingPipeline(mock_config)
    
    # Mock filesystem interactions
    with patch('os.path.exists', return_value=True), \
         patch('os.remove') as mock_remove, \
         patch('os.makedirs'):
        
        success = pipeline.execute_job(job)
        
        assert success is True
        assert job['status'] == 'completed'
        mock_down.assert_called_once()
        mock_audio.assert_called_once()
        mock_trans.assert_called_once_with(["temp/chunk1.mp3"], "model-trans", ANY)
        mock_notes.assert_called_once_with(ANY, "model-note", ANY)
        
        # Verify cleanup was called
        assert mock_remove.called

@patch('src.pipeline.download_audio')
def test_execute_job_download_failure(mock_down, mock_config, job):
    """Test pipeline failure when download fails."""
    mock_down.return_value = None
    
    pipeline = ProcessingPipeline(mock_config)
    success = pipeline.execute_job(job)
    
    assert success is False
    assert job['status'] == 'failed'