"""Independent layered checks for generated structures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import unicodedata

from .model import Compound, SemanticType
from .morphology import LinearizationResult, MorphologyError, linearization_result


class ValidationError(ValueError):
    pass


class ValidationLayer(StrEnum):
    STRUCTURE = "structure"
    SEMANTICS = "semantics"
    MORPHOLOGY = "morphology"
    ORTHOGRAPHY = "orthography"


@dataclass(frozen=True, slots=True)
class LayerValidation:
    layer: ValidationLayer
    checks: tuple[str, ...]
    valid: bool = True


@dataclass(frozen=True, slots=True)
class EdgeValidation:
    index: int
    modifier: str
    relation: str
    input_head_type: SemanticType
    modifier_type: SemanticType
    result_type: SemanticType
    valid: bool = True


@dataclass(frozen=True, slots=True)
class ValidationReport:
    components: int
    characters: int
    expected_components: int | None = None
    count_valid: bool = True
    edges: tuple[EdgeValidation, ...] = ()
    final_semantic_type: SemanticType | None = None
    layers: tuple[LayerValidation, ...] = ()
    valid: bool = True

    def layer(self, name: ValidationLayer) -> LayerValidation:
        return next(item for item in self.layers if item.layer == name)


def count_semantic_components(compound: Compound) -> int:
    """Count lexical tree nodes; linking forms are deliberately excluded."""
    return 1 + len(compound.steps)


def validate_component_count(compound: Compound, expected_length: int) -> int:
    if isinstance(expected_length, bool) or not isinstance(expected_length, int):
        raise ValidationError("expected component count must be an integer >= 1")
    if expected_length < 1:
        raise ValidationError("expected component count must be an integer >= 1")
    actual = count_semantic_components(compound)
    if actual != expected_length:
        raise ValidationError(
            f"expected {expected_length} semantic components, got {actual}"
        )
    if len(compound.components()) != actual:
        raise ValidationError("component traversal disagrees with structural count")
    return actual


def validate_structure(
    compound: Compound, expected_length: int | None = None,
) -> LayerValidation:
    actual = count_semantic_components(compound)
    if compound.component_count != actual:
        raise ValidationError("structure: component_count property is inconsistent")
    if len(compound.components()) != actual:
        raise ValidationError("structure: component traversal has the wrong size")
    if compound.components()[-1] is not compound.head:
        raise ValidationError("structure: rightmost component is not the head")
    if expected_length is not None:
        validate_component_count(compound, expected_length)
    return LayerValidation(
        ValidationLayer.STRUCTURE,
        ("component-count", "surface-order-traversal", "rightmost-head"),
    )


def validate_semantic_edges(compound: Compound) -> tuple[EdgeValidation, ...]:
    """Fold and verify every inner-to-outer typed relation edge."""
    current = compound.head.semantic_type
    reports: list[EdgeValidation] = []
    for index, step in enumerate(compound.steps, start=1):
        if step.rule.head_type != current:
            raise ValidationError(
                f"edge {index}: rule expects head type "
                f"{step.rule.head_type.value}, got {current.value}"
            )
        if step.modifier.semantic_type != step.rule.modifier_type:
            raise ValidationError(
                f"edge {index}: modifier {step.modifier.lemma} has type "
                f"{step.modifier.semantic_type.value}, expected "
                f"{step.rule.modifier_type.value}"
            )
        if not step.rule.accepts(step.modifier.semantic_type, current):
            raise ValidationError(f"edge {index}: relation signature rejected inputs")
        reports.append(
            EdgeValidation(
                index=index,
                modifier=step.modifier.lemma,
                relation=step.rule.relation.value,
                input_head_type=current,
                modifier_type=step.modifier.semantic_type,
                result_type=step.rule.result_type,
            )
        )
        current = step.rule.result_type
    if current != compound.semantic_type:
        raise ValidationError(
            "semantic fold result disagrees with compound.semantic_type"
        )
    return tuple(reports)


def validate_semantics(
    compound: Compound,
) -> tuple[LayerValidation, tuple[EdgeValidation, ...]]:
    edges = validate_semantic_edges(compound)
    return (
        LayerValidation(
            ValidationLayer.SEMANTICS,
            ("typed-relation-fold", "modifier-signatures", "final-result-type"),
        ),
        edges,
    )


def validate_morphology(
    compound: Compound,
) -> tuple[LayerValidation, LinearizationResult]:
    if not compound.head.allowed_as_head:
        raise ValidationError("morphology: compound head is not head-licensed")
    for index, step in enumerate(compound.steps, start=1):
        if not step.modifier.allowed_as_modifier:
            raise ValidationError(
                f"morphology: edge {index} contains a modifier-forbidden lexeme"
            )
        if step.effective_linking_form not in step.modifier.linking_forms:
            raise ValidationError(
                f"morphology: edge {index} linking form is not licensed"
            )
    try:
        realization = linearization_result(compound)
    except MorphologyError as exc:
        raise ValidationError(f"morphology: {exc}") from exc
    if len(realization.components) != count_semantic_components(compound):
        raise ValidationError(
            "morphology: realization changed the semantic component count"
        )
    return (
        LayerValidation(
            ValidationLayer.MORPHOLOGY,
            ("role-licensing", "linking-allomorphs", "component-realization"),
        ),
        realization,
    )


def validate_orthography(word: str) -> LayerValidation:
    if not word:
        raise ValidationError("orthography: result is empty")
    if not unicodedata.is_normalized("NFC", word):
        raise ValidationError("orthography: result is not NFC-normalized")
    if not word[0].isupper():
        raise ValidationError("orthography: German noun is not capitalized")
    if not word.isalpha():
        raise ValidationError("orthography: result is not one alphabetic word")
    return LayerValidation(
        ValidationLayer.ORTHOGRAPHY,
        ("non-empty", "noun-capitalization", "one-alphabetic-word", "nfc"),
    )


def validate(compound: Compound, expected_length: int | None = None) -> ValidationReport:
    """Run structure -> semantics -> morphology -> orthography in order."""
    structure = validate_structure(compound, expected_length)
    semantics, edge_reports = validate_semantics(compound)
    morphology, realization = validate_morphology(compound)
    orthography = validate_orthography(realization.word)
    actual_components = count_semantic_components(compound)
    return ValidationReport(
        components=actual_components,
        characters=len(realization.word),
        expected_components=expected_length,
        count_valid=(expected_length is None or actual_components == expected_length),
        edges=edge_reports,
        final_semantic_type=compound.semantic_type,
        layers=(structure, semantics, morphology, orthography),
    )
