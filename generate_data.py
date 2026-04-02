"""Generate all chord WAV and TXT files under data/instruments/.

Run once to populate, or re-run to fill in missing files (existing files are
never overwritten, so custom replacements stay safe):

    uv run python generate_data.py

File structure written:
  Single voicing  → chord.wav  + chord.txt
  Multiple voicings → chord1.wav + chord1.txt, chord2.wav + chord2.txt, …

Each .txt:
  Line 1 — voicing name
  Line 2 — description
"""

import wave
from pathlib import Path

import numpy as np

from audio import INSTRUMENT_HARMONICS, INSTRUMENT_ADSR, _adsr_envelope, _midi_to_hz
from chord_data import (
    NOTES, NOTE_SYMBOLS, CHORD_TYPES,
    GUITAR_VOICINGS, guitar_voicing_description,
    UKULELE_VOICINGS, ukulele_voicing_description,
    chord_note_names,
)

DATA_ROOT = Path(__file__).parent / "data" / "instruments"

INSTRUMENT_DEFS = [
    ("piano",   "Piano"),
    ("guitar",  "Guitar"),
    ("Ukulele", "Ukulele"),
    ("Organ",   "Organ"),
    ("Harp",    "Harp"),
    ("Banjo",   "Banjo"),
]

GEN_SAMPLE_RATE   = 22050
GEN_DURATION      = 2.0
STRUM_INSTRUMENTS = {"Guitar", "Ukulele", "Banjo", "Harp"}


# ── Audio ─────────────────────────────────────────────────────────────────────

def _synth_chord(root_idx: int, intervals: list[int], synth_key: str,
                 interval_offsets: list[int] | None = None) -> np.ndarray:
    """
    Synthesise a chord. interval_offsets lets individual notes be shifted by
    extra semitones (used for piano inversions).
    """
    harmonics   = INSTRUMENT_HARMONICS.get(synth_key, INSTRUMENT_HARMONICS["Piano"])
    adsr        = INSTRUMENT_ADSR.get(synth_key, INSTRUMENT_ADSR["Piano"])
    strum_delay = 0.03 if synth_key in STRUM_INSTRUMENTS else 0.0

    offsets = interval_offsets or ([0] * len(intervals))
    n_total = int(GEN_SAMPLE_RATE * (GEN_DURATION + strum_delay * len(intervals)))
    mix     = np.zeros(n_total)
    midi_base = 60 + root_idx  # C4

    for i, (interval, extra) in enumerate(zip(intervals, offsets)):
        freq   = _midi_to_hz(midi_base + interval + extra)
        n_tone = int(GEN_SAMPLE_RATE * GEN_DURATION)
        t      = np.linspace(0, GEN_DURATION, n_tone, endpoint=False)

        wave_data = np.zeros(n_tone)
        for harmonic, amp in harmonics:
            h_freq = freq * harmonic
            if h_freq < GEN_SAMPLE_RATE / 2:
                wave_data += amp * np.sin(2 * np.pi * h_freq * t)
        peak = np.max(np.abs(wave_data))
        if peak > 0:
            wave_data /= peak

        env  = _adsr_envelope(n_tone, adsr[0], adsr[1], 0.6, adsr[3],
                               sample_rate=GEN_SAMPLE_RATE)
        tone = wave_data * env

        offset = int(i * strum_delay * GEN_SAMPLE_RATE)
        end    = offset + len(tone)
        if end <= n_total:
            mix[offset:end] += tone
        else:
            mix[offset:] += tone[:n_total - offset]

    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.8
    return mix.astype(np.float32)


