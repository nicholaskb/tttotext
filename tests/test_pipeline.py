from pathlib import Path
import pytest

# Assume the pipeline functions are defined in a module named 'pipeline'.
# These are placeholders since the actual implementation is not present.
try:
    from pipeline import download_video, extract_audio, transcribe_audio, clean_text
except ImportError:
    download_video = extract_audio = transcribe_audio = clean_text = None

@pytest.mark.skipif(download_video is None, reason="pipeline functions not implemented")
def test_video_download_success(tmp_path):
    """Video download should return a valid mp4 file."""
    url = "https://www.tiktok.com/@example/video/1234567890"
    video_path = Path(download_video(url, output_dir=tmp_path))
    assert video_path.exists()
    assert video_path.suffix == ".mp4"
    assert video_path.stat().st_size > 0

@pytest.mark.skipif(download_video is None, reason="pipeline functions not implemented")
def test_video_download_invalid_url(tmp_path):
    """Invalid URL should raise an exception."""
    with pytest.raises(Exception):
        download_video("https://invalid.url", output_dir=tmp_path)


@pytest.mark.skipif(extract_audio is None, reason="pipeline functions not implemented")
def test_audio_extraction_success(tmp_path):
    """Audio extraction should produce a non-empty audio file."""
    # Simulate existing video file
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.write_bytes(b"0" * 100)
    audio_path = Path(extract_audio(dummy_video))
    assert audio_path.exists()
    assert audio_path.suffix in {".wav", ".mp3"}
    assert audio_path.stat().st_size > 0

@pytest.mark.skipif(transcribe_audio is None, reason="pipeline functions not implemented")
def test_transcription_success(tmp_path):
    """Transcription should produce non-empty text."""
    # Simulate audio file
    dummy_audio = tmp_path / "dummy.wav"
    dummy_audio.write_bytes(b"0" * 100)
    text = transcribe_audio(dummy_audio)
    assert isinstance(text, str)
    assert text.strip() != ""

@pytest.mark.skipif(clean_text is None, reason="pipeline functions not implemented")
def test_text_cleaning():
    """Cleaning should remove filler words and punctuation."""
    raw_text = "um, hello world!!!"
    cleaned = clean_text(raw_text)
    assert "um" not in cleaned.lower()
    assert cleaned.endswith("world")

@pytest.mark.skipif(extract_audio is None, reason="pipeline functions not implemented")
def test_audio_extraction_invalid_file(tmp_path):
    """Passing a non-video file should raise an exception."""
    non_video = tmp_path / "file.txt"
    non_video.write_text("not a video")
    with pytest.raises(Exception):
        extract_audio(non_video)

@pytest.mark.skipif(transcribe_audio is None, reason="pipeline functions not implemented")
def test_transcription_empty_audio(tmp_path):
    """Transcribing an empty audio file should raise an exception."""
    empty_audio = tmp_path / "empty.wav"
    empty_audio.write_bytes(b"")
    with pytest.raises(Exception):
        transcribe_audio(empty_audio)
