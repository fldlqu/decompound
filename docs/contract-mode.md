# Exact-length contract mode

Contract mode is the public promise behind:

```bash
decompound --len N
```

## Request contract

`N` is an integer number of semantic lexical components and must satisfy
`N >= 1`. Boolean values are rejected by the library even though Python treats
`bool` as a subclass of `int`.

The library API is:

```python
from decompound import ContractRequest, generate_contract

result = generate_contract(ContractRequest(length=12, seed="example"))
compound = result.compound
```

`ContractRequest` validates inputs before generation. `ContractResult` retains
the request next to the immutable compound and exposes its component count.

## Fulfilment pipeline

```text
ContractRequest
  -> seeded Generator
  -> iterative exact-step construction
  -> independent validate(expected_length=N)
  -> ContractResult
```

The service does not trust generator construction alone. It runs independent
structural, relation, morphology, and exact-count validation before returning.
An internal mismatch becomes `ContractError` rather than leaking an invalid
result.

## Determinism

The optional seed initializes a private `random.Random` instance. The same
project version, curated data, request length, and seed produce the same
compound. Global random state is not read or modified.

A seed does not alter validity. It only selects among candidates already
licensed by the typed grammar or safe skeleton.

## Complexity

For `N` components, contract construction accumulates `N-1` steps in a list and
freezes the sequence once. Model construction, validation, and linearization are
each linear in `N`. The implementation does not recursively call Python and does
not depend on backtracking through an exponential search tree.

The resulting string length is data-dependent but also grows at least linearly
with the number of non-empty lexical stems. Callers remain responsible for
choosing resource limits suitable for their environment.

## CLI behavior

With no analysis option, successful contract mode writes exactly one generated
word followed by a newline to stdout:

```bash
decompound --len 8 --seed demo
```

Diagnostics and argument errors are handled separately from the successful word
stream. Optional `--json`, `--explain`, and `--show-boundaries` intentionally
select alternate output formats.

## Guarantee source

Exact length follows from constructing one head plus exactly `N-1` extension
steps. Availability for every finite `N` follows from the safe recursive
skeleton. Type and morphology correctness follow from independent validation.
The contract does not imply dictionary attestation or conventional usage.
