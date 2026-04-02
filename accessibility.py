"""Prism/prismatoid wrapper for screen reader announcements."""

from __future__ import annotations

_ctx = None
_backend = None


def init() -> bool:
    """Initialize Prism. Returns True on success."""
    global _ctx, _backend
    try:
        from prism import Context
        _ctx = Context()
        _backend = _ctx.create_best()
        return True
    except Exception:
        return False


def speak(text: str, interrupt: bool = True) -> None:
    """Speak text via the active screen reader / TTS backend."""
    if _backend is None:
        return
    try:
        _backend.output(text, interrupt)
    except Exception:
        try:
            _backend.speak(text, interrupt)
        except Exception:
            pass


def shutdown() -> None:
    global _ctx, _backend
    _backend = None
    _ctx = None
