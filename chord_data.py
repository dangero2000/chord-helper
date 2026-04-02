"""Chord definitions, voicings, and fingering data."""

NOTES = ["C", "C sharp", "D", "D sharp", "E", "F", "F sharp", "G", "G sharp", "A", "A sharp", "B"]
NOTE_SYMBOLS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Chord types: (display name, intervals from root in semitones)
CHORD_TYPES = [
    ("major",           [0, 4, 7]),
    ("minor",           [0, 3, 7]),
    ("diminished",      [0, 3, 6]),
    ("augmented",       [0, 4, 8]),
    ("suspended 2",     [0, 2, 7]),
    ("suspended 4",     [0, 5, 7]),
    ("dominant 7th",    [0, 4, 7, 10]),
    ("major 7th",       [0, 4, 7, 11]),
    ("minor 7th",       [0, 3, 7, 10]),
    ("minor major 7th", [0, 3, 7, 11]),
    ("half diminished", [0, 3, 6, 10]),
    ("diminished 7th",  [0, 3, 6, 9]),
    ("augmented 7th",   [0, 4, 8, 10]),
    ("dominant 9th",    [0, 4, 7, 10, 14]),
    ("major 9th",       [0, 4, 7, 11, 14]),
    ("minor 9th",       [0, 3, 7, 10, 14]),
    ("add 9",           [0, 4, 7, 14]),
    ("6th",             [0, 4, 7, 9]),
    ("minor 6th",       [0, 3, 7, 9]),
    ("dominant 11th",   [0, 4, 7, 10, 14, 17]),
    ("dominant 13th",   [0, 4, 7, 10, 14, 17, 21]),
    ("power chord",     [0, 7]),
]

def chord_note_names(root_idx: int, intervals: list[int]) -> list[str]:
    return [NOTES[(root_idx + i) % 12] for i in intervals]


