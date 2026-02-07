import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import ProcessingPipeline
from src.config_manager import ConfigManager

@pytest.fixture
def pipeline_setup():
    config = ConfigManager()
    api = MagicMock()
    # Mock KeyManager to avoid reset_quotas_if_needed errors
    api.key_manager = MagicMock()
    job_manager = MagicMock()
    pipeline = ProcessingPipeline(config, api, job_manager)
    return pipeline

def test_resume_from_downloaded(pipeline_setup):
    """Test that if status is DOWNLOADED and file exists, download is skipped."""
    pipeline = pipeline_setup
    job = {
        "id": "job1",
        "name": "Test Job",
        "url": "http://example.com",
        "status": "DOWNLOADED"
    }

    with patch("src.downloader.get_expected_audio_path") as mock_path, \
         patch("src.pipeline.os.path.exists") as mock_exists, \
         patch("src.downloader.download_audio") as mock_download, \
         patch("src.audio_processor.AudioProcessor.remove_silence") as mock_silence, \
         patch("src.audio_processor.AudioProcessor.reencode_to_optimal") as mock_reencode, \
         patch("src.pipeline.os.listdir") as mock_listdir, \
         patch("src.pipeline.shutil.copy2") as mock_copy, \
         patch("src.audio_processor.AudioProcessor.get_duration") as mock_duration:

        mock_path.return_value = "downloads/Test_Job.mp3"
        # Control os.path.exists to simulate file presence
        mock_exists.side_effect = lambda p: True if "Test_Job" in p or p == "temp" or "downloads" in p else False
        mock_duration.return_value = 100
        mock_listdir.return_value = [] # No chunks yet

        # Stop execution before API call to keep test simple
        pipeline.api.generate_content_with_file.side_effect = Exception("Stop here")

        try:
            pipeline.execute_job(job)
        except Exception as e:
            if str(e) != "Stop here" and "No such file or directory" not in str(e): raise

        mock_download.assert_not_called()
        # Should call silence removal since status is DOWNLOADED
        assert mock_silence.called or mock_reencode.called or mock_copy.called

def test_resume_from_chunked(pipeline_setup):
    """Test that if status is CHUNKED, download and processing are skipped."""
    pipeline = pipeline_setup
    job = {
        "id": "job1",
        "name": "Test Job",
        "url": "http://example.com",
        "status": "CHUNKED"
    }

    with patch("src.downloader.get_expected_audio_path") as mock_path, \
         patch("src.pipeline.os.path.exists") as mock_exists, \
         patch("src.pipeline.os.listdir") as mock_listdir, \
         patch("src.downloader.download_audio") as mock_download, \
         patch("src.audio_processor.AudioProcessor.remove_silence") as mock_silence, \
         patch("src.pipeline.open", MagicMock()):

        mock_path.return_value = "downloads/Test_Job.mp3"
        mock_exists.side_effect = lambda p: True if "job1" in p or p == "temp" or "downloads" in p or "Test_Job" in p else False
        # listdir returns chunks for this job
        mock_listdir.return_value = ["job_job1_chunk_001.mp3", "job_job1_chunk_002.mp3"]

        pipeline.api.generate_content_with_file.side_effect = Exception("Stop here")

        try:
            pipeline.execute_job(job)
        except Exception as e:
            if str(e) != "Stop here" and "No such file or directory" not in str(e): raise

        mock_download.assert_not_called()
        mock_silence.assert_not_called()
        assert pipeline.api.generate_content_with_file.called

def test_resume_transcription_skip_chunks(pipeline_setup):
    """Test that already transcribed chunks are skipped."""
    pipeline = pipeline_setup
    job = {
        "id": "job1",
        "name": "Test Job",
        "url": "http://example.com",
        "status": "TRANSCRIBING_CHUNK_1",
        "transcriptions": {"1": "Already done"}
    }

    with patch("src.downloader.get_expected_audio_path") as mock_path, \
         patch("src.pipeline.os.path.exists") as mock_exists, \
         patch("src.pipeline.os.listdir") as mock_listdir, \
         patch("src.pipeline.open", MagicMock()):

        mock_path.return_value = "downloads/Test_Job.mp3"
        # We need DOWNLOADED to be skipped, so audio_path must exist
        mock_exists.side_effect = lambda p: True if "job1" in p or p == "temp" or "Test_Job" in p else False
        mock_listdir.return_value = ["job_job1_chunk_001.mp3", "job_job1_chunk_002.mp3"]

        # If it tries to transcribe chunk 1, this will fail. If it skips, it will try chunk 2 and fail there.
        pipeline.api.generate_content_with_file.side_effect = [Exception("Stop at chunk 2")]

        try:
            pipeline.execute_job(job)
        except Exception as e:
            if str(e) != "Stop at chunk 2" and "No such file or directory" not in str(e): raise

        # Verify it skipped chunk 1 (the first call to generate_content_with_file was for "Stop at chunk 2")
        assert pipeline.api.generate_content_with_file.call_count == 1
        args, kwargs = pipeline.api.generate_content_with_file.call_args
        assert "chunk_002" in kwargs['file_path']
