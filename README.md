# transcribeer

macOS audio capture, transcription, and summarization — CLI-first, Hebrew + English.

Captures both sides of a call via system audio (SCStream), transcribes with faster-whisper, optionally diarizes speakers, and summarizes with an LLM.

---

## Requirements

- macOS 13 (Ventura) or later, Apple Silicon (arm64)
- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- ffmpeg (`brew install ffmpeg`)

---

## Install

```bash
git clone https://github.com/your-org/transcribeer
cd transcribeer
bash install.sh
```

The installer will:
1. Check macOS version and architecture
2. Install ffmpeg if missing (via Homebrew)
3. Place `capture-bin` in `~/.transcribeer/bin/`
4. Create a Python venv at `~/.transcribeer/venv/`
5. Ask which diarization backend to install:
   - **pyannote** — best quality, requires a HuggingFace account and token
   - **resemblyzer** — no account needed, good quality
   - **none** — no speaker labels, fastest
6. Write a default config to `~/.transcribeer/config.toml`
7. Symlink `transcribeer` into `~/.local/bin/`

---

## Usage

### One-shot: record → transcribe → summarize

```bash
transcribeer run
# or with a time limit:
transcribeer run --duration 300   # auto-stop after 5 minutes
```

Press `Ctrl+C` to stop recording. Transcription and summarization run automatically.

Output saved to `~/.transcribeer/sessions/YYYY-MM-DD-HHMM/`:
- `audio.wav`
- `transcript.txt`
- `summary.md`

### Record only

```bash
transcribeer record                     # stop with Ctrl+C
transcribeer record --duration 60       # stop after 60 seconds
transcribeer record --out /tmp/call.wav # custom output path
```

macOS will prompt for **Screen & System Audio Recording** permission on first run.

### Transcribe an existing file

```bash
transcribeer transcribe call.wav
transcribeer transcribe call.wav --lang he          # force Hebrew
transcribeer transcribe call.wav --no-diarize       # skip speaker labels
transcribeer transcribe call.wav --out call.txt     # custom output path
```

Supported languages: `he` (Hebrew), `en` (English), `auto` (detect).

Output format:
```
[00:00 -> 00:08] Speaker 1: שלום, איך אתה?
[00:09 -> 00:15] Speaker 2: בסדר גמור, תודה.
```

### Summarize a transcript

```bash
transcribeer summarize call.txt
transcribeer summarize call.txt --backend openai    # override LLM backend
transcribeer summarize call.txt --out call.md       # custom output path
```

---

## Configuration

`~/.transcribeer/config.toml` is written by the installer. Edit it to change defaults:

```toml
[transcription]
language = "auto"          # auto, he, en
diarization = "resemblyzer" # pyannote, resemblyzer, none
num_speakers = 0           # 0 = auto-detect

[summarization]
backend = "ollama"         # ollama, openai, anthropic
model = "llama3"
ollama_host = "http://localhost:11434"

[paths]
sessions_dir = "~/.transcribeer/sessions"
capture_bin = "~/.transcribeer/bin/capture-bin"
```

### LLM backends

| Backend | Setup |
|---|---|
| `ollama` | Run [Ollama](https://ollama.ai) locally with a model pulled (`ollama pull llama3`) |
| `openai` | Set `OPENAI_API_KEY` in your environment |
| `anthropic` | Set `ANTHROPIC_API_KEY` in your environment |

---

## Models

| Component | Model |
|---|---|
| Transcription | `ivrit-ai/whisper-large-v3-turbo-ct2` (via faster-whisper) |
| Diarization (pyannote) | `ivrit-ai/pyannote-speaker-diarization-3.1` |

Models are downloaded from HuggingFace on first use and cached at `~/.cache/huggingface/`.

---

## Permission

On first `transcribeer record` or `transcribeer run`, macOS will request **Screen & System Audio Recording** permission. Grant it in **System Settings → Privacy & Security → Screen & System Audio Recording**.

---

## Development

```bash
git clone https://github.com/your-org/transcribeer
cd transcribeer
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```
