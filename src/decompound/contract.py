"""Public service boundary for exact-component contract generation."""

from __future__ import annotations

from dataclasses import dataclass

from .generator import Generator
from .model import Compound, SemanticType
from .validation import validate, validate_component_count


class ContractError(ValueError):
    """Raised when a contract request or generated result violates its terms."""


@dataclass(frozen=True, slots=True)
class ContractRequest:
    """Request exactly ``length`` semantic lexical components."""

    length: int
    seed: int | str | bytes | None = None
    target_type: SemanticType | str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.length, bool) or not isinstance(self.length, int):
            raise ContractError("length must be an integer >= 1")
        if self.length < 1:
            raise ContractError("length must be an integer >= 1")
        if isinstance(self.target_type, str):
            try:
                normalized = SemanticType(self.target_type.lower())
            except ValueError as exc:
                raise ContractError(
                    f"unknown semantic target type: {self.target_type}"
                ) from exc
            object.__setattr__(self, "target_type", normalized)
        elif self.target_type is not None and not isinstance(
            self.target_type, SemanticType
        ):
            raise ContractError("target_type must be a SemanticType or string")


@dataclass(frozen=True, slots=True)
class ContractResult:
    request: ContractRequest
    compound: Compound

    @property
    def component_count(self) -> int:
        return self.compound.component_count


def generate_contract(request: ContractRequest) -> ContractResult:
    """Fulfil and independently verify an exact-length generation request."""
    generator = Generator.seeded(request.seed)
    try:
        compound = generator.generate(request.length, request.target_type)
    except ValueError as exc:
        raise ContractError(str(exc)) from exc
    try:
        validate_component_count(compound, request.length)
        validate(compound, request.length)
    except ValueError as exc:
        raise ContractError(f"generator failed its length contract: {exc}") from exc
    return ContractResult(request, compound)
