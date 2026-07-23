"""decompound public API."""

from .contract import (
    ContractError, ContractRequest, ContractResult, generate_contract,
)
from .generator import Generator
from .left_extension import (
    LeftExtensionError, LeftExtensionResult, extend_left, internalize,
)
from .model import (
    Compound, Gender, GenerationMetadata, Lexeme, Register, Relation, Rule,
    SemanticType, Step,
)
from .morphology import (
    LinearizationResult, MorphologyError, RealizedComponent, boundaries,
    linearization_result, linearize, realize_components, surface_forms,
)
from .platform import (
    StreamConfiguration, configure_cli_streams, configure_text_stream,
)
from .presentation import (
    SCHEMA_NAME, SCHEMA_VERSION, analysis_data, analysis_json,
    explanation_lines,
)
from .rebuild import RebuildError, RebuildResult, rebuild
from .terminal import TerminalRenderer
from .validation import (
    EdgeValidation, LayerValidation, ValidationError, ValidationLayer,
    count_semantic_components, validate, validate_component_count,
    validate_morphology, validate_orthography, validate_semantic_edges,
    validate_semantics, validate_structure,
)

__all__ = [
    "Compound", "ContractError", "ContractRequest", "ContractResult", "Gender", "GenerationMetadata", "Generator", "LeftExtensionError", "LeftExtensionResult", "Lexeme", "RebuildError", "RebuildResult", "Register", "Relation", "Rule", "SCHEMA_NAME", "SCHEMA_VERSION", "SemanticType", "StreamConfiguration", "TerminalRenderer",
    "Step", "EdgeValidation", "LayerValidation", "LinearizationResult", "MorphologyError", "RealizedComponent", "ValidationError", "ValidationLayer", "analysis_data", "analysis_json", "boundaries", "configure_cli_streams", "configure_text_stream", "count_semantic_components", "explanation_lines", "extend_left", "generate_contract", "internalize", "linearization_result", "linearize", "realize_components", "rebuild", "surface_forms", "validate", "validate_component_count", "validate_morphology", "validate_orthography", "validate_semantic_edges", "validate_semantics", "validate_structure",
]
__version__ = "0.1.0"
