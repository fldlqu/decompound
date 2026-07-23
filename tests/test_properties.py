import pytest

from decompound import Generator, SemanticType, linearize, validate

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, settings, strategies as st


TARGETS = (
    SemanticType.INSTITUTION,
    SemanticType.SYSTEM,
    SemanticType.PROCESS,
    SemanticType.DOCUMENT,
)


@given(
    st.integers(min_value=1, max_value=300),
    st.integers(),
    st.sampled_from(TARGETS),
)
@settings(max_examples=100, deadline=None)
def test_contract_property(length, seed, target):
    compound = Generator.seeded(seed).generate(length, target)
    report = validate(compound, length)
    assert report.components == length
    assert len(report.edges) == length - 1
    assert compound.semantic_type == target


@given(st.integers())
def test_extension_suffix_property(seed):
    generator = Generator.seeded(seed)
    old = generator.start()
    new = generator.extend(old)
    assert new.component_count == old.component_count + 1
    assert new.components() == (new.components()[0],) + old.components()
    assert linearize(new).endswith(linearize(old).lower())
    validate(new, 2)
    # Case differs only because the old standalone noun became internal.
