import json

import pytest

from decompound import (
    Generator,
    SCHEMA_NAME,
    SCHEMA_VERSION,
    SemanticType as T,
    analysis_data,
    analysis_json,
    explanation_lines,
)


@pytest.mark.parametrize("length", [1, 2, 12, 100])
def test_json_schema_is_complete_and_count_consistent(length):
    compound = Generator.seeded(length).generate(length, T.DOCUMENT)
    data = analysis_data(compound)
    assert data["schema"] == SCHEMA_NAME == "decompound.analysis"
    assert data["schema_version"] == SCHEMA_VERSION == 1
    assert data["components"] == length
    assert len(data["component_sequence"]) == length
    assert len(data["relations_inner_to_outer"]) == length - 1
    assert data["validation"]["valid"] is True
    assert data["validation"]["semantic_edges"] == length - 1
    assert [layer["name"] for layer in data["validation"]["layers"]] == [
        "structure", "semantics", "morphology", "orthography",
    ]
    assert all(layer["valid"] for layer in data["validation"]["layers"])
    assert data["semantic_type"] == "document"
    assert data["component_sequence"][-1]["is_head"] is True
    assert sum(x["is_head"] for x in data["component_sequence"]) == 1


def test_component_and_relation_records_have_stable_positions():
    compound = Generator.seeded("positions").generate(20, T.SYSTEM)
    data = analysis_data(compound)
    assert [x["position"] for x in data["component_sequence"]] == list(range(1, 21))
    assert [x["index"] for x in data["relations_inner_to_outer"]] == list(range(1, 20))
    assert all(x["surface"] == x["stem"] + x["linking_form"] for x in data["component_sequence"][:-1])


def test_json_serialization_is_deterministic_compact_and_unicode():
    compound = Generator.seeded("json").generate(30)
    left = analysis_json(compound)
    right = analysis_json(compound)
    assert left == right
    assert "\n" not in left
    assert ": " not in left
    assert "Prüfung" in left or "Qualität" in left or "Behörde" in left or json.loads(left)["word"]
    assert json.loads(left) == analysis_data(compound)


def test_explanation_contains_required_human_fields():
    compound = Generator.seeded(5).generate(8, T.PROCESS)
    lines = explanation_lines(compound)
    assert lines[0].isalpha()
    assert any(line == "components: 8" for line in lines)
    assert any(line.startswith("boundaries: ") for line in lines)
    assert any(line == "type: process" for line in lines)
    assert any(line.startswith("head: ") for line in lines)
    assert any(line.startswith("gloss: ") for line in lines)
    assert any(line.startswith("strategy: ") for line in lines)
