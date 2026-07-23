"""Optional generated-word splitter diagnostics.

No splitter is a validity oracle. This protocol lets applications attach one as
non-authoritative evidence without coupling the core to a particular package.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class SplitDiagnostic:
    tool: str
    word: str
    parts: tuple[str, ...]
    score: float | None = None
    authoritative: bool = False


class CompoundSplitter(Protocol):
    name: str

    def split(self, word: str) -> SplitDiagnostic: ...


def diagnose(splitter: CompoundSplitter, word: str) -> SplitDiagnostic:
    result = splitter.split(word)
    if result.authoritative:
        # Prevent an adapter from accidentally upgrading a heuristic result into
        # proof inside this project's API contract.
        return SplitDiagnostic(result.tool, result.word, result.parts, result.score, False)
    return result
