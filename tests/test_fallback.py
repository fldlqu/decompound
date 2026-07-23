from unittest.mock import patch

from decompound import Generator, SemanticType, linearize, validate
from decompound.planning import PlanningError


def test_normal_generation_records_dp_strategy():
    compound = Generator.seeded(1).generate(25, SemanticType.SYSTEM)
    assert compound.metadata.strategy == "constrained-dp"
    assert not compound.metadata.fallback_used
    assert compound.metadata.fallback_reason is None


def test_planning_failure_falls_back_to_safe_skeleton_exactly():
    with patch(
        "decompound.generator.SemanticPlanner.plan",
        side_effect=PlanningError("fixture graph exhausted"),
    ):
        compound = Generator.seeded(8).generate(500, SemanticType.DOCUMENT)

    assert compound.component_count == 500
    assert compound.semantic_type == SemanticType.DOCUMENT
    assert compound.metadata.strategy == "safe-skeleton"
    assert compound.metadata.fallback_used
    assert "planner" in compound.metadata.fallback_reason
    validate(compound, 500)
    assert linearize(compound).isalpha()


def test_fallback_uses_only_closed_type_preserving_steps():
    with patch(
        "decompound.generator.SemanticPlanner.plan",
        side_effect=PlanningError("fixture"),
    ):
        for kind in (
            SemanticType.INSTITUTION,
            SemanticType.SYSTEM,
            SemanticType.PROCESS,
            SemanticType.DOCUMENT,
        ):
            compound = Generator.seeded(kind.value).generate(100, kind)
            assert all(step.rule.recursive for step in compound.steps)
            assert all(step.rule.signature == (kind, kind, kind) for step in compound.steps)
            assert all(step.modifier.semantic_type == kind for step in compound.steps)


def test_metadata_survives_interactive_extension():
    generator = Generator.seeded(2)
    compound = generator.generate(3, SemanticType.SYSTEM)
    extended = generator.extend(compound)
    assert extended.metadata == compound.metadata
