BIN_DIR   = $(HOME)/.transcribeer/bin
ENTITLEMENTS = capture/capture.entitlements.plist

.PHONY: gui capture test-capture logs help

help:
	@echo "dev targets:"
	@echo "  make gui            run Python rumps menubar (uses terminal TCC)"
	@echo "  make capture        rebuild capture-bin → ~/.transcribeer/bin"
	@echo "  make test-capture   test capture-bin directly (5s recording)"
	@echo "  make logs           stream transcribeer process logs"

# ── Python menubar GUI ────────────────────────────────────────────────────────
gui:
	uv run transcribeer-gui

# ── capture-bin ───────────────────────────────────────────────────────────────
capture:
	cd capture && swift build -c release -q
	cp capture/.build/release/capture $(BIN_DIR)/capture-bin
	chmod +x $(BIN_DIR)/capture-bin
	codesign --force --sign - --entitlements $(ENTITLEMENTS) $(BIN_DIR)/capture-bin 2>/dev/null || true
	codesign --force --sign - $(BIN_DIR)/capture-bin 2>/dev/null

# ── test capture directly (terminal has TCC) ─────────────────────────────────
test-capture:
	@mkdir -p /tmp/transcribeer-test
	@echo "Recording 5s to /tmp/transcribeer-test/test.wav — press Ctrl+C to stop early"
	$(BIN_DIR)/capture-bin /tmp/transcribeer-test/test.wav 5
	@ls -lh /tmp/transcribeer-test/test.wav

# ── logs ──────────────────────────────────────────────────────────────────────
logs:
	log stream --predicate 'process == "Python" OR process == "capture-bin"' --level debug
