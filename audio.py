"""Chord audio synthesis using additive synthesis."""

import threading
import wave as wave_mod
from pathlib import Path

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 44100
_playback_lock = threading.Lock()


# MIDI note 60 = middle C (C4) = 261.63 Hz
def _midi_to_hz(midi_note: int) -> float:
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


# Instrument tone shapers: returns a normalized amplitude envelope per harmonic.
# Each entry is a list of (harmonic_number, relative_amplitude).
INSTRUMENT_HARMONICS = {
    "Piano": [
        (1, 1.0), (2, 0.5), (3, 0.25), (4, 0.15), (5, 0.1),
        (6, 0.07), (7, 0.05), (8, 0.04),
    ],
    "Guitar": [
        (1, 1.0), (2, 0.6), (3, 0.3), (4, 0.15), (5, 0.08), (6, 0.04),
    ],
    "Ukulele": [
        (1, 1.0), (2, 0.4), (3, 0.15), (4, 0.06),
    ],
    "Organ": [
        (1, 1.0), (2, 1.0), (3, 0.8), (4, 0.6), (5, 0.4), (6, 0.2),
    ],
    "Harp": [
        (1, 1.0), (2, 0.7), (3, 0.4), (4, 0.2), (5, 0.1),
    ],
    "Banjo": [
        (1, 1.0), (2, 0.8), (3, 0.5), (4, 0.3), (5, 0.2), (6, 0.1), (7, 0.05),
    ],
}

# Attack/decay/sustain/release parameters (seconds)
INSTRUMENT_ADSR = {
    "Piano":   (0.005, 0.3,  0.4, 0.4),
    "Guitar":  (0.005, 0.15, 0.3, 0.5),
    "Ukulele": (0.005, 0.1,  0.3, 0.3),
    "Organ":   (0.02,  0.0,  1.0, 0.05),
    "Harp":    (0.005, 0.2,  0.2, 0.6),
    "Banjo":   (0.003, 0.1,  0.2, 0.3),
}

INSTRUMENTS = list(INSTRUMENT_HARMONICS.keys())


def _adsr_envelope(n_samples: int, attack: float, decay: float, sustain_level: float, release: float, sample_rate: int | None = None) -> np.ndarray:
    sr = sample_rate if sample_rate is not None else SAMPLE_RATE
    a_samples = int(attack * sr)
    d_samples = int(decay * sr)
    r_samples = int(release * sr)
    s_samples = max(0, n_samples - a_samples - d_samples - r_samples)

    env = np.zeros(n_samples)
    # Attack
    end_a = min(a_samples, n_samples)
    env[:end_a] = np.linspace(0, 1, end_a)
    # Decay
    end_d = min(end_a + d_samples, n_samples)
    env[end_a:end_d] = np.linspace(1, sustain_level, end_d - end_a)
    # Sustain
    end_s = min(end_d + s_samples, n_samples)
    env[end_d:end_s] = sustain_level
    # Release
    env[end_s:] = np.linspace(sustain_level, 0, n_samples - end_s)
    return env


def _synthesize_tone(freq: float, duration: float, harmonics: list, adsr: tuple) -> np.ndarray:
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    wave = np.zeros(n)
    for harmonic, amp in harmonics:
        h_freq = freq * harmonic
        if h_freq < SAMPLE_RATE / 2:  # Nyquist check
            wave += amp * np.sin(2 * np.pi * h_freq * t)
    # Normalize
    peak = np.max(np.abs(wave))
    if peak > 0:
        wave /= peak
    attack, decay, sustain_ratio, release = adsr
    envelope = _adsr_envelope(n, attack, decay, 0.6, release)
    return wave * envelope


def play_chord(root_idx: int, intervals: list[int], instrument: str, duration: float = 2.0):
    """Play a chord asynchronously. Stops any currently playing sound."""
    harmonics = INSTRUMENT_HARMONICS.get(instrument, INSTRUMENT_HARMONICS["Piano"])
    adsr = INSTRUMENT_ADSR.get(instrument, INSTRUMENT_ADSR["Piano"])

    # Build chord as a mix of tones, each note staggered slightly for guitar/banjo/harp
    strum_instruments = {"Guitar", "Ukulele", "Banjo", "Harp"}
    strum_delay = 0.03 if instrument in strum_instruments else 0.0

    n_total = int(SAMPLE_RATE * (duration + strum_delay * len(intervals)))
    mix = np.zeros(n_total)

    # Root note starts at octave 4 (MIDI 60 = C4)
    midi_base = 60 + root_idx  # C4 + root offset

    for i, interval in enumerate(intervals):
        midi_note = midi_base + interval
        freq = _midi_to_hz(midi_note)
        tone = _synthesize_tone(freq, duration, harmonics, adsr)
        offset = int(i * strum_delay * SAMPLE_RATE)
        end = offset + len(tone)
        if end <= n_total:
            mix[offset:end] += tone
        else:
            mix[offset:] += tone[:n_total - offset]

    # Normalize mix
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.8

    mix = mix.astype(np.float32)

    def _play():
        with _playback_lock:
            sd.play(mix, SAMPLE_RATE)
            sd.wait()

    t = threading.Thread(target=_play, daemon=True)
    t.start()


def play_wav(path) -> bool:
    """Play a WAV file asynchronously. Returns False if the file can't be read."""
    try:
        with wave_mod.open(str(path), "rb") as f:
            n_channels  = f.getnchannels()
            sample_rate = f.getframerate()
            raw         = f.readframes(f.getnframes())
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if n_channels > 1:
            samples = samples.reshape(-1, n_channels)
    except Exception:
        return False

    def _play():
        with _playback_lock:
            sd.play(samples, sample_rate)
            sd.wait()

    threading.Thread(target=_play, daemon=True).start()
    return True


def stop_audio():
    sd.stop()
