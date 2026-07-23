"""Transport-independent control protocol for infinite generation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class InteractionAction(StrEnum):
    EXTEND = "extend"
    QUIT = "quit"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class InteractionInput:
    """Classification of one complete input line."""

    action: InteractionAction
    raw: str
    command: str = ""


def classify_input(line: str) -> InteractionInput:
    """Map a line to the deliberately tiny infinite-mode protocol.

    An empty string denotes EOF. A line containing only whitespace denotes an
    Enter-driven extension. Named quit commands are case-insensitive. Other
    text is invalid and must not mutate generation state.
    """
    if line == "":
        return InteractionInput(InteractionAction.QUIT, line, "eof")
    command = line.strip()
    if not command:
        return InteractionInput(InteractionAction.EXTEND, line, "enter")
    if command.lower() in {"q", "quit", "exit"}:
        return InteractionInput(InteractionAction.QUIT, line, command.lower())
    return InteractionInput(InteractionAction.INVALID, line, command)
