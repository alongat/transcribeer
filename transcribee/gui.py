"""macOS menubar GUI using rumps."""
from __future__ import annotations

import signal
import subprocess
import threading
from pathlib import Path

import rumps

from transcribee.config import load


class TranscribeeApp(rumps.App):
    def __init__(self):
        super().__init__("🎙", quit_button="Quit")
        self.cfg = load()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._capture_proc: subprocess.Popen | None = None
        self.menu = ["Start Recording"]

    # ── Menu actions ──────────────────────────────────────────────────────────

    @rumps.clicked("Start Recording")
    def toggle(self, sender):
        if self._thread and self._thread.is_alive():
            self._stop()
        else:
            self._start()

    def _start(self):
        self._stop_event.clear()
        self.menu["Start Recording"].title = "⏹ Stop Recording"
        self.title = "⏺"
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _stop(self):
        self._stop_event.set()
        proc = self._capture_proc
        if proc:
            proc.send_signal(signal.SIGINT)

    # ── Pipeline (background thread) ─────────────────────────────────────────

    def _run(self):
        from transcribee import session, transcribe as tx, summarize as sm

        cfg = self.cfg
        sess = session.new_session(cfg.sessions_dir)
        audio_path = sess / "audio.wav"
        transcript_path = sess / "transcript.txt"
        summary_path = sess / "summary.md"

        # 1. Record
        try:
            self._capture_proc = subprocess.Popen(
                [str(cfg.capture_bin), str(audio_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _, stderr = self._capture_proc.communicate()
            rc = self._capture_proc.returncode
            self._capture_proc = None

            if rc != 0 and not self._stop_event.is_set():
                err = stderr.decode("utf-8", errors="replace")
                if "Screen & System Audio Recording" in err:
                    return self._set_error("Grant Screen Recording in System Settings → Privacy")
                return self._set_error(f"capture-bin exited {rc}")

            if not audio_path.exists() or audio_path.stat().st_size == 0:
                self._reset_button()
                self.title = "🎙"
                return
        except Exception as e:
            return self._set_error(str(e))

        # 2. Transcribe
        self.title = "📝"
        try:
            tx.run(
                audio_path=audio_path,
                language=cfg.language,
                diarize_backend=cfg.diarization,
                num_speakers=cfg.num_speakers,
                out_path=transcript_path,
            )
        except Exception as e:
            return self._set_error(f"Transcription failed: {e}")

        # 3. Summarize (best-effort)
        self.title = "🤔"
        try:
            summary = sm.run(
                transcript=transcript_path.read_text(encoding="utf-8"),
                backend=cfg.llm_backend,
                model=cfg.llm_model,
                ollama_host=cfg.ollama_host,
            )
            summary_path.write_text(summary, encoding="utf-8")
        except Exception:
            pass

        self._set_done(sess)

    # ── State helpers ─────────────────────────────────────────────────────────

    def _reset_button(self):
        item = self.menu.get("⏹ Stop Recording") or self.menu.get("Start Recording")
        if item:
            item.title = "Start Recording"

    def _set_done(self, sess: Path):
        self._reset_button()
        self.title = "✓"
        rumps.notification("Transcribee", "Done", str(sess), sound=False)
        # Replace stale "Open Session" if present, then prepend fresh one
        if "Open Session" in self.menu:
            del self.menu["Open Session"]
        open_item = rumps.MenuItem(
            "Open Session",
            callback=lambda _: subprocess.run(["open", str(sess)]),
        )
        self.menu.insert_before("Start Recording", open_item)

    def _set_error(self, msg: str):
        self._reset_button()
        self.title = "⚠"
        rumps.alert(title="Transcribee Error", message=msg)


def main():
    TranscribeeApp().run()


if __name__ == "__main__":
    main()
