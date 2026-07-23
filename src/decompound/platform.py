"""Cross-platform text-stream policy for the command-line interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TextIO


@dataclass(frozen=True, slots=True)
class StreamConfiguration:
    encoding: str = "utf-8"
    errors: str = "strict"


def configure_text_stream(
    stream: TextIO,
    configuration: StreamConfiguration = StreamConfiguration(),
) -> bool:
    """Request deterministic Unicode handling when the stream supports it.

    `TextIOWrapper.reconfigure` exists on supported CPython platforms, while
    StringIO, test doubles, and embedded streams may omit it. Unsupported streams
    remain usable and return False.
    """
    reconfigure = getattr(stream, "reconfigure", None)
    if not callable(reconfigure):
        return False
    try:
        reconfigure(
            encoding=configuration.encoding,
            errors=configuration.errors,
        )
    except (AttributeError, OSError, ValueError):
        return False
    return True


def configure_cli_streams(stdout: TextIO, stderr: TextIO) -> tuple[bool, bool]:
    return configure_text_stream(stdout), configure_text_stream(stderr)
