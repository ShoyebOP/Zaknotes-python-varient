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
    def get_mock(key, default=None):
        if key == "notion_integration_enabled": return True
        return default
    config.get.side_effect = get_mock
    return config

@pytest.fixture
def job():
    return {"id": "123", "name": "Test_Job", "url": "http://example.com", "status": "queue"}

@patch('src.pipeline.download_audio')
@patch('src.pipeline.AudioProcessor')
@patch('src.pipeline.GeminiAPIWrapper')
@patch('src.pipeline.NoteGenerationService.generate')
@patch('src.pipeline.NotionService')
@patch('src.pipeline.NotionConfigManager')
@patch('src.pipeline.os')
@patch('src.pipeline.shutil')
@patch('src.pipeline.JobManager')
@patch('src.pipeline.FileCleanupService.cleanup_job_files')
def test_execute_job_notion_success(mock_cleanup, mock_job_manager_class, mock_shutil, mock_os, mock_notion_config_class, mock_notion_service_class, mock_notes, mock_api_class, mock_audio_class, mock_down, mock_config, job):
    # Setup mocks
    mock_os.path.exists.return_value = True
    mock_os.path.join = os.path.join
    mock_os.path.basename = os.path.basename
    mock_os.path.splitext = os.path.splitext
    
    mock_notion_config = mock_notion_config_class.return_value
    mock_notion_config.get_credentials.return_value = ("secret", "db_id")
    
    mock_notion_service = mock_notion_service_class.return_value
    mock_notion_service.create_page.return_value = "http://notion.url"
    
    mock_audio_class.get_duration.return_value = 100
    
    mock_notes.return_value = True
    
    pipeline = ProcessingPipeline(mock_config)
    
    with patch('builtins.open', MagicMock()) as mock_open:
        # Mock file reading for markdown
        mock_open.return_value.__enter__.return_value.read.return_value = "MD Content"
        
        success = pipeline.execute_job(job)
        
        assert success is True
        mock_notion_service.create_page.assert_called_once()
        # Verify title formatting: Test_Job -> Test Job
        args, kwargs = mock_notion_service.create_page.call_args
        assert args[0] == "Test Job" 

@patch('src.pipeline.download_audio')
@patch('src.pipeline.AudioProcessor')
@patch('src.pipeline.GeminiAPIWrapper')
@patch('src.pipeline.NoteGenerationService.generate')
@patch('src.pipeline.NotionService')
@patch('src.pipeline.NotionConfigManager')
@patch('src.pipeline.os')
@patch('src.pipeline.shutil')
@patch('src.pipeline.JobManager')
@patch('src.pipeline.FileCleanupService.cleanup_job_files')
def test_execute_job_notion_failure(mock_cleanup, mock_job_manager_class, mock_shutil, mock_os, mock_notion_config_class, mock_notion_service_class, mock_notes, mock_api_class, mock_audio_class, mock_down, mock_config, job):
    # Setup mocks
    mock_os.path.exists.return_value = True
    mock_os.path.join = os.path.join
    mock_os.path.basename = os.path.basename
    mock_os.path.splitext = os.path.splitext
    
    mock_notion_config = mock_notion_config_class.return_value
    mock_notion_config.get_credentials.return_value = ("secret", "db_id")
    
    mock_notion_service = mock_notion_service_class.return_value
    mock_notion_service.create_page.side_effect = Exception("API Error")
    
    mock_audio_class.get_duration.return_value = 100
    mock_notes.return_value = True
    
    mock_manager = mock_job_manager_class.return_value
    pipeline = ProcessingPipeline(mock_config, job_manager=mock_manager)
    
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "MD Content"
        success = pipeline.execute_job(job)
        
        assert success is True # Pipeline itself succeeded in generating notes
        mock_manager.update_job_status.assert_called_with('123', 'completed_local_only')
        
        # Verify final_notes_path was NOT added to cleanup
        cleanup_args = mock_cleanup.call_args[0][0]
        assert not any("notes" in f for f in cleanup_args)
        
        # Verify local file deletion after success (Wait, task 2 implements deletion)
        # For now, just check if it was called.
