import os
import sys
import subprocess
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_processor import AudioProcessor

@pytest.fixture
def dummy_file(tmp_path):
    """Creates a 1KB dummy file."""
    p = tmp_path / "test.mp3"
    p.write_bytes(b"\0" * 1024)
    return str(p)

@pytest.fixture
def real_audio_file(tmp_path):
    """Creates a 5-second silent MP3 file."""
    p = tmp_path / "silent.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", 
        "-t", "5", "-b:a", "128k", str(p)
    ], check=True, capture_output=True)
    return str(p)

def test_get_file_size(dummy_file):
    """Test retrieving file size in bytes."""
    size = AudioProcessor.get_file_size(dummy_file)
    assert size == 1024

def test_is_under_limit(dummy_file):
    """Test file size limit validation."""
    # 1KB is under 1MB limit
    assert AudioProcessor.is_under_limit(dummy_file, limit_mb=1) is True
    
    # Create a 2MB file
    large_file = os.path.join(os.path.dirname(dummy_file), "large.mp3")
    with open(large_file, "wb") as f:
        f.write(b"\0" * (2 * 1024 * 1024))
    
    # 2MB is NOT under 1MB limit
    assert AudioProcessor.is_under_limit(large_file, limit_mb=1) is False

def test_reencode_audio(real_audio_file, tmp_path):
    """Test re-encoding audio to a lower bitrate."""
    output_file = str(tmp_path / "reencoded.mp3")
    
    # Re-encode with very low bitrate
    success = AudioProcessor.reencode_audio(real_audio_file, output_file, bitrate="16k")
    
    assert success is True
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) < os.path.getsize(real_audio_file)

def test_split_into_chunks(real_audio_file, tmp_path):
    """Test splitting audio into chunks."""
    output_pattern = str(tmp_path / "chunk_%03d.mp3")
    
    # Split 5s file into 2s chunks -> should produce 3 chunks (2s, 2s, 1s)
    chunks = AudioProcessor.split_into_chunks(real_audio_file, output_pattern, segment_time=2)
    
    assert len(chunks) >= 2
    for chunk in chunks:
        assert os.path.exists(chunk)

def test_process_for_transcription_small(dummy_file):
    """Test orchestration for a small file."""
    chunks = AudioProcessor.process_for_transcription(dummy_file, limit_mb=100)
    assert chunks == [dummy_file]

def test_process_for_transcription_large(real_audio_file, tmp_path):
    """Test orchestration for a file that needs splitting and possibly re-encoding."""
    # real_audio_file is ~80KB. Set limit to 40KB.
    limit = 0.04 
    
    chunks = AudioProcessor.process_for_transcription(
        real_audio_file, 
        limit_mb=limit, 
        segment_time=2,
        output_dir=str(tmp_path)
    )
    
    assert len(chunks) >= 2
    for chunk in chunks:
        assert AudioProcessor.is_under_limit(chunk, limit_mb=limit)