# Optional explanation and machine-readable output

Default generation remains word-only. Rich representations are opt-in through
`--explain`, `--json`, or the corresponding library functions.

## Shared validated source

Both representations are derived from `analysis_data(compound)`. That function:

1. performs independent full validation;
2. performs canonical complete-state rebuilding;
3. folds the relation interpretation from the rightmost head outward;
4. emits only JSON-native values.

Presentation does not alter the compound and does not admit unvalidated data.

## Versioned JSON document

`analysis_json` and CLI `--json` emit one compact Unicode JSON object followed by
one newline. The top-level schema identifiers are:

```json
{
  "schema": "decompound.analysis",
  "schema_version": 1
}
```

Version 1 fields are:

```text
schema
schema_version
word
components
component_sequence
boundaries
semantic_type
head
gloss
generation
validation
relations_inner_to_outer
```

`component_sequence` is in surface order and records position, lemma, stem,
selected linking form, realized surface, semantic type, head role, sense ID, and
source. `relations_inner_to_outer` is in model fold order and includes stable
one-based indexes and complete typed signatures.

The serializer uses sorted keys and compact separators, so repeated serialization
of the same compound is byte-for-byte deterministic. Unicode letters are emitted
directly rather than escaped.

Additive fields may be introduced within schema version 1 when existing meanings
remain unchanged. Removing fields or changing their meaning requires a schema
version increment.

## Human explanation

`explanation_lines` and CLI `--explain` return a stable concise summary:

```text
<word>
components: <N>
boundaries: <annotated structure>
type: <final semantic type>
head: <lemma> (<head semantic type>)
gloss: <compositional interpretation>
strategy: <generation strategy>
```

A fallback line is included only when fallback occurred. Human explanation is
not intended as a machine protocol; consumers should use JSON.

## Output-mode exclusivity

`--json`, `--explain`, and `--show-boundaries` are mutually exclusive. Each
replaces default word-only stdout rather than appending to it. Successful modes
write no diagnostics to stderr.

## Library API

The public API exports:

```python
analysis_data(compound)
analysis_json(compound)
explanation_lines(compound)
SCHEMA_NAME
SCHEMA_VERSION
```

This allows applications to consume structured values directly without parsing
CLI text.
