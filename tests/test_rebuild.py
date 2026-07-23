import pytest

from decompound import Generator, SemanticType as T, linearize, rebuild, validate


@pytest.mark.parametrize("kind", [T.INSTITUTION, T.SYSTEM, T.PROCESS, T.DOCUMENT])
@pytest.mark.parametrize("length", [1, 2, 25, 500])
def test_rebuild_derives_complete_consistent_state(kind, length):
    compound = Generator.seeded(f"{kind}:{length}").generate(length, kind)
    result = rebuild(compound)
    assert result.compound is compound
    assert result.steps_inner_to_outer == compound.steps
    assert result.components == compound.components()
    assert result.component_count == length
    assert len(result.realization.components) == length
    assert result.word == linearize(compound)
    validate(compound, length)


def test_every_extension_rebuild_contains_all_old_and_new_steps():
    generator = Generator.seeded("rebuild")
    compound = generator.start(T.DOCUMENT)
    for expected in range(2, 200):
        old = compound
        result = generator.extend_left(old)
        compound = result.compound
        assert result.rebuilt.compound is compound
        assert result.rebuilt.steps_inner_to_outer == old.steps + (result.step,)
        assert result.rebuilt.components == (result.step.modifier,) + old.components()
        assert result.rebuilt.word == result.word
        assert result.rebuilt.component_count == expected


def test_rebuild_is_deterministic_and_has_no_cached_string_dependency():
    compound = Generator.seeded(8).generate(100, T.SYSTEM)
    first = rebuild(compound)
    second = rebuild(compound)
    assert first == second
    assert first.word == second.word
