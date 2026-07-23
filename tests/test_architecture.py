import ast
from pathlib import Path

import decompound


PACKAGE = Path(__file__).parents[1] / "src" / "decompound"


def project_imports(module):
    tree = ast.parse((PACKAGE / module).read_text(encoding="utf-8"))
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            result.add(node.module or "")
    return result


def test_model_is_domain_root_without_project_dependencies():
    assert project_imports("model.py") == set()


def test_lexicon_and_relations_depend_only_on_model_inside_project():
    assert project_imports("lexicon.py") <= {"__future__", "model"}
    assert project_imports("relations.py") <= {"__future__", "model"}


def test_public_api_exposes_documented_primitives():
    expected = {
        "Generator", "Compound", "Step", "Lexeme", "Rule", "SemanticType",
        "Relation", "Gender", "Register", "GenerationMetadata", "ContractRequest", "ContractResult",
        "ContractError", "generate_contract", "linearize", "boundaries",
        "validate", "validate_component_count", "validate_semantic_edges",
        "count_semantic_components", "EdgeValidation", "LinearizationResult",
        "MorphologyError", "RealizedComponent", "LeftExtensionError",
        "LeftExtensionResult", "RebuildError", "RebuildResult", "extend_left",
        "internalize", "linearization_result", "rebuild", "TerminalRenderer",
        "analysis_data", "analysis_json", "explanation_lines", "SCHEMA_NAME",
        "SCHEMA_VERSION", "LayerValidation", "ValidationLayer",
        "validate_structure", "validate_semantics", "validate_morphology",
        "validate_orthography", "StreamConfiguration",
        "configure_text_stream", "configure_cli_streams",
        "realize_components", "surface_forms", "ValidationError",
    }
    assert expected <= set(decompound.__all__)
    assert all(hasattr(decompound, name) for name in expected)


def test_cli_entry_modules_exist():
    assert (PACKAGE / "cli.py").is_file()
    assert (PACKAGE / "__main__.py").is_file()
