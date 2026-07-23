"""Always-available algebraic and metamorphic contract properties."""

import random

import pytest

from decompound import (
    ContractRequest,
    Generator,
    SemanticType as T,
    count_semantic_components,
    generate_contract,
    internalize,
    linearize,
    validate,
)
from decompound.morphology import realize_modifier


TARGETS = (T.INSTITUTION, T.SYSTEM, T.PROCESS, T.DOCUMENT)
LENGTHS = (1, 2, 3, 17, 100, 500)
SEEDS = (0, 1, 2, 17, 99, "alpha", "umlaut-ä")


@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("length", LENGTHS)
def test_exact_contract_algebra(target, length):
    compound = generate_contract(
        ContractRequest(length, seed=f"{target}:{length}", target_type=target)
    ).compound
    report = validate(compound, length)

    assert count_semantic_components(compound) == 1 + len(compound.steps) == length
    assert len(compound.components()) == length
    assert len(report.edges) == max(0, length - 1)
    assert compound.semantic_type == target
    assert report.final_semantic_type == target
    assert report.valid and report.count_valid


@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("seed", SEEDS)
def test_extension_induction_step_preserves_invariants(target, seed):
    generator = Generator.seeded(seed)
    current = generator.start(target)
    validate(current, 1)

    for expected_count in range(2, 102):
        previous = current
        extension = generator.extend_left(previous)
        current = extension.compound

        assert current.component_count == previous.component_count + 1
        assert current.components() == (extension.step.modifier,) + previous.components()
        assert current.head is previous.head
        assert extension.step.rule.accepts(
            extension.step.modifier.semantic_type,
            previous.semantic_type,
        )
        assert current.semantic_type == extension.step.rule.result_type
        modifier = realize_modifier(extension.step)
        assert extension.word == (
            modifier[:1].upper() + modifier[1:] + internalize(extension.previous_word)
        )
        validate(current, expected_count)


@pytest.mark.parametrize("seed", SEEDS)
def test_seeded_contract_is_referentially_stable(seed):
    for target in TARGETS:
        for length in (1, 10, 75):
            request = ContractRequest(length, seed, target)
            left = generate_contract(request).compound
            right = generate_contract(request).compound
            assert left == right
            assert linearize(left) == linearize(right)


def test_contract_generation_isolated_from_global_random_state():
    random.seed(90210)
    before = random.getstate()
    for seed in SEEDS:
        generate_contract(ContractRequest(50, seed, T.SYSTEM))
    after = random.getstate()
    assert after == before


@pytest.mark.parametrize("target", TARGETS)
def test_linking_material_is_never_a_semantic_node(target):
    compound = Generator.seeded(f"links:{target}").generate(500, target)
    links = tuple(step.effective_linking_form for step in compound.steps)
    assert any(links)
    assert len(links) == 499
    assert count_semantic_components(compound) == 500
    assert count_semantic_components(compound) != 500 + sum(bool(x) for x in links)


@pytest.mark.parametrize("target", TARGETS)
def test_arbitrary_finite_sample_has_no_hidden_generation_ceiling(target):
    for length in (1, 2, 10, 257, 1000):
        compound = Generator.seeded(length).generate(length, target)
        assert validate(compound, length).components == length
