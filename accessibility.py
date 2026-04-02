"""Prism/prismatoid wrapper for screen reader announcements."""

from __future__ import annotations

import contextlib
import os
import sys
from pathlib import Path

_ctx = None
_backend = None


def _prepare_prism():
    """
    Ensure the prism native DLL is discoverable before importing the package.

    In a Nuitka standalone build the exe sits next to a prism/_native/
    directory that was copied in at build time. prismatoid's lib.py uses
    Path(__file__).parent / "_native" which may not resolve correctly when
    frozen, so we pre-register the directory with the OS loader ourselves.
    """
    candidates = [
        # Nuitka standalone: next to the executable
        Path(sys.executable).parent / "prism" / "_native",
        # Running from source or onefile extraction
        Path(__file__).parent / "prism" / "_native",
    ]
    # Also try the installed package location
    with contextlib.suppress(Exception):
        import importlib.util
        spec = importlib.util.find_spec("prism")
        if spec and spec.origin:
            candidates.append(Path(spec.origin).parent / "_native")

    for candidate in candidates:
        if candidate.exists():
            # Windows requires explicit DLL directory registration
            if sys.platform == "win32":
                with contextlib.suppress(AttributeError):
                    os.add_dll_directory(str(candidate))
            # Also set PATH so older Windows DLL search picks it up
            os.environ["PATH"] = str(candidate) + os.pathsep + os.environ.get("PATH", "")
            break


def init() -> bool:
    """Initialize Prism. Returns True on success."""
    global _ctx, _backend
    _prepare_prism()
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
        with contextlib.suppress(Exception):
            _backend.speak(text, interrupt)


def shutdown() -> None:
    global _ctx, _backend
    _backend = None
    _ctx = None
