"""German compound morphology and orthographic linearisation."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from .model import Compound, Step


class MorphologyError(ValueError):
    """Raised when a structure cannot be realized under strict morphology."""


@dataclass(frozen=True, slots=True)
class RealizedComponent:
    """One lexical component after role and linking-form realization."""

    lemma: str
    stem: str
    linking_form: str
    surface: str
    is_head: bool
    source_step_index: int | None


@dataclass(frozen=True, slots=True)
class LinearizationResult:
    """Auditable output of the morphology-to-orthography pipeline."""

    components: tuple[RealizedComponent, ...]
    word: str

    @property
    def linking_forms(self) -> tuple[str, ...]:
        return tuple(component.linking_form for component in self.components[:-1])


def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _internal(form: str) -> str:
    """Lowercase only the lexical initial after it becomes word-internal."""
    return form[:1].lower() + form[1:]


def realize_modifier(step: Step) -> str:
    """Realize one modifier with its explicitly licensed linking form."""
    if not step.modifier.allowed_as_modifier:
        raise MorphologyError(
            f"{step.modifier.lemma} is not licensed as a modifier"
        )
    link = _nfc(step.effective_linking_form)
    if link not in step.modifier.linking_forms:
        raise MorphologyError(
            f"linking form {link!r} is not licensed for {step.modifier.lemma}"
        )
    stem = _nfc(step.modifier.stem)
    form = stem + link
    if not stem or not stem.isalpha() or (link and not link.isalpha()):
        raise MorphologyError(
            f"modifier realization for {step.modifier.lemma} is not alphabetic"
        )
    return form


def realize_components(compound: Compound) -> tuple[RealizedComponent, ...]:
    """Apply morphology and return components in German surface order."""
    if not compound.head.allowed_as_head:
        raise MorphologyError(f"{compound.head.lemma} is not licensed as a head")

    components: list[RealizedComponent] = []
    step_count = len(compound.steps)
    for reverse_offset, step in enumerate(reversed(compound.steps)):
        source_index = step_count - reverse_offset
        stem = _nfc(step.modifier.stem)
        link = _nfc(step.effective_linking_form)
        components.append(
            RealizedComponent(
                lemma=step.modifier.lemma,
                stem=stem,
                linking_form=link,
                surface=realize_modifier(step),
                is_head=False,
                source_step_index=source_index,
            )
        )

    head = _nfc(compound.head.stem)
    if not head or not head.isalpha():
        raise MorphologyError("head realization is not alphabetic")
    components.append(
        RealizedComponent(
            lemma=compound.head.lemma,
            stem=head,
            linking_form="",
            surface=head,
            is_head=True,
            source_step_index=None,
        )
    )
    return tuple(components)


def surface_forms(compound: Compound) -> tuple[str, ...]:
    """Return linked lexical realizations in German surface order."""
    return tuple(component.surface for component in realize_components(compound))


def linearization_result(compound: Compound) -> LinearizationResult:
    """Run the explicit morphology, ordering, casing, and NFC pipeline."""
    components = realize_components(compound)
    word = "".join(_internal(component.surface) for component in components)
    word = _nfc(word[:1].upper() + word[1:])
    if not word or not word.isalpha():
        raise MorphologyError("linearization did not produce one alphabetic word")
    if not unicodedata.is_normalized("NFC", word):
        raise MorphologyError("linearization did not produce NFC text")
    return LinearizationResult(components, word)


def linearize(compound: Compound) -> str:
    """Return one NFC-normalized, capitalized German noun.

    Modern German spelling preserves three identical consonants at a compound
    boundary; straightforward concatenation therefore deliberately performs no
    consonant deletion. Hyphens are outside the strict default representation.
    """
    return linearization_result(compound).word


def boundaries(compound: Compound) -> str:
    """Expose lexical boundaries and linking forms without counting links."""
    parts: list[str] = []
    for component in realize_components(compound):
        if component.is_head:
            parts.append(component.stem)
        elif component.linking_form:
            parts.append(f"{component.stem}[{component.linking_form}]")
        else:
            parts.append(component.stem)
    return "+".join(parts)
