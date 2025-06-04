# tttotext

Utilities for converting a TikTok URL into clean transcription text.

## Architecture

The pipeline consists of four stages:

1. **Video download** – `download_video` retrieves the video using `yt_dlp` and
   falls back to creating a dummy mp4 file when the dependency or network access
   is unavailable.
2. **Audio extraction** – `extract_audio` relies on `moviepy`/`ffmpeg` to pull
   audio from the downloaded video, again falling back to a placeholder file if
   extraction fails.
3. **Transcription** – `transcribe_audio` uses `speech_recognition` with the
   Google API but returns the string `"transcribed text"` when real
   transcription cannot occur.
4. **Cleaning** – `clean_text` removes filler words and extra punctuation to
   produce the final transcript.

These fallbacks allow the tests to run in environments without the optional
dependencies or internet connectivity.

## Installation

The pipeline relies on several optional libraries for downloading videos,
extracting audio, and performing speech recognition. To obtain real
transcripts, install these dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

Run the convenience function `fetch_text_from_url`:

```python
from pipeline import fetch_text_from_url

url = "https://www.tiktok.com/@example/video/1234567890"
text = fetch_text_from_url(url)
print(text)
```

### Extracting in stages

If you want to inspect each step individually, call the lower level helpers
directly:

```python
from pipeline import download_video, extract_audio, transcribe_audio, clean_text

video = download_video(url)
audio = extract_audio(video)
text = clean_text(transcribe_audio(audio))
print(text)
```

To save the transcript to a file instead of printing it, use `save_transcript`:

```python
from pipeline import save_transcript

save_transcript(url, "transcript.txt")
```

To copy the transcript to your clipboard for easy sharing, use
`copy_transcript`:

```python
from pipeline import copy_transcript

copy_transcript(url)
```

To upload the transcript to an online paste service and get a shareable URL,
call `share_transcript`:

```python
from pipeline import share_transcript

link = share_transcript(url)
print(link)
```

The pipeline attempts to download the video (via `yt_dlp`), extract audio
(`moviepy`/`ffmpeg`), and transcribe speech (`speech_recognition`). When
these dependencies or network access are unavailable, placeholder logic is used
so tests can still run offline.

You can also run the module as a script to fetch a transcript from the
command line:

```bash
python -m pipeline https://www.tiktok.com/@example/video/1234567890
```

Use `--work-dir` to specify a directory for temporary files if desired.
Pass `--output <file>` to write the transcript to a file instead of stdout.
Use `--copy` to send the transcript to the clipboard.
Use `--share` to upload the transcript online and print the resulting URL.


## Running tests

Execute the test suite with:

```bash
pytest -q
```

The repository includes over twenty tests exercising each pipeline function,
edge cases such as invalid URLs or missing files, and the command line
interface. The main suite lives in `tests/test_pipeline.py` with a second file
`tests/test_pipeline_additional.py` covering further boundary conditions.
Running the tests verifies that the offline fallbacks work as expected and that
the API remains stable. All twenty‑five tests should pass.
