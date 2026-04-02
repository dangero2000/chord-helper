# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the app
uv run python main.py

# Populate instrument data (run once before launching, safe to re-run)
uv run python generate_data.py

# Build standalone executable
uv run python -m nuitka --standalone --onefile main.py
```

## Architecture

The app is a Pygame GUI with no traditional UI widgets. A single window captures keyboard events and routes them to action functions. All user feedback goes through two channels: the Pygame window (visual) and Prism (screen reader/TTS via `prismatoid`).

**Data flow at runtime:**

1. `main.py` holds all application state as module-level globals (`note_idx`, `chord_type_idx`, `instrument_idx`, `in_submenu`, etc.) and maps pygame key events to action functions.
2. `data_loader.py` resolves the current chord to files under `data/instruments/{instrument}/{note} {chord type}/` and returns voicing tuples of `(name, description, wav_path)`.
3. `audio.py` plays either a WAV file from disk (`play_wav`) or a synthesized chord (`play_chord`) via `sounddevice`. Synthesis uses additive harmonics with ADSR envelopes; instrument timbre is defined by `INSTRUMENT_HARMONICS` and `INSTRUMENT_ADSR` dicts.
4. `accessibility.py` wraps Prism (`prism.Context` -> `create_best()` -> `output()`). It degrades silently if no screen reader is present.

**Instrument discovery:** `data_loader.get_instruments()` scans `data/instruments/` for subfolders. The instrument list in the app is whatever folders exist there, with the built-in synthesis names (`audio.INSTRUMENTS`) as a fallback if the folder is empty.

**Voicing file convention:**
- Single voicing: `chord.wav` + `chord.txt`
- Multiple voicings: `chord1.wav` + `chord1.txt`, `chord2.wav` + `chord2.txt`, ...
- Each `.txt`: line 1 is the voicing name, line 2 is the description.

**Submenu state:** `in_submenu` is a module-level bool. While true, Up/Down navigate `submenu_items` (a list of voicing tuples), Enter plays the selected voicing's WAV, Space reads its fingering text, and Escape returns to the main view. Most other keys are ignored.

**`generate_data.py`** is a standalone script (not imported by the app) that synthesises all chord WAVs and writes all fingering TXTs. It never overwrites existing files, so custom replacements are preserved across runs. Piano voicings include three inversions with distinct audio (lowest notes shifted up an octave). Guitar and ukulele voicings come from the dicts in `chord_data.py`.

## Versioning and commits

Releases are created automatically by `.github/workflows/release.yml` on every push to `main`. The workflow reads the commit message to determine whether and how to bump the version. Commits that don't match any prefix are pushed normally but do not produce a release.

| Prefix | Effect | Example |
|--------|--------|---------|
| `feat:` | Minor bump (`0.1` → `0.2`) | `feat: add mandolin instrument` |
| `fix:` | Patch bump (`0.2` → `0.2.1`) | `fix: correct E minor guitar voicing` |
| `breaking:` | Major bump (`0.2` → `1.0`) | `breaking: restructure data folder format` |
| anything else | No release | `docs: update README` |

The patch component is dropped when it is zero (`1.1.0` is tagged and displayed as `1.1`).

When writing commits, use the appropriate prefix whenever the change is user-facing. Use unprefixed messages for things like documentation edits, internal refactors, or CI changes that don't affect behaviour.
