import pytest

from decompound import (
    Generator,
    ValidationError,
    count_semantic_components,
    validate,
    validate_component_count,
)


@pytest.mark.parametrize("length", [1, 2, 10, 1000])
def test_structural_count_matches_all_model_views(length):
    compound = Generator.seeded(length).generate(length)
    assert count_semantic_components(compound) == length
    assert compound.component_count == length
    assert len(compound.components()) == length
    assert validate_component_count(compound, length) == length
    report = validate(compound, length)
    assert report.components == length
    assert report.expected_components == length
    assert report.count_valid


def test_linking_forms_do_not_add_components():
    compound = Generator.seeded("links").generate(200)
    nonempty_links = sum(bool(step.effective_linking_form) for step in compound.steps)
    assert nonempty_links > 0
    assert count_semantic_components(compound) == 200
    assert count_semantic_components(compound) != 200 + nonempty_links


def test_wrong_expected_count_is_rejected_with_semantic_wording():
    compound = Generator.seeded(1).generate(3)
    with pytest.raises(
        ValidationError,
        match="expected 4 semantic components, got 3",
    ):
        validate_component_count(compound, 4)


@pytest.mark.parametrize("bad", [0, -1, 1.5, True, "3", None])
def test_invalid_expected_count_is_rejected(bad):
    compound = Generator.seeded(1).generate(3)
    with pytest.raises(ValidationError, match="integer >= 1"):
        validate_component_count(compound, bad)  # type: ignore[arg-type]
