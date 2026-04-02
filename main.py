"""Chords — accessible chord reference and audio app."""

import time

import pygame

import accessibility
import audio
import data_loader
from audio import INSTRUMENTS as _SYNTH_INSTRUMENTS
from chord_data import NOTES, NOTE_SYMBOLS, CHORD_TYPES, chord_note_names

# ── Instrument list ───────────────────────────────────────────────────────────
# Prefer instruments discovered from the data folder; fall back to the built-in
# synthesis list so the app still works before generate_data.py has been run.

INSTRUMENTS = data_loader.get_instruments() or list(_SYNTH_INSTRUMENTS)

# ── State ─────────────────────────────────────────────────────────────────────

note_idx       = 0
chord_type_idx = 0
instrument_idx = 0

in_submenu   = False
submenu_items: list[tuple[str, str, object]] = []  # (label, desc, wav_path|None)
submenu_idx  = 0

# ── Helpers ───────────────────────────────────────────────────────────────────

def current_note_name()  -> str: return NOTES[note_idx]
def current_chord_type() -> str: return CHORD_TYPES[chord_type_idx][0]
def current_intervals()  -> list: return CHORD_TYPES[chord_type_idx][1]
def current_instrument() -> str: return INSTRUMENTS[instrument_idx]

def current_chord_name() -> str:
    return f"{current_note_name()} {current_chord_type()}"


def _play_chord_audio():
    """Play WAV from data folder if available, else synthesise."""
    audio.stop_audio()
    wav = data_loader.get_chord_wav(
        current_instrument(), current_note_name(), current_chord_type()
    )
    if wav:
        audio.play_wav(wav)
    else:
        audio.play_chord(note_idx, current_intervals(), current_instrument())


def _play_voicing_audio(voicing_wav):
    """Play a voicing-specific WAV if provided, else fall back to chord audio."""
    audio.stop_audio()
    if voicing_wav and audio.play_wav(voicing_wav):
        return
    wav = data_loader.get_chord_wav(
        current_instrument(), current_note_name(), current_chord_type()
    )
    if wav:
        audio.play_wav(wav)
    else:
        audio.play_chord(note_idx, current_intervals(), current_instrument())


def announce_current_chord():
    accessibility.speak(current_chord_name(), interrupt=True)


def announce_instrument():
    accessibility.speak(current_instrument(), interrupt=True)


# ── Actions ───────────────────────────────────────────────────────────────────

def on_up():
    global chord_type_idx, submenu_idx
    if in_submenu:
        if submenu_idx > 0:
            submenu_idx -= 1
            name, _, _ = submenu_items[submenu_idx]
            accessibility.speak(name, interrupt=True)
        return
    if chord_type_idx > 0:
        chord_type_idx -= 1
        announce_current_chord()


def on_down():
    global chord_type_idx, submenu_idx
    if in_submenu:
        if submenu_idx < len(submenu_items) - 1:
            submenu_idx += 1
            name, _, _ = submenu_items[submenu_idx]
            accessibility.speak(name, interrupt=True)
        return
    if chord_type_idx < len(CHORD_TYPES) - 1:
        chord_type_idx += 1
        announce_current_chord()


def on_left():
    global note_idx
    if in_submenu:
        return
    if note_idx > 0:
        note_idx -= 1
        announce_current_chord()


def on_right():
    global note_idx
    if in_submenu:
        return
    if note_idx < len(NOTES) - 1:
        note_idx += 1
        announce_current_chord()


def on_home():
    global chord_type_idx
    if in_submenu:
        return
    chord_type_idx = 0
    announce_current_chord()


def on_end():
    global chord_type_idx
    if in_submenu:
        return
    chord_type_idx = len(CHORD_TYPES) - 1
    announce_current_chord()


_LETTER_TO_NOTE = {
    pygame.K_c: 0,
    pygame.K_d: 2,
    pygame.K_e: 4,
    pygame.K_f: 5,
    pygame.K_g: 7,
    pygame.K_a: 9,
    pygame.K_b: 11,
}


def on_note_letter(new_note_idx: int):
    global note_idx
    if in_submenu:
        return
    note_idx = new_note_idx
    announce_current_chord()


def on_page_up():
    global instrument_idx
    if in_submenu:
        return
    if instrument_idx > 0:
        instrument_idx -= 1
        announce_instrument()


def on_page_down():
    global instrument_idx
    if in_submenu:
        return
    if instrument_idx < len(INSTRUMENTS) - 1:
        instrument_idx += 1
        announce_instrument()


def _open_voicing_menu():
    """Open the voicings submenu. Returns True if menu was opened."""
    global in_submenu, submenu_items, submenu_idx
    voicings = data_loader.get_voicings(
        current_instrument(), current_note_name(), current_chord_type()
    )
    if not voicings:
        return False
    in_submenu    = True
    submenu_items = voicings
    submenu_idx   = 0
    name, desc, wav = submenu_items[0]
    accessibility.speak(
        f"Voicings for {current_chord_name()}. {name}. "
        "Up and down to browse. Enter to play, Space for fingering, Escape to close.",
        interrupt=True,
    )
    return True


def on_enter():
    if in_submenu:
        # Re-play current voicing's audio
        _, _, wav = submenu_items[submenu_idx]
        _play_voicing_audio(wav)
        return

    voicings = data_loader.get_voicings(
        current_instrument(), current_note_name(), current_chord_type()
    )
    if voicings and len(voicings) > 1:
        _open_voicing_menu()
    else:
        # Single voicing or no data — just play
        _play_chord_audio()


