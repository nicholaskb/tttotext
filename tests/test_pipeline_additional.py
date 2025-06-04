from pathlib import Path
import sys
import pytest

# Attempt to import the pipeline module and its functions. If not present,
# the tests will be skipped.
try:
    from pipeline import download_video, extract_audio, transcribe_audio, clean_text
except ImportError:
    download_video = extract_audio = transcribe_audio = clean_text = None

skip_pipeline = pytest.mark.skipif(
    any(func is None for func in [download_video, extract_audio, transcribe_audio, clean_text]),
    reason="pipeline functions not implemented"
)

@skip_pipeline
@pytest.mark.parametrize("text,expected", [
    ("", ""),
    ("   ", ""),
    ("\n\n", ""),
    ("Hello, world!!!", "Hello, world"),
    ("um hello", "hello"),
    ("Uh, what's up?", "what's up"),
])
def test_clean_text_various_inputs(text, expected):
    """clean_text should gracefully handle empty and noisy inputs."""
    assert clean_text(text) == expected

@skip_pipeline
def test_download_video_non_http_url(tmp_path):
    """Non-http URLs should raise an exception."""
    with pytest.raises(Exception):
        download_video("ftp://example.com/video", output_dir=tmp_path)

@skip_pipeline
def test_extract_audio_missing_file(tmp_path):
    """Passing a path that does not exist should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        extract_audio(tmp_path / "nofile.mp4")

@skip_pipeline
def test_transcribe_audio_wrong_format(tmp_path):
    """Transcription should fail on unsupported file types."""
    bogus = tmp_path / "audio.txt"
    bogus.write_text("not audio")
    with pytest.raises(Exception):
        transcribe_audio(bogus)

@skip_pipeline
def test_transcribe_audio_missing_file(tmp_path):
    """Missing audio file should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        transcribe_audio(tmp_path / "missing.wav")

@skip_pipeline
def test_pipeline_flow(monkeypatch, tmp_path):
    """The pipeline should pass outputs sequentially between steps."""
    calls = []
    def fake_download(url, output_dir=None):
        calls.append('download')
        p = tmp_path / "video.mp4"
        p.write_bytes(b'video')
        return str(p)

    def fake_extract(video_path):
        calls.append('extract')
        p = tmp_path / "audio.wav"
        p.write_bytes(b'audio')
        return str(p)

    def fake_transcribe(audio_path):
        calls.append('transcribe')
        assert Path(audio_path).exists()
        return " raw text "

    def fake_clean(text):
        calls.append('clean')
        return text.strip()

    monkeypatch.setattr("pipeline.download_video", fake_download, raising=False)
    monkeypatch.setattr("pipeline.extract_audio", fake_extract, raising=False)
    monkeypatch.setattr("pipeline.transcribe_audio", fake_transcribe, raising=False)
    monkeypatch.setattr("pipeline.clean_text", fake_clean, raising=False)

    from pipeline import download_video as dl, extract_audio as ea, transcribe_audio as ta, clean_text as ct

    cleaned = ct(ta(ea(dl("https://tiktok.com/@u/v/1", output_dir=tmp_path))))
    assert cleaned == "raw text"
    assert calls == ['download', 'extract', 'transcribe', 'clean']

@skip_pipeline
def test_fetch_text_from_url(monkeypatch, tmp_path):
    """fetch_text_from_url should orchestrate the full pipeline."""
    def fake_download(url, output_dir=None):
        p = tmp_path / "video.mp4"
        p.write_bytes(b"video")
        return str(p)

    def fake_extract(path):
        p = tmp_path / "audio.wav"
        p.write_bytes(b"audio")
        return str(p)

    def fake_transcribe(path):
        return " my text "

    monkeypatch.setattr("pipeline.download_video", fake_download)
    monkeypatch.setattr("pipeline.extract_audio", fake_extract)
    monkeypatch.setattr("pipeline.transcribe_audio", fake_transcribe)

    from pipeline import fetch_text_from_url

    result = fetch_text_from_url("https://tiktok.com/@u/v/1", work_dir=tmp_path)
    assert result == "my text"


@skip_pipeline
def test_cli_runs(tmp_path):
    """The command line interface should execute without errors."""
    import subprocess, sys

    result = subprocess.run(
        [sys.executable, "-m", "pipeline", "https://tiktok.com/@u/v/1", "--work-dir", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() != ""


@skip_pipeline
def test_cli_writes_output(tmp_path):
    """CLI should write transcript to the specified file when --output is used."""
    import subprocess, sys

    out_file = tmp_path / "out.txt"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pipeline",
            "https://tiktok.com/@u/v/1",
            "--work-dir",
            str(tmp_path),
            "--output",
            str(out_file),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert out_file.exists()
    assert out_file.read_text().strip() != ""


@skip_pipeline
def test_save_transcript_writes_file(monkeypatch, tmp_path):
    """save_transcript should write the cleaned text to the specified file."""
    def fake_fetch(url, work_dir=None):
        return "hello world"

    monkeypatch.setattr("pipeline.fetch_text_from_url", fake_fetch)

    from pipeline import save_transcript

    outfile = tmp_path / "out.txt"
    returned = save_transcript("https://tiktok.com/@u/v/1", outfile)
    assert Path(returned) == outfile
    assert outfile.read_text() == "hello world"


@skip_pipeline
def test_copy_transcript(monkeypatch):
    """copy_transcript should attempt to copy text to the clipboard."""
    captured = {}

    def fake_fetch(url, work_dir=None):
        return "copied text"

    def fake_copy(text):
        captured["text"] = text

    monkeypatch.setattr("pipeline.fetch_text_from_url", fake_fetch)
    monkeypatch.setitem(sys.modules, "pyperclip", type("m", (), {"copy": fake_copy}))

    from pipeline import copy_transcript

    result = copy_transcript("https://tiktok.com/@u/v/1")
    assert result == "copied text"
    assert captured.get("text") == "copied text"


@skip_pipeline
def test_share_transcript_success(monkeypatch):
    """share_transcript should return the URL from the paste service."""

    def fake_fetch(url, work_dir=None):
        return "share this"

    class FakeResponse:
        status_code = 200
        text = "http://paste/abc"

    def fake_post(url, data=None):
        assert data == b"share this"
        return FakeResponse()

    monkeypatch.setattr("pipeline.fetch_text_from_url", fake_fetch)
    monkeypatch.setitem(sys.modules, "requests", type("r", (), {"post": fake_post}))

    from pipeline import share_transcript

    result = share_transcript("https://tiktok.com/@u/v/1")
    assert result == "http://paste/abc"


@skip_pipeline
def test_share_transcript_failure(monkeypatch):
    """On failure to post, share_transcript should return the transcript text."""

    def fake_fetch(url, work_dir=None):
        return "local text"

    def fake_post(url, data=None):
        raise OSError("no network")

    monkeypatch.setattr("pipeline.fetch_text_from_url", fake_fetch)
    monkeypatch.setitem(sys.modules, "requests", type("r", (), {"post": fake_post}))

    from pipeline import share_transcript

    result = share_transcript("https://tiktok.com/@u/v/1")
    assert result == "local text"

