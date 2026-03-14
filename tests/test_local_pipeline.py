import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import ProcessingPipeline

@pytest.fixture
def mock_config():
    config = MagicMock()
    config.get.side_effect = lambda k, d=None: d
    return config

@pytest.fixture
def local_job():
    return {
        "id": "local_123",
        "name": "Local Test Job",
        "file_path": "uploads/test.mp3",
        "status": "queue"
    }

@patch('src.pipeline.download_audio')
@patch('src.pipeline.AudioProcessor')
@patch('src.pipeline.GeminiAPIWrapper')
@patch('src.pipeline.NoteGenerationService.generate')
@patch('src.pipeline.os')
@patch('src.pipeline.shutil')
@patch('src.pipeline.JobManager')
def test_execute_local_job_success(mock_job_manager_class, mock_shutil, mock_os, mock_notes, mock_api_class, mock_audio_class, mock_down, mock_config, local_job):
    """Test successful execution of the pipeline with a local file."""
    # Setup mocks
    mock_manager = mock_job_manager_class.get_instance.return_value if hasattr(mock_job_manager_class, 'get_instance') else mock_job_manager_class.return_value
    
    # OS mocks
    def exists_side_effect(path):
        if path == "uploads/test.mp3": return True # Local file exists
        if "chunk" in path: return True # Chunks exist
        return False
    mock_os.path.exists.side_effect = exists_side_effect
    
    mock_os.path.join = os.path.join
    mock_os.path.basename = os.path.basename
    mock_os.path.splitext = os.path.splitext
    
    # AudioProcessor mocks
    mock_audio_class.process_for_transcription.return_value = ["temp/chunk_1.mp3"]
    
    # API mocks
    mock_api = mock_api_class.return_value
    mock_api.generate_content_with_file.return_value = "Transcript text"
    
    mock_notes.return_value = True
    
    pipeline = ProcessingPipeline(mock_config, job_manager=mock_manager)
    
    with patch('builtins.open', MagicMock()):
        success = pipeline.execute_job(local_job)
        
        assert success is True
        # Verify download was NEVER called for local job
        mock_down.assert_not_called()
        
        # Verify status update for local job
        mock_manager.update_job_status.assert_any_call('local_123', 'DOWNLOADED')
        mock_manager.update_job_status.assert_any_call('local_123', 'completed')

if __name__ == '__main__':
    pytest.main([__file__])
