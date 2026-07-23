"""Core linguistic data structures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SemanticType(StrEnum):
    SUBJECT = "subject"
    ACTIVITY = "activity"
    PROCESS = "process"
    SYSTEM = "system"
    INSTITUTION = "institution"
    DOCUMENT = "document"
    ARTIFACT = "artifact"
    LOCATION = "location"
    MATERIAL = "material"


class Relation(StrEnum):
    CONCERNS = "concerns"
    MANAGES = "manages"
    REGULATES = "regulates"
    EXAMINES = "examines"
    USED_FOR = "used_for"
    LOCATED_AT = "located_at"
    PROCESSES = "processes"


class Gender(StrEnum):
    MASCULINE = "m"
    FEMININE = "f"
    NEUTER = "n"
    PLURAL = "pl"


class Register(StrEnum):
    NEUTRAL = "neutral"
    TECHNICAL = "technical"
    ADMINISTRATIVE = "administrative"


@dataclass(frozen=True, slots=True)
class Lexeme:
    """A noun sense with explicit compound morphology and provenance."""

    lemma: str
    stem: str
    semantic_type: SemanticType
    linking_forms: tuple[str, ...] = ("",)
    preferred_linking_form: str = ""
    gender: Gender = Gender.NEUTER
    gloss: str = ""
    allowed_as_modifier: bool = True
    allowed_as_head: bool = True
    register: Register = Register.NEUTRAL
    source: str = "core-curated"
    sense_id: str | None = None

    def __post_init__(self) -> None:
        if not self.lemma or not self.lemma[0].isupper():
            raise ValueError("noun lemma must be non-empty and capitalized")
        if not self.stem or not self.stem[0].isupper():
            raise ValueError("compound stem must be non-empty and capitalized")
        if not self.linking_forms:
            raise ValueError("at least one linking form must be licensed")
        if self.preferred_linking_form not in self.linking_forms:
            raise ValueError("preferred linking form is not licensed")
        if any(not link.isalpha() for link in self.linking_forms if link):
            raise ValueError("linking forms must be alphabetic or empty")
        if not self.allowed_as_modifier and not self.allowed_as_head:
            raise ValueError("lexeme must be usable as modifier or head")
        if not self.source:
            raise ValueError("lexeme source must be recorded")

    @property
    def link(self) -> str:
        """Preferred linking form retained as a compact public convenience."""
        return self.preferred_linking_form

    @property
    def modifier_form(self) -> str:
        if not self.allowed_as_modifier:
            raise ValueError(f"{self.lemma} is not licensed as a modifier")
        return self.stem + self.preferred_linking_form


@dataclass(frozen=True, slots=True)
class Rule:
    """A typed semantic signature ``(modifier, head) -> result``."""

    modifier_type: SemanticType
    head_type: SemanticType
    result_type: SemanticType
    relation: Relation
    gloss_template: str
    recursive: bool = False

    def __post_init__(self) -> None:
        if "{modifier}" not in self.gloss_template:
            raise ValueError("rule gloss template must contain {modifier}")
        if "{head}" not in self.gloss_template:
            raise ValueError("rule gloss template must contain {head}")
        if self.recursive and not (
            self.modifier_type == self.head_type == self.result_type
        ):
            raise ValueError(
                "recursive rules must be closed: (T, T) -> T"
            )

    @property
    def signature(self) -> tuple[SemanticType, SemanticType, SemanticType]:
        return self.modifier_type, self.head_type, self.result_type

    def accepts(self, modifier_type: SemanticType, head_type: SemanticType) -> bool:
        return modifier_type == self.modifier_type and head_type == self.head_type

    def interpret(self, *, modifier: str, head: str) -> str:
        return self.gloss_template.format(modifier=modifier, head=head)


@dataclass(frozen=True, slots=True)
class Step:
    modifier: Lexeme
    rule: Rule
    linking_form: str | None = None

    def __post_init__(self) -> None:
        selected = self.effective_linking_form
        if selected not in self.modifier.linking_forms:
            raise ValueError(
                f"linking form {selected!r} is not licensed for "
                f"{self.modifier.lemma}"
            )
        if not self.modifier.allowed_as_modifier:
            raise ValueError(
                f"{self.modifier.lemma} is not licensed as a modifier"
            )

    @property
    def effective_linking_form(self) -> str:
        return (
            self.modifier.preferred_linking_form
            if self.linking_form is None
            else self.linking_form
        )

    @property
    def modifier_form(self) -> str:
        return self.modifier.stem + self.effective_linking_form


@dataclass(frozen=True, slots=True)
class GenerationMetadata:
    """Non-linguistic provenance for how a compound was constructed."""

    strategy: str = "unspecified"
    fallback_used: bool = False
    fallback_reason: str | None = None


@dataclass(frozen=True, slots=True)
class Compound:
    """Flat representation of a right-headed binary tree.

    ``steps`` are stored from nearest-to-head to outermost. Thus extending a
    compound is O(1); spelling reverses them and appends the immutable head.
    """

    head: Lexeme
    steps: tuple[Step, ...] = ()
    metadata: GenerationMetadata = GenerationMetadata()

    @property
    def component_count(self) -> int:
        return 1 + len(self.steps)

    @property
    def semantic_type(self) -> SemanticType:
        return self.steps[-1].rule.result_type if self.steps else self.head.semantic_type

    def extend(self, step: Step) -> "Compound":
        """Return C(k+1) = rule(modifier, C(k)).

        Type compatibility is checked here so invalid states cannot be created
        accidentally through the public extension operation. Full validation
        remains independent and can inspect externally constructed instances.
        """
        if step.rule.head_type != self.semantic_type:
            raise ValueError(
                f"rule expects head type {step.rule.head_type}, "
                f"got {self.semantic_type}"
            )
        if step.modifier.semantic_type != step.rule.modifier_type:
            raise ValueError(
                "modifier semantic type does not match the rule signature"
            )
        return Compound(self.head, self.steps + (step,), self.metadata)

    def components(self) -> tuple[Lexeme, ...]:
        """Return surface order: outermost modifier through rightmost head."""
        return tuple(s.modifier for s in reversed(self.steps)) + (self.head,)
