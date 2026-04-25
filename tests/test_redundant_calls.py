import os
import sys
import pytest
import shutil
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline import ProcessingPipeline
from src.audio_processor import AudioProcessor

@pytest.fixture
def mock_job():
    return {
        "id": "1",
        "name": "Test Job",
        "url": "https://example.com/audio.mp3",
        "status": "DOWNLOADED"
    }

@patch('src.pipeline.download_audio')
@patch('src.pipeline.get_expected_audio_path')
@patch('src.audio_processor.AudioProcessor.optimize_audio')
@patch('src.audio_processor.AudioProcessor.split_into_chunks')
@patch('src.audio_processor.AudioProcessor.get_duration')
@patch('src.pipeline.GeminiAPIWrapper')
@patch('src.pipeline.JobManager')
def test_redundant_optimization_calls(mock_job_manager, mock_gemini_class, mock_get_duration, mock_split, mock_optimize, mock_get_path, mock_download, mock_job, tmp_path):
    # Setup
    audio_file = tmp_path / "test.mp3"
    audio_file.write_bytes(b"dummy content")
    mock_get_path.return_value = str(audio_file)
    
    # Ensure prepared_path does NOT exist so optimize_audio IS called
    prepared_path = os.path.join("temp", "test_prepared.mp3")
    if os.path.exists(prepared_path):
        os.remove(prepared_path)
    
    # Side effect for optimize_audio to actually create the file
    def side_effect_optimize(input_path, output_path, **kwargs):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(b"optimized content")
        return True
    mock_optimize.side_effect = side_effect_optimize
    
    mock_get_duration.return_value = 100
    mock_split.return_value = [str(tmp_path / "chunk_001.mp3")]
    
    # Mock Gemini API instance
    mock_gemini_instance = mock_gemini_class.return_value
    mock_gemini_instance.generate_content_with_file.return_value = "Mocked transcription"
    
    # Mock pipeline dependencies
    config = MagicMock()
    config.get.side_effect = lambda key, default=None: {
        "segment_time": 1800,
        "max_chunk_size_mb": 15
    }.get(key, default)
    
    pipeline = ProcessingPipeline(config, api_wrapper=mock_gemini_instance)
    
    # Mock transcription and notes to avoid long runs
    with patch('src.pipeline.NoteGenerationService.generate') as mock_notes:
        mock_notes.return_value = True
        with patch('src.pipeline.FileCleanupService.cleanup_job_files'):
            pipeline.execute_job(mock_job)
    
    # EXPECTATION: This should now be EXACTLY 1
    assert mock_optimize.call_count == 1, f"Expected 1 call to optimize_audio, but got {mock_optimize.call_count}"
    
    # Cleanup
    if os.path.exists("temp"):
        shutil.rmtree("temp")

if __name__ == "__main__":
    pytest.main([__file__])
