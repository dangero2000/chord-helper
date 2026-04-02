# DISCLAIMER

Currently, a majority of the program and documentation are written by Claude Code. As such, there might be some bugs and inconsistancies. Issue and pull request submitions are always welcome.

# Chord Helper

An accessible chord reference app. Browse every chord across multiple instruments, hear how each one sounds, and get fingering instructions for guitar, ukulele, and piano.

Screen reader support is provided through [Prism](https://github.com/ethindp/prism) via the [prismatoid](https://pypi.org/project/prismatoid/) Python bindings. All navigation is keyboard-driven and every action is announced to the active screen reader or TTS backend automatically.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management

## Building

Install dependencies:

```
uv sync
```

To build a standalone executable with Nuitka:

```
uv run python -m nuitka --standalone --onefile main.py
```

The output binary will be named `chords` (or `chords.exe` on Windows).

## Generating instrument data

The app loads chord audio and fingering text from `data/instruments/`. Run the generator once before launching:

```
uv run python generate_data.py
```

This creates a WAV file and a TXT file for every chord across all included instruments. It will never overwrite files that already exist, so any custom replacements you have added are safe.

## Running

```
uv run python main.py
```

## Usage

### Navigation

| Key | Action |
|-----|--------|
| Left / Right arrow | Move to the previous or next root note |
| A, B, C, D, E, F, G | Jump directly to that root note |
| Up / Down arrow | Move to the previous or next chord type |
| Home | Jump to the first chord type |
| End | Jump to the last chord type |
| Page Up / Page Down | Switch to the previous or next instrument |
| Enter | Play the chord, or open the voicings menu if multiple voicings exist |
| Space | Read the fingering, or open the voicings menu if multiple voicings exist |
| H | Hear a description of all key bindings |
| Escape | Close the voicings menu, or quit |

### Voicings menu

When a chord has more than one voicing (for example, open position versus barre), pressing Enter or Space opens a menu listing each one. Inside the menu:

| Key | Action |
|-----|--------|
| Up / Down arrow | Move between voicings |
| Enter | Play the selected voicing |
| Space | Read the fingering for the selected voicing |
| Escape | Close the menu and return to the main view |

## Adding instruments and custom sounds

The `data/instruments/` folder contains one subfolder per instrument. Each chord gets its own subfolder named `{note} {chord type}` (for example, `C major` or `A sharp minor`).

Inside a chord folder:

- **Single voicing:** `chord.wav`/`chord.txt`
- **Multiple voicings:** `chord1.wav`/`chord1.txt`, `chord2.wav`/`chord2.txt`, and so on

Each `.txt` file has two lines: the voicing name on the first line and the fingering description on the second.

To replace a generated sound with a recording, drop a new `chord.wav` (or `chord1.wav`, etc.) in the appropriate folder. The generator will not overwrite it on future runs.

To add a new instrument entirely, create a subfolder under `data/instruments/` with the instrument name, then populate it with the same chord folder structure. The app discovers instruments from that folder automatically, so no code changes are needed.

## Contributing

Contributions are welcome. The most impactful thing the community can do is replace the synthesized WAV files with real recordings, so the app is genuinely useful for learning what chords are supposed to sound like. See the section above for how the file structure works.

# DISCLAIMER

Currently, a majority of the program and documentation are written by Claude Code. As such, there might be some bugs and inconsistancies. Issue and pull request submitions are always welcome.