def on_space():
    if in_submenu:
        # Read fingering for current voicing
        name, desc, _ = submenu_items[submenu_idx]
        text = f"{name}: {desc}" if desc else name
        accessibility.speak(text, interrupt=True)
        return

    voicings = data_loader.get_voicings(
        current_instrument(), current_note_name(), current_chord_type()
    )
    if not voicings:
        accessibility.speak(
            f"No fingering data for {current_chord_name()} on {current_instrument()}.",
            interrupt=True,
        )
        return

    if len(voicings) == 1:
        name, desc, _ = voicings[0]
        text = f"{name}: {desc}" if desc else name
        accessibility.speak(text, interrupt=True)
        return

    _open_voicing_menu()


def on_escape() -> bool:
    global in_submenu
    if in_submenu:
        in_submenu = False
        accessibility.speak("Closed voicings menu.", interrupt=True)
        announce_current_chord()
        return False
    accessibility.speak("Goodbye.", interrupt=True)
    time.sleep(0.4)
    return True


def on_help():
    accessibility.speak(
        "Keyboard help. "
        "Left and right arrows: change root note. "
        "A through G: jump directly to that root note. "
        "Up and down arrows: change chord type. "
        "Home: first chord type. End: last chord type. "
        "Page up and page down: change instrument. "
        "Enter: play chord, or open voicings menu if multiple exist. "
        "Space: show fingering, or open voicings menu if multiple exist. "
        "In the voicings menu: Enter replays audio, Space reads fingering. "
        "Escape: close voicings menu, or quit.",
        interrupt=True,
    )

# ── Drawing ───────────────────────────────────────────────────────────────────

BG     = (30, 30, 30)
FG     = (220, 220, 220)
ACCENT = (100, 180, 255)
DIM    = (120, 120, 120)


def draw(screen, font_large, font_med, font_small):
    screen.fill(BG)
    w, h = screen.get_size()

    surf = font_large.render(current_chord_name(), True, ACCENT)
    screen.blit(surf, surf.get_rect(centerx=w // 2, y=40))

    surf = font_med.render(current_instrument(), True, FG)
    screen.blit(surf, surf.get_rect(centerx=w // 2, y=110))

    note_names = chord_note_names(note_idx, current_intervals())
    surf = font_small.render("Notes: " + ",  ".join(note_names), True, DIM)
    screen.blit(surf, surf.get_rect(centerx=w // 2, y=165))

    if in_submenu:
        panel = pygame.Surface((w - 80, h - 240), pygame.SRCALPHA)
        panel.fill((50, 50, 70, 220))
        screen.blit(panel, (40, 210))

        title = font_med.render(f"Voicings for {current_chord_name()}", True, ACCENT)
        screen.blit(title, title.get_rect(centerx=w // 2, y=220))

        for i, (label, desc, _) in enumerate(submenu_items):
            selected = i == submenu_idx
            color  = ACCENT if selected else FG
            prefix = "▶ " if selected else "   "
            l_surf = font_small.render(prefix + label, True, color)
            d_surf = font_small.render("    " + desc, True, FG if selected else DIM)
            y = 270 + i * 55
            screen.blit(l_surf, (60, y))
            screen.blit(d_surf, (60, y + 22))
    else:
        hints = [
            "← → or A–G: root note",
            "↑ ↓ chord type",
            "Home/End: first/last",
            "PgUp/Dn: instrument",
            "Enter: play",
            "Space: fingering",
            "H: help",
            "Esc: quit",
        ]
        surf = font_small.render("    ".join(hints), True, DIM)
        screen.blit(surf, surf.get_rect(centerx=w // 2, y=h - 36))

    pygame.display.flip()

# ── Key table & main loop ─────────────────────────────────────────────────────

_KEY_ACTIONS = {
    pygame.K_UP:       on_up,
    pygame.K_DOWN:     on_down,
    pygame.K_LEFT:     on_left,
    pygame.K_RIGHT:    on_right,
    pygame.K_HOME:     on_home,
    pygame.K_END:      on_end,
    pygame.K_PAGEUP:   on_page_up,
    pygame.K_PAGEDOWN: on_page_down,
    pygame.K_RETURN:   on_enter,
    pygame.K_SPACE:    on_space,
    pygame.K_h:        on_help,
}


def main():
    pygame.init()
    screen = pygame.display.set_mode((720, 420))
    pygame.display.set_caption("Chords")

    font_large = pygame.font.SysFont("Segoe UI", 48, bold=True)
    font_med   = pygame.font.SysFont("Segoe UI", 28)
    font_small = pygame.font.SysFont("Segoe UI", 18)

    prism_ok = accessibility.init()
    if prism_ok:
        time.sleep(0.2)
        accessibility.speak(
            f"Chords app ready. "
            f"{current_chord_name()} on {current_instrument()}. "
            "Press H for help.",
            interrupt=False,
        )

    clock   = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if on_escape():
                        running = False
                elif event.key in _KEY_ACTIONS:
                    _KEY_ACTIONS[event.key]()
                elif event.key in _LETTER_TO_NOTE:
                    on_note_letter(_LETTER_TO_NOTE[event.key])

        draw(screen, font_large, font_med, font_small)
        clock.tick(60)

    audio.stop_audio()
    accessibility.shutdown()
    pygame.quit()


if __name__ == "__main__":
    main()
