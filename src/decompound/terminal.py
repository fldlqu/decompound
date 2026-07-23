"""TTY-safe rendering primitives for interactive complete-word redraws."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TextIO


@dataclass(slots=True)
class TerminalRenderer:
    """Render complete states, using ANSI only for an actual TTY."""

    stream: TextIO
    tty: bool | None = None
    _published: bool = False
    _closed: bool = False

    CLEAR_LINE = "\r\x1b[2K"

    def __post_init__(self) -> None:
        if self.tty is None:
            self.tty = bool(getattr(self.stream, "isatty", lambda: False)())

    def publish(self, word: str) -> None:
        if self._closed:
            raise RuntimeError("cannot publish after renderer close")
        if not word or "\n" in word or "\r" in word:
            raise ValueError("renderer requires one complete single-line word")
        if self.tty:
            prefix = self.CLEAR_LINE if self._published else ""
            self.stream.write(prefix + word)
            self.stream.flush()
        else:
            print(word, file=self.stream, flush=True)
        self._published = True

    def close(self) -> None:
        if self._closed:
            return
        if self.tty and self._published:
            self.stream.write("\n")
            self.stream.flush()
        self._closed = True
