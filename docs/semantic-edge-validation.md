# Semantic relation-edge validation

A compound is valid only if every inner-to-outer composition edge satisfies its
complete typed relation signature. Validating the final type alone is
insufficient.

## Fold order

A flat `Compound` stores steps nearest-to-head first. Semantic validation begins
with:

```text
current_type = head.semantic_type
```

For each step numbered from one:

1. require `rule.head_type == current_type`;
2. require `modifier.semantic_type == rule.modifier_type`;
3. call `rule.accepts(modifier_type, current_type)`;
4. record a successful `EdgeValidation`;
5. set `current_type = rule.result_type`.

After the final edge, the folded type must equal `compound.semantic_type`.

## Edge report

Every successful edge produces:

```text
index
modifier
relation
input_head_type
modifier_type
result_type
valid
```

`ValidationReport.edges` contains these records in inner-to-outer order. For an
N-component compound it contains exactly `N-1` records. A one-component compound
has an empty edge report and inherits the head type directly.

## Failure localization

Errors identify the exact one-based edge number. Examples:

```text
edge 3: rule expects head type document, got system
edge 2: modifier Amt has type institution, expected activity
```

This makes malformed externally constructed structures diagnosable without
relying on the generator that would normally prevent them.

## Independent validation

`Compound.extend` performs local checks while building an interactive state, and
`SemanticPlanner` admits only typed transitions. `validate_semantic_edges` still
recomputes the entire fold independently because:

- callers can instantiate immutable dataclasses directly;
- serialized or externally adapted structures may bypass builder methods;
- future regressions in planning should not redefine validity;
- contract fulfilment needs an explicit post-condition check.

## Separation from morphology

Semantic edge validation does not inspect linking allomorphs or spelling.
Morphological validation follows as a separate layer in `validate`. A relation
edge can be semantically typed yet morphologically unrealizable, and a
morphologically well-formed concatenation can lack a licensed semantic edge.