# ---------------------------------------------------------------------------
# Guitar voicings
# Each voicing is a list of 6 values (strings E2 A2 D3 G3 B3 E4 low→high).
# Value = fret number (int), or None = string not played (X).
# ---------------------------------------------------------------------------
#
# Format: dict keyed by (note_symbol, chord_type_name) → list of voicings
# Each voicing is (label, [e, A, D, G, B, e]) where fret=None means muted.
#
GUITAR_VOICINGS: dict[tuple[str, str], list[tuple[str, list]]] = {
    # ── MAJOR ──────────────────────────────────────────────────────────────
    ("C", "major"): [
        ("Open C", [None, 3, 2, 0, 1, 0]),
        ("Barre 8th fret", [8, 10, 10, 9, 8, 8]),
    ],
    ("D", "major"): [
        ("Open D", [None, None, 0, 2, 3, 2]),
        ("Barre 5th fret", [5, 7, 7, 6, 5, 5]),
    ],
    ("E", "major"): [
        ("Open E", [0, 2, 2, 1, 0, 0]),
        ("Barre 12th fret", [12, 14, 14, 13, 12, 12]),
    ],
    ("F", "major"): [
        ("Barre 1st fret", [1, 3, 3, 2, 1, 1]),
        ("High voicing", [None, None, 3, 2, 1, 1]),
    ],
    ("G", "major"): [
        ("Open G", [3, 2, 0, 0, 0, 3]),
        ("Barre 3rd fret", [3, 5, 5, 4, 3, 3]),
    ],
    ("A", "major"): [
        ("Open A", [None, 0, 2, 2, 2, 0]),
        ("Barre 5th fret", [5, 7, 7, 6, 5, 5]),
    ],
    ("B", "major"): [
        ("Barre 2nd fret", [None, 2, 4, 4, 4, 2]),
        ("Barre 7th fret", [7, 9, 9, 8, 7, 7]),
    ],
    ("C#", "major"): [
        ("Barre 4th fret", [None, 4, 6, 6, 6, 4]),
        ("Barre 9th fret", [9, 11, 11, 10, 9, 9]),
    ],
    ("D#", "major"): [
        ("Barre 6th fret", [None, 6, 8, 8, 8, 6]),
        ("Barre 11th fret", [11, 13, 13, 12, 11, 11]),
    ],
    ("F#", "major"): [
        ("Barre 2nd fret", [2, 4, 4, 3, 2, 2]),
        ("Barre 9th fret", [9, 11, 11, 10, 9, 9]),
    ],
    ("G#", "major"): [
        ("Barre 4th fret", [4, 6, 6, 5, 4, 4]),
        ("Barre 11th fret", [11, 13, 13, 12, 11, 11]),
    ],
    ("A#", "major"): [
        ("Barre 1st fret", [None, 1, 3, 3, 3, 1]),
        ("Barre 6th fret", [6, 8, 8, 7, 6, 6]),
    ],
    # ── MINOR ──────────────────────────────────────────────────────────────
    ("C", "minor"): [
        ("Barre 3rd fret", [None, 3, 5, 5, 4, 3]),
        ("High voicing", [None, None, 5, 5, 4, 3]),
    ],
    ("D", "minor"): [
        ("Open Dm", [None, None, 0, 2, 3, 1]),
        ("Barre 5th fret", [5, 7, 7, 5, 5, 5]),
    ],
    ("E", "minor"): [
        ("Open Em", [0, 2, 2, 0, 0, 0]),
        ("Barre 12th fret", [12, 14, 14, 12, 12, 12]),
    ],
    ("F", "minor"): [
        ("Barre 1st fret", [1, 3, 3, 1, 1, 1]),
    ],
    ("G", "minor"): [
        ("Barre 3rd fret", [3, 5, 5, 3, 3, 3]),
        ("Open-ish", [None, None, 5, 3, 3, 3]),
    ],
    ("A", "minor"): [
        ("Open Am", [None, 0, 2, 2, 1, 0]),
        ("Barre 5th fret", [5, 7, 7, 5, 5, 5]),
    ],
    ("B", "minor"): [
        ("Barre 2nd fret", [None, 2, 4, 4, 3, 2]),
        ("Barre 7th fret", [7, 9, 9, 7, 7, 7]),
    ],
    ("C#", "minor"): [
        ("Barre 4th fret", [None, 4, 6, 6, 5, 4]),
        ("Barre 9th fret", [9, 11, 11, 9, 9, 9]),
    ],
    ("D#", "minor"): [
        ("Barre 6th fret", [None, 6, 8, 8, 7, 6]),
    ],
    ("F#", "minor"): [
        ("Barre 2nd fret", [2, 4, 4, 2, 2, 2]),
        ("Barre 9th fret", [9, 11, 11, 9, 9, 9]),
    ],
    ("G#", "minor"): [
        ("Barre 4th fret", [4, 6, 6, 4, 4, 4]),
    ],
    ("A#", "minor"): [
        ("Barre 1st fret", [None, 1, 3, 3, 2, 1]),
        ("Barre 6th fret", [6, 8, 8, 6, 6, 6]),
    ],
    # ── DOMINANT 7TH ───────────────────────────────────────────────────────
    ("C", "dominant 7th"): [
        ("Open C7", [None, 3, 2, 3, 1, 0]),
        ("Barre 8th fret", [8, 10, 10, 9, 8, None]),
    ],
    ("D", "dominant 7th"): [
        ("Open D7", [None, None, 0, 2, 1, 2]),
    ],
    ("E", "dominant 7th"): [
        ("Open E7", [0, 2, 0, 1, 0, 0]),
    ],
    ("G", "dominant 7th"): [
        ("Open G7", [3, 2, 0, 0, 0, 1]),
    ],
    ("A", "dominant 7th"): [
        ("Open A7", [None, 0, 2, 0, 2, 0]),
    ],
    ("B", "dominant 7th"): [
        ("Barre 2nd fret", [None, 2, 1, 2, 0, 2]),
    ],
    # ── MAJOR 7TH ──────────────────────────────────────────────────────────
    ("C", "major 7th"): [
        ("Open Cmaj7", [None, 3, 2, 0, 0, 0]),
    ],
    ("D", "major 7th"): [
        ("Open Dmaj7", [None, None, 0, 2, 2, 2]),
    ],
    ("E", "major 7th"): [
        ("Open Emaj7", [0, 2, 1, 1, 0, 0]),
    ],
    ("G", "major 7th"): [
        ("Open Gmaj7", [3, 2, 0, 0, 0, 2]),
    ],
    ("A", "major 7th"): [
        ("Open Amaj7", [None, 0, 2, 1, 2, 0]),
    ],
    # ── MINOR 7TH ──────────────────────────────────────────────────────────
    ("A", "minor 7th"): [
        ("Open Am7", [None, 0, 2, 0, 1, 0]),
    ],
    ("D", "minor 7th"): [
        ("Open Dm7", [None, None, 0, 2, 1, 1]),
    ],
    ("E", "minor 7th"): [
        ("Open Em7", [0, 2, 2, 0, 3, 0]),
    ],
    # ── POWER CHORDS ───────────────────────────────────────────────────────
    ("C", "power chord"): [("C5", [None, 3, 5, 5, None, None])],
    ("D", "power chord"): [("D5", [None, None, 0, 2, 3, None])],
    ("E", "power chord"): [("E5", [0, 2, 2, None, None, None])],
    ("F", "power chord"): [("F5", [1, 3, 3, None, None, None])],
    ("G", "power chord"): [("G5", [3, 5, 5, None, None, None])],
    ("A", "power chord"): [("A5", [None, 0, 2, 2, None, None])],
    ("B", "power chord"): [("B5", [None, 2, 4, 4, None, None])],
}

