import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import ProcessingPipeline

@pytest.fixture
def mock_config():
    config = MagicMock()
    config.get.side_effect = lambda key, default=None: {
        "rclone_integration_enabled": True,
        "notion_integration_enabled": False,
        "segment_time": 1800,
        "max_chunk_size_mb": 15
    }.get(key, default)
    return config

@pytest.fixture
def mock_job_manager():
    return MagicMock()

@pytest.fixture
def mock_api():
    api = MagicMock()
    api.generate_content_with_file.return_value = "Test transcript"
    return api

@pytest.fixture
def pipeline(mock_config, mock_api, mock_job_manager):
    with patch('src.pipeline.NotionConfigManager'), \
         patch('src.pipeline.RcloneConfigManager'), \
         patch('src.pipeline.RcloneService'):
        p = ProcessingPipeline(mock_config, api_wrapper=mock_api, job_manager=mock_job_manager)
        # Manually set mocks for services
        p.rclone_config = MagicMock()
        p.rclone_config.get_credentials.return_value = ("remote", "path")
        p.rclone_service = MagicMock()
        p.rclone_service.push_note.return_value = (True, "Success")
        return p

@patch('src.pipeline.download_audio')
@patch('src.pipeline.get_expected_audio_path')
@patch('src.pipeline.AudioProcessor')
@patch('src.pipeline.NoteGenerationService')
@patch('src.pipeline.FileCleanupService')
@patch('os.path.exists')
@patch('os.makedirs')
def test_pipeline_rclone_push_called(mock_makedirs, mock_exists, mock_cleanup, mock_note_gen, mock_audio_proc, mock_get_path, mock_download, pipeline):
    """Test that rclone_service.push_note is called when enabled."""
    # Setup mocks for file existence
    mock_exists.return_value = True
    mock_get_path.return_value = "audio.mp3"
    mock_download.return_value = "audio.mp3"
    mock_audio_proc.optimize_audio.return_value = True
    mock_audio_proc.process_for_transcription.return_value = ["chunk1.mp3"]
    mock_note_gen.generate.return_value = True
    
    # Mock open for reading transcript and note
    with patch("builtins.open", MagicMock()):
        job = {"id": 1, "name": "Test Job", "status": "queue"}
        success = pipeline.execute_job(job)
        
        assert success is True
        pipeline.rclone_service.push_note.assert_called_once()
        
        # Verify job status updated to completed
        pipeline.manager.update_job_status.assert_any_call(1, 'completed')

@patch('src.pipeline.download_audio')
@patch('src.pipeline.get_expected_audio_path')
@patch('src.pipeline.AudioProcessor')
@patch('src.pipeline.NoteGenerationService')
@patch('src.pipeline.FileCleanupService')
@patch('os.path.exists')
@patch('os.makedirs')
def test_pipeline_rclone_failed_push_keeps_file(mock_makedirs, mock_exists, mock_cleanup, mock_note_gen, mock_audio_proc, mock_get_path, mock_download, pipeline):
    """Test that failed rclone push marks job as completed_local_only and keeps the note file."""
    # Setup mocks
    mock_exists.return_value = True
    mock_get_path.return_value = "audio.mp3"
    mock_download.return_value = "audio.mp3"
    mock_audio_proc.optimize_audio.return_value = True
    mock_audio_proc.process_for_transcription.return_value = ["chunk1.mp3"]
    mock_note_gen.generate.return_value = True
    
    # Mock push failure
    pipeline.rclone_service.push_note.return_value = (False, "Failure")
    
    with patch("builtins.open", MagicMock()):
        job = {"id": 1, "name": "Test Job", "status": "queue"}
        success = pipeline.execute_job(job)
        
        assert success is True # Pipeline overall success (local file exists)
        pipeline.manager.update_job_status.assert_any_call(1, 'completed_local_only')
        
        # Verify note file is NOT in the cleanup list
        cleanup_call_args = mock_cleanup.cleanup_job_files.call_args[0][0]
        # Find the .md file in the cleanup list (should not be there)
        md_files = [f for f in cleanup_call_args if f.endswith(".md")]
        assert len(md_files) == 0
