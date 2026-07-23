import random

import pytest

from decompound import (
    ContractError,
    ContractRequest,
    generate_contract,
    linearize,
    validate,
)


@pytest.mark.parametrize("length", [1, 2, 17, 1000])
def test_contract_service_returns_exact_valid_result(length):
    request = ContractRequest(length, seed="contract")
    result = generate_contract(request)
    assert result.request is request
    assert result.component_count == length
    assert validate(result.compound, length).valid
    assert linearize(result.compound).isalpha()


@pytest.mark.parametrize("length", [0, -1, 1.2, True, "4", None])
def test_contract_request_rejects_invalid_lengths(length):
    with pytest.raises(ContractError, match="integer >= 1"):
        ContractRequest(length)  # type: ignore[arg-type]


def test_contract_seed_does_not_touch_global_random_state():
    random.seed(90210)
    expected = random.random()
    random.seed(90210)
    generate_contract(ContractRequest(50, seed="private"))
    assert random.random() == expected


def test_contract_is_reproducible():
    left = generate_contract(ContractRequest(80, seed="same"))
    right = generate_contract(ContractRequest(80, seed="same"))
    assert left.compound == right.compound
    assert linearize(left.compound) == linearize(right.compound)
