"""Load instrument and chord data from data/instruments/.

File structure per chord folder:
  Single voicing  → chord.wav  + chord.txt
  Multiple voicings → chord1.wav + chord1.txt, chord2.wav + chord2.txt, …

Each .txt file:
  Line 1 — voicing name  (e.g. "Open C")
  Line 2 — description   (e.g. "low E: muted, A: 3rd fret, …")
"""

from pathlib import Path

DATA_ROOT = Path(__file__).parent / "data" / "instruments"


def get_instruments() -> list[str]:
    if not DATA_ROOT.exists():
        return []
    return sorted(p.name for p in DATA_ROOT.iterdir() if p.is_dir())


def _chord_dir(instrument: str, note_name: str, chord_type: str) -> Path:
    return DATA_ROOT / instrument / f"{note_name} {chord_type}"


def _read_txt(path: Path) -> tuple[str, str]:
    """Return (name, description) from a voicing txt file."""
    lines = path.read_text(encoding="utf-8").splitlines()
    name = lines[0].strip() if lines else ""
    desc = lines[1].strip() if len(lines) > 1 else ""
    return name, desc


def get_chord_wav(instrument: str, note_name: str, chord_type: str) -> Path | None:
    """Return chord.wav for a single-voicing chord, or None."""
    p = _chord_dir(instrument, note_name, chord_type) / "chord.wav"
    return p if p.exists() else None


def get_voicings(
    instrument: str, note_name: str, chord_type: str
) -> list[tuple[str, str, Path | None]] | None:
    """
    Return list of (name, description, wav_path_or_None) for all voicings.
    Returns None if no fingering data exists.
    """
    cd = _chord_dir(instrument, note_name, chord_type)
    if not cd.exists():
        return None

    # Multiple voicings: chord1.txt, chord2.txt, …
    if (cd / "chord1.txt").exists():
        result = []
        i = 1
        while True:
            txt = cd / f"chord{i}.txt"
            if not txt.exists():
                break
            wav = cd / f"chord{i}.wav"
            name, desc = _read_txt(txt)
            result.append((name, desc, wav if wav.exists() else None))
            i += 1
        return result or None

    # Single voicing: chord.txt
    txt = cd / "chord.txt"
    if txt.exists():
        name, desc = _read_txt(txt)
        wav = cd / "chord.wav"
        return [(name, desc, wav if wav.exists() else None)]

    return None