def _save_wav(path: Path, samples: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    int16 = np.clip(samples * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(GEN_SAMPLE_RATE)
        f.writeframes(int16.tobytes())


def _write_txt(path: Path, name: str, desc: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{name}\n{desc}", encoding="utf-8")


# ── Voicing data ──────────────────────────────────────────────────────────────

def _piano_voicings(note_idx: int, intervals: list[int]) -> list[tuple[str, str, list[int]]]:
    """Return (name, description, interval_offsets) for each piano inversion."""
    n = len(intervals)
    note_names = chord_note_names(note_idx, intervals)
    result = []

    # Root position — no shifts
    result.append((
        "Root position",
        "Play: " + ", ".join(note_names),
        [0] * n,
    ))
    # First inversion — move lowest note up an octave
    if n >= 3:
        inv1_offsets = [12] + [0] * (n - 1)
        inv1_names   = note_names[1:] + [note_names[0] + " (octave up)"]
        result.append((
            "First inversion",
            "Play: " + ", ".join(inv1_names),
            inv1_offsets,
        ))
    # Second inversion — move two lowest notes up an octave
    if n >= 3:
        inv2_offsets = [12, 12] + [0] * (n - 2)
        inv2_names   = note_names[2:] + [note_names[0] + " (octave up)",
                                          note_names[1] + " (octave up)"]
        result.append((
            "Second inversion",
            "Play: " + ", ".join(inv2_names),
            inv2_offsets,
        ))
    return result


def _guitar_voicings(note_sym: str, chord_type: str) -> list[tuple[str, str]] | None:
    raw = GUITAR_VOICINGS.get((note_sym, chord_type))
    if not raw:
        return None
    return [(label, guitar_voicing_description(frets)) for label, frets in raw]


def _ukulele_voicings(note_sym: str, chord_type: str) -> list[tuple[str, str]] | None:
    raw = UKULELE_VOICINGS.get((note_sym, chord_type))
    if not raw:
        return None
    return [(label, ukulele_voicing_description(frets)) for label, frets in raw]


# ── Generator ─────────────────────────────────────────────────────────────────

def _find_or_create_dir(folder_name: str) -> Path:
    """Case-insensitive match against existing dirs; create if absent."""
    if DATA_ROOT.exists():
        for p in DATA_ROOT.iterdir():
            if p.is_dir() and p.name.lower() == folder_name.lower():
                return p
    d = DATA_ROOT / folder_name
    d.mkdir(parents=True, exist_ok=True)
    return d


def generate():
    total = len(NOTES) * len(CHORD_TYPES)
    print(f"Generating {len(INSTRUMENT_DEFS)} instruments × {total} chords each")
    print(f"Output: {DATA_ROOT}\n")

    for folder_name, synth_key in INSTRUMENT_DEFS:
        inst_dir = _find_or_create_dir(folder_name)
        print(f"  [{synth_key}]  →  {inst_dir.name}/")
        done = 0

        for note_idx, (note_name, note_sym) in enumerate(zip(NOTES, NOTE_SYMBOLS)):
            for chord_type, intervals in CHORD_TYPES:
                chord_dir = inst_dir / f"{note_name} {chord_type}"
                chord_dir.mkdir(parents=True, exist_ok=True)

                # ── Gather voicing list for this instrument ────────────────
                if synth_key == "Piano":
                    pv = _piano_voicings(note_idx, intervals)
                    # pv: list of (name, desc, offsets)
                    voicings_named = [(name, desc) for name, desc, _ in pv]
                    voicings_offsets = [offs for _, _, offs in pv]
                elif synth_key == "Guitar":
                    gv = _guitar_voicings(note_sym, chord_type)
                    voicings_named   = gv if gv else None
                    voicings_offsets = [[0]*len(intervals)] * len(gv) if gv else None
                elif synth_key == "Ukulele":
                    uv = _ukulele_voicings(note_sym, chord_type)
                    voicings_named   = uv if uv else None
                    voicings_offsets = [[0]*len(intervals)] * len(uv) if uv else None
                else:
                    voicings_named   = None
                    voicings_offsets = None

                # ── Write files ───────────────────────────────────────────
                if voicings_named and len(voicings_named) == 1:
                    # Single voicing → chord.wav + chord.txt
                    wav_path = chord_dir / "chord.wav"
                    txt_path = chord_dir / "chord.txt"
                    if not wav_path.exists():
                        samples = _synth_chord(note_idx, intervals, synth_key,
                                               voicings_offsets[0])
                        _save_wav(wav_path, samples)
                    if not txt_path.exists():
                        name, desc = voicings_named[0]
                        _write_txt(txt_path, name, desc)

                elif voicings_named and len(voicings_named) > 1:
                    # Multiple voicings → chord1.wav + chord1.txt, …
                    for i, ((name, desc), offsets) in enumerate(
                        zip(voicings_named, voicings_offsets), start=1
                    ):
                        wav_path = chord_dir / f"chord{i}.wav"
                        txt_path = chord_dir / f"chord{i}.txt"
                        if not wav_path.exists():
                            samples = _synth_chord(note_idx, intervals, synth_key,
                                                   offsets)
                            _save_wav(wav_path, samples)
                        if not txt_path.exists():
                            _write_txt(txt_path, name, desc)

                else:
                    # No voicing data — audio only, no fingering
                    wav_path = chord_dir / "chord.wav"
                    if not wav_path.exists():
                        samples = _synth_chord(note_idx, intervals, synth_key)
                        _save_wav(wav_path, samples)

                done += 1
                if done % 50 == 0:
                    print(f"    {done}/{total}")

        print(f"    {total}/{total} done")

    print("\nDone. Existing files were never overwritten.")
    print("To customise: replace any chord.wav / chord.txt (or chord1.*, chord2.*, …).")
    print("To add an instrument: create a subfolder in data/instruments/ with the same structure.")


if __name__ == "__main__":
    generate()
