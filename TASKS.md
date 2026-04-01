# Transcribee Tasks

## Backlog

### Settings Page
Build a native macOS settings window (accessible from the menubar) to configure the app without manually editing `~/.transcribee/config.toml`.

**Pipeline mode**
- Toggle: record-only vs. record + transcribe vs. record + transcribe + summarize
- Affects which post-processing steps run after a session ends

**Transcription settings**
- Language (default: auto)
- Diarization backend (resemblyzer / off)
- Number of speakers (0 = auto)

**Summarization / LLM settings**
- Backend selector: `ollama` | `openai` | `anthropic` (others TBD)
- Model name (free-text or dropdown per backend)
- Ollama host URL (default: `http://localhost:11434`)
- API key fields for cloud backends (stored securely in macOS Keychain, not in the config file)

**Persistence**
- Reads from / writes to `~/.transcribee/config.toml`
- API keys → macOS Keychain (`transcribee/<backend>`)
- Live reload: app picks up changes without restart

---

### History Page
Build a native macOS window to browse and manage past sessions.

**Session list (left panel)**
- List all sessions from `~/.transcribee/sessions/`, sorted by date descending
- Show date/time, user-defined name (if set), tags, and status badges (has audio / transcript / summary)
- Search / filter by name, tag, or date range

**Session metadata**
- Editable name (stored in `meta.json` alongside `audio.wav` / `transcript.txt` / `summary.md`)
- Tags/labels (free-form, multi-value)
- Duration (derived from audio file)

**Session detail (right panel)**
- Timestamp and duration header
- Transcript viewer — scrollable, speaker-labeled segments
- Summary viewer — rendered markdown; shows placeholder if not yet generated
- Ad-hoc actions:
  - **Transcribe now** — runs transcription pipeline on `audio.wav` (if transcript missing or user wants to re-run)
  - **Summarize now** — runs summarization on existing transcript (if summary missing or user wants to re-run)
  - Both actions show inline progress and update the view on completion

**Implementation notes**
- `meta.json` schema: `{ "name": str, "tags": [str] }` — created lazily on first edit
- Native window via `AppKit` / `rumps` or a lightweight `webview` panel (TBD)
- Reuse `transcribe.run()` and `summarize.run()` for ad-hoc actions

---

### Session Naming
Allow users to give sessions a human-readable name, either upfront or after the fact.

**At recording start**
- Menubar "Start recording" triggers a small prompt dialog asking for an optional name
- If left blank, session keeps the timestamp directory name as display name
- Name is written immediately to `meta.json` in the new session dir

**After the fact (via History page)**
- Inline editable name field in the session detail panel (see History Page task)
- Edit saves to `meta.json`

**Implementation notes**
- `meta.json` is the single source of truth for name (and tags)
- Directory name stays as `YYYY-MM-DD-HHMM` — only the display name changes
- All places that show a session title should prefer `meta.name` and fall back to the dir name

---

<!-- add more tasks below -->