GUITAR_STRING_NAMES = ["low E", "A", "D", "G", "B", "high E"]


def guitar_voicing_description(voicing: list) -> str:
    """Convert a voicing list to a human-readable string."""
    parts = []
    for string_name, fret in zip(GUITAR_STRING_NAMES, voicing):
        if fret is None:
            parts.append(f"{string_name}: muted")
        elif fret == 0:
            parts.append(f"{string_name}: open")
        else:
            ordinal = _ordinal(fret)
            parts.append(f"{string_name}: {ordinal} fret")
    return ", ".join(parts)


def _ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return f"{n}{['th','st','nd','rd','th','th','th','th','th','th'][n % 10]}"


# ---------------------------------------------------------------------------
# Ukulele voicings (G4 C4 E4 A4 tuning, low→high)
# ---------------------------------------------------------------------------

UKULELE_VOICINGS: dict[tuple[str, str], list[tuple[str, list]]] = {
    ("C", "major"): [("Open C", [0, 0, 0, 3])],
    ("D", "major"): [("Open D", [2, 2, 2, 0])],
    ("E", "major"): [("Barre", [4, 4, 4, 2])],
    ("F", "major"): [("Open F", [2, 0, 1, 0])],
    ("G", "major"): [("Open G", [0, 2, 3, 2])],
    ("A", "major"): [("Open A", [2, 1, 0, 0])],
    ("B", "major"): [("Barre 2nd", [4, 3, 2, 2])],
    ("C#", "major"): [("Barre 1st", [1, 1, 1, 4])],
    ("D#", "major"): [("Barre 3rd", [3, 3, 3, 1])],
    ("F#", "major"): [("Barre", [3, 1, 2, 1])],
    ("G#", "major"): [("Barre", [5, 3, 4, 3])],
    ("A#", "major"): [("Open Bb", [3, 2, 1, 1])],

    ("C", "minor"): [("Open Cm", [0, 3, 3, 3])],
    ("D", "minor"): [("Open Dm", [2, 2, 1, 0])],
    ("E", "minor"): [("Em", [0, 4, 3, 2])],
    ("F", "minor"): [("Fm", [1, 0, 1, 3])],
    ("G", "minor"): [("Gm", [0, 2, 3, 1])],
    ("A", "minor"): [("Open Am", [2, 0, 0, 0])],
    ("B", "minor"): [("Bm", [4, 2, 2, 2])],
    ("A#", "minor"): [("Bbm", [3, 1, 1, 1])],

    ("C", "dominant 7th"): [("C7", [0, 0, 0, 1])],
    ("D", "dominant 7th"): [("D7", [2, 2, 2, 3])],
    ("G", "dominant 7th"): [("G7", [0, 2, 1, 2])],
    ("A", "dominant 7th"): [("A7", [0, 1, 0, 0])],

    ("C", "major 7th"): [("Cmaj7", [0, 0, 0, 2])],
    ("F", "major 7th"): [("Fmaj7", [2, 4, 1, 0])],

    ("A", "minor 7th"): [("Am7", [0, 0, 0, 0])],
    ("D", "minor 7th"): [("Dm7", [2, 2, 1, 3])],
}

UKULELE_STRING_NAMES = ["G", "C", "E", "A"]


def ukulele_voicing_description(voicing: list) -> str:
    parts = []
    for string_name, fret in zip(UKULELE_STRING_NAMES, voicing):
        if fret == 0:
            parts.append(f"{string_name}: open")
        else:
            parts.append(f"{string_name}: {_ordinal(fret)} fret")
    return ", ".join(parts)


