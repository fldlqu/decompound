# German compound morphology and orthography

Strict linearization is intentionally conservative: it realizes only morphology
stored on structured lexemes and composition steps.

## Linking elements

The model can represent zero linking and alphabetic linking forms including:

```text
Ø, -s-, -es-, -n-, -en-, -e-, -er-
```

A lexeme stores all licensed alternatives in `linking_forms` and identifies a
`preferred_linking_form`. A `Step` may explicitly select one licensed alternative
through `linking_form`; otherwise the preferred form is used.

The selected linking form belongs morphologically to the left constituent. It is
not an independent semantic component and does not affect `--len` counting.

`Step.__post_init__` rejects:

- a linking form absent from the modifier's licensed set;
- a lexeme that is not licensed for modifier use.

The strict generator currently uses preferred forms. Per-step selection exists
for future context-specific allomorph rules and normalized external resources.

## Surface order

Internal steps are stored from nearest-to-head to outermost. German spelling is
produced by reversing the steps and concatenating:

```text
outer modifier + ... + inner modifier + rightmost head
```

Each modifier is realized as:

```text
compound stem + selected linking form
```

The rightmost head is realized as its head stem without a modifier link.

## Capitalization

German nouns are capitalized once at the beginning of the completed word.
Lexeme records keep capitalized citation/stem forms for readability. During
linearization, the initial letter of every constituent is lowercased, all forms
are concatenated, and the initial letter of the complete noun is uppercased.
Internal characters—including umlauts and `ß`—are preserved.

## Unicode

All constituent forms and final output are normalized to Unicode NFC. This
ensures that visually identical decomposed and precomposed umlaut spellings do
not produce inconsistent output.

## Compound-boundary consonants

Modern German orthography preserves three identical consonants where compound
constituents meet. The linearizer therefore performs direct concatenation and
does not delete a consonant, for example:

```text
Schiff + Stoff -> Schiffstoff
```

## Hyphens and spaces

The strict default produces one alphabetic word:

- no spaces;
- no explanatory punctuation;
- no hyphens.

German hyphenation is useful or required in some constructions involving
abbreviations, digits, names, or readability conventions. Those constructions
are outside the current curated noun-only core. The generator must not introduce
a hyphen merely to repair an otherwise unsupported entry.

## Validation

Morphological validation checks:

- modifier-role permission;
- head-role permission;
- membership of every selected linking form in the modifier's licensed set;
- alphabetic modifier and head realizations;
- capitalized, NFC-normalized, single-word output.

Semantic relation validation and morphological validation are separate layers:
a type-correct combination can still be morphologically rejected, and licensed
morphology does not by itself prove a semantic relation.
