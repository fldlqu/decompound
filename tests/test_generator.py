import random

import pytest

from decompound import Generator, linearize, validate


@pytest.mark.parametrize("length", [1, 2, 3, 10, 100, 1000])
def test_exact_contract(length):
    compound = Generator.seeded(7).generate(length)
    assert compound.component_count == length
    assert validate(compound, length).valid
    assert linearize(compound).isalpha()


def test_seed_is_reproducible():
    a = linearize(Generator.seeded("god").generate(30))
    b = linearize(Generator.seeded("god").generate(30))
    assert a == b


@pytest.mark.parametrize("bad", [0, -1, 1.5, True, "3"])
def test_rejects_invalid_length(bad):
    with pytest.raises(ValueError):
        Generator.seeded().generate(bad)


def test_each_infinite_extension_adds_exactly_one_and_keeps_old_suffix():
    generator = Generator(random.Random(2))
    compound = generator.start()
    old = linearize(compound)
    for expected in range(2, 100):
        compound = generator.extend(compound)
        new = linearize(compound)
        assert compound.component_count == expected
        assert new.lower().endswith(old.lower())
        validate(compound)
        old = new
