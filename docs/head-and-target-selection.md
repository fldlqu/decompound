# Head and target semantic-type selection

Every generated German nominal compound inherits its broad semantic category
from the rightmost head through the typed relation chain. Head selection is
therefore also target-type selection.

## Available target types

The core currently has selectable heads for:

```text
institution
system
process
document
```

`Generator.available_head_types()` derives this set from `HEADS` and returns it
in stable `SemanticType` enum order. Modifier-only types such as `subject`,
`activity`, and `material` cannot be requested as final result types until an
explicit head and safe recursive skeleton are added for them.

## Selection algorithm

`Generator.choose_target_type(requested)` behaves as follows:

1. derive types having at least one selectable head;
2. if no type was requested, choose uniformly from those available types using
   the generator's private seeded random source;
3. if a string was requested, normalize it through `SemanticType`;
4. reject unknown types;
5. reject known types that have no selectable head.

`Generator.choose_head(target_type)` then filters `HEADS` to entries that:

- have exactly the resolved semantic type;
- are explicitly `allowed_as_head`.

It chooses uniformly among that non-empty head pool. `Generator.start` wraps the
selected head in the base one-component `Compound`.

## Contract and CLI control

The library supports:

```python
ContractRequest(12, seed="demo", target_type=SemanticType.SYSTEM)
ContractRequest(12, seed="demo", target_type="system")
```

The CLI equivalent is:

```bash
decompound --len 12 --type system --seed demo
```

The resulting compound's semantic type is guaranteed to be `system`, because
all system composition rules preserve their declared result type and the safe
fallback is `(SYSTEM, SYSTEM) -> SYSTEM`.

The same option applies to infinite mode:

```bash
decompound --infinite --type document
```

## Determinism and distribution

Target-type and head choices consume the same private random stream as later
modifier choices. Given the same version, data, seed, length, and target option,
the full result is reproducible.

When no target is supplied, selection is uniform over available semantic types,
not over all heads. This prevents a type with more synonym heads from receiving
a larger probability merely because its curated head pool is larger. Head choice
is then uniform within the chosen type.

## Safety precondition

Selectable head types are audited against `SAFE_SKELETONS` at generator import.
Consequently, choosing a target type also chooses a type for which arbitrary
finite extension has a constructive witness.
