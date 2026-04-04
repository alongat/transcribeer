# Custom Prompt Profiles — Design Spec

Date: 2026-04-04

## Overview

Add support for user-defined summarization prompt profiles. The hardcoded `SYSTEM_PROMPT` remains the default and fallback. Users drop `.md` files into `~/.transcribeer/prompts/` to define named profiles and choose one per session via the menubar, history window, or CLI flags.

---

## 1. Profile Storage & Loading

**Location:** `~/.transcribeer/prompts/<name>.md`

- Filename (minus `.md`) is the profile name (e.g., `1on1.md` → profile `"1on1"`).
- No subdirectories.
- A `default.md` is optional — if absent, the hardcoded `SYSTEM_PROMPT` is used.

**New module: `transcribeer/prompts.py`**

```python
def list_profiles() -> list[str]:
    """Scan ~/.transcribeer/prompts/, return sorted names. Always includes 'default' first."""

def load_prompt(name: str | None) -> str:
    """Load prompt text for `name`. None or 'default' with no file → SYSTEM_PROMPT."""
```

**`summarize.run()` signature change:**

```python
def run(transcript, backend, model, ollama_host, prompt: str | None = None) -> str:
```

`None` → uses `SYSTEM_PROMPT`. No regression for existing callers.

---

## 2. Config

New field in `[summarization]` section of `~/.transcribeer/config.toml`:

```toml
[summarization]
prompt_on_stop = true   # show profile picker when stopping recording
```

- `Config` dataclass gains `prompt_on_stop: bool = True`.
- No `default_profile` persisted — profile selection is per-session and transient.

---

## 3. GUI — Menubar

**New menu item:** `"Prompt: Default"` appears during an active session alongside `"✏️ Rename Session…"`.

- Clicking opens a `rumps.Window` picker listing available profiles (same UX pattern as rename).
- `TranscribeerApp` gains `self._prompt_profile: str | None` (reset to `None` on each new session).
- Title updates to reflect selection: `"Prompt: 1on1"`, `"Prompt: Default"`, etc.
- Hidden when idle (no active session).

**On stop behavior:**

- If `cfg.prompt_on_stop is True` AND `list_profiles()` returns any custom profiles (more than just `"default"`), a picker dialog pops up automatically after `_on_stop` is triggered, before the pipeline continues.
- If the user cancels the picker, the default prompt is used (no blocking).
- Threading: the picker runs on the main thread (`_on_stop`) and sets `self._prompt_profile` before or during transcription. The `_run()` background thread reads the value when it reaches the summarize step — safe because transcription is the time bottleneck.

---

## 4. GUI — History Window

**Profile picker in WebView:**

- `on_load` sends a new `"profiles"` message to the frontend with `list_profiles()` result.
- The HTML summary action area gains a `<select>` dropdown for profile selection.
- `action == "summarize"` payload gains optional `"profile": str` key.
- `_run_summarize(sess, profile=None)` passes the prompt through to `sm.run()`.

---

## 5. CLI

**`summarize` command:**

```
--profile <name>      Named profile from ~/.transcribeer/prompts/
--prompt-file <path>  One-off prompt file (takes precedence over --profile)
```

**`run` command (record+transcribe+summarize):**

```
--profile <name>      Named profile (no --prompt-file; pipeline doesn't do file-picking)
```

Omitting both = default prompt. No regression.

---

## Files to Touch

| File | Change |
|------|--------|
| `transcribeer/prompts.py` | **New** — `list_profiles()`, `load_prompt()` |
| `transcribeer/summarize.py` | Add `prompt` param to `run()` and each `_run_*` helper |
| `transcribeer/config.py` | Add `prompt_on_stop` field + default + TOML serialization |
| `transcribeer/cli.py` | `--profile` / `--prompt-file` flags on `summarize`; `--profile` on `run` |
| `transcribeer/gui.py` | `_prompt_profile` state, "Prompt" menu item, on-stop picker |
| `transcribeer/history_window.py` | Send profiles on load; pass profile to `_run_summarize` |
| HTML/JS (history WebView) | Profile `<select>` dropdown in summarize action |
