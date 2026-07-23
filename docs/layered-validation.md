# Layered validators

Validation is an ordered independent pipeline rather than one undifferentiated
boolean check. Each layer has a narrow responsibility and produces an auditable
success record.

## Order

Full `validate` runs exactly:

```text
structure -> semantics -> morphology -> orthography
```

A layer runs only after all preceding layers succeed. Failure raises
`ValidationError` immediately, with either a layer prefix or a localized semantic
edge number. Invalid compounds do not receive partially successful reports.

## Structure layer

`validate_structure` checks:

- canonical component count `1 + len(steps)`;
- agreement with `Compound.component_count`;
- surface-order traversal size;
- immutable head is the rightmost component;
- optional exact expected component count.

It does not inspect relation meanings, linking forms, or spelling.

## Semantics layer

`validate_semantics` folds every inner-to-outer edge and checks:

- current head type equals the rule's head input;
- modifier type equals the rule's modifier input;
- the complete rule signature accepts both inputs;
- propagated result type equals the compound's declared final type.

It returns the detailed `EdgeValidation` tuple separately from its layer record.

## Morphology layer

`validate_morphology` checks:

- rightmost lexeme is head-licensed;
- every modifier is modifier-licensed;
- every selected linking allomorph is licensed by that modifier;
- complete component realization succeeds;
- morphology preserves semantic component count.

Morphology errors are wrapped as `ValidationError` with a `morphology:` prefix.
The layer returns the complete `LinearizationResult` for orthographic checking.

## Orthography layer

`validate_orthography(word)` checks that the realized output is:

- non-empty;
- noun-capitalized;
- one alphabetic word;
- produced by the NFC-enforcing morphology pipeline.

Spaces, hyphens, digits, punctuation, and uncapitalized output are rejected under
the strict default representation.

## Report

A successful `ValidationReport.layers` contains four `LayerValidation` records in
pipeline order. Each record contains:

```text
layer
checks
valid
```

JSON analysis exposes these as `validation.layers`, using stable string names:

```text
structure
semantics
morphology
orthography
```

## Public layer APIs

Applications may call layers independently:

```python
validate_structure(compound, expected_length)
validate_semantics(compound)
validate_morphology(compound)
validate_orthography(word)
```

The normal contract boundary calls full `validate`; independent layer calls are
for diagnostics, testing, and trusted application pipelines, not a way to weaken
the generation contract.
