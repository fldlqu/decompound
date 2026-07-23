# Exact semantic-component count validation

Contract length is verified from the internal lexical structure, never inferred
from characters, substring matches, splitter output, or linking elements.

## Counting definition

For a `Compound(head, steps)`:

```text
semantic component count = 1 + len(steps)
```

The one is the immutable rightmost head. Every `Step` contains exactly one
modifier lexeme and therefore contributes exactly one additional semantic node.
The selected linking form is a field of that step and contributes zero nodes.

`count_semantic_components(compound)` implements this structural definition.

## Independent consistency checks

`validate_component_count(compound, expected)` checks:

1. `expected` is an integer and not a Boolean;
2. `expected >= 1`;
3. structural count `1 + len(steps)` equals `expected`;
4. `len(compound.components())` agrees with the structural count.

Full `validate` additionally confirms that `Compound.component_count` agrees
with the structural calculation. These redundant views make an accidental model
or traversal regression observable instead of trusting a single property.

## Contract boundary

`generate_contract` explicitly calls `validate_component_count` before full
semantic and morphological validation. A mismatch is wrapped as `ContractError`
and no result is returned.

The resulting `ValidationReport` records:

```text
components
expected_components
count_valid
characters
valid
```

Character count is diagnostic only and has no role in fulfilling `--len`.

## Failure examples

A three-component structure requested as length four fails with:

```text
expected 4 semantic components, got 3
```

Invalid expected counts such as zero, negative integers, floats, strings, and
Booleans fail before comparison.

## Complexity

The canonical structural count is `O(1)` because steps are stored as a tuple.
The independent surface-order traversal check is `O(N)`. Contract validation is
already linear because it validates every relation and realizes the word, so the
additional count consistency check does not change asymptotic complexity.
