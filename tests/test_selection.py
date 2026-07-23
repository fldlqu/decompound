import pytest

from decompound import ContractError, ContractRequest, Generator, SemanticType, generate_contract
from decompound.lexicon import HEADS


def test_available_head_types_are_derived_in_stable_enum_order():
    generator = Generator.seeded(1)
    expected_set = {head.semantic_type for head in HEADS}
    assert set(generator.available_head_types()) == expected_set
    assert list(generator.available_head_types()) == [
        kind for kind in SemanticType if kind in expected_set
    ]


@pytest.mark.parametrize("kind", [
    SemanticType.INSTITUTION,
    SemanticType.SYSTEM,
    SemanticType.PROCESS,
    SemanticType.DOCUMENT,
])
def test_requested_target_selects_matching_head_and_result(kind):
    generator = Generator.seeded("target")
    head = generator.choose_head(kind)
    assert head.semantic_type == kind
    assert head.allowed_as_head
    compound = generator.generate(100, kind)
    assert compound.head.semantic_type == kind
    assert compound.semantic_type == kind


def test_string_target_is_normalized():
    request = ContractRequest(10, "seed", "SYSTEM")
    assert request.target_type == SemanticType.SYSTEM
    result = generate_contract(request)
    assert result.compound.semantic_type == SemanticType.SYSTEM


def test_known_modifier_only_type_is_rejected_as_target():
    with pytest.raises(ContractError, match="no selectable head"):
        generate_contract(ContractRequest(3, target_type=SemanticType.MATERIAL))


def test_unknown_target_is_rejected_at_request_boundary():
    with pytest.raises(ContractError, match="unknown semantic target"):
        ContractRequest(3, target_type="planet")


def test_target_selection_is_reproducible():
    left = Generator.seeded("same").choose_head()
    right = Generator.seeded("same").choose_head()
    assert left == right
