import random

import pytest

from decompound import Generator, SemanticType as T, extend_left, internalize, validate
from decompound.morphology import realize_modifier


@pytest.mark.parametrize("kind", [T.INSTITUTION, T.SYSTEM, T.PROCESS, T.DOCUMENT])
def test_verified_left_extension_preserves_exact_structure_and_word(kind):
    generator = Generator.seeded(kind.value)
    compound = generator.start(kind)
    for expected in range(2, 250):
        old = compound
        old_steps = old.steps
        old_components = old.components()
        result = generator.extend_left(old)
        compound = result.compound

        assert result.previous is old
        assert result.added_components == 1
        assert compound.component_count == expected
        assert compound.head is old.head
        assert compound.steps[:-1] == old_steps
        assert compound.steps[-1] == result.step
        assert compound.components() == (result.step.modifier,) + old_components
        assert result.added_surface == realize_modifier(result.step)
        assert result.rebuilt.compound is compound
        assert result.rebuilt.steps_inner_to_outer == compound.steps
        assert result.rebuilt.word == result.word
        assert result.word == (
            result.added_surface[:1].upper()
            + result.added_surface[1:]
            + internalize(result.previous_word)
        )
        validate(compound, expected)


def test_old_state_remains_unchanged_after_extension():
    generator = Generator(random.Random(4))
    old = generator.generate(20, T.SYSTEM)
    old_steps = old.steps
    old_components = old.components()
    old_word = generator.extend_left(old).previous_word
    assert old.steps == old_steps
    assert old.components() == old_components
    assert old.component_count == 20
    assert old_word


def test_direct_api_applies_supplied_legal_step():
    generator = Generator.seeded(9)
    old = generator.start(T.DOCUMENT)
    step = generator.next_step(old)
    result = extend_left(old, step)
    assert result.compound.steps == (step,)
    assert result.compound.components() == (step.modifier, old.head)
