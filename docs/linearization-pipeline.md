# Linking-form application and linearization pipeline

Orthographic output is produced only after the semantic structure is complete.
The pipeline is explicit and auditable; linking elements are neither guessed
from the finished string nor represented as lexical nodes.

## Pipeline stages

`linearization_result(compound)` performs these stages in order:

1. **role validation** — the rightmost lexeme must be head-licensed and every
   step modifier must be modifier-licensed;
2. **surface ordering** — reverse the stored inner-to-outer steps, then append
   the immutable rightmost head;
3. **allomorph application** — append each step's explicitly selected licensed
   linking form to that modifier stem;
4. **internal casing** — lowercase only the initial character of each component
   after it becomes word-internal;
5. **concatenation** — join all component surfaces without spaces or hyphens;
6. **noun capitalization** — uppercase the first character of the complete word;
7. **NFC normalization** — normalize lexical inputs and final output;
8. **orthographic post-condition** — require one non-empty alphabetic word.

No consonant deletion occurs. Modern German triple-consonant spellings are
preserved by ordinary concatenation.

## Auditable realization

Each output component is represented as `RealizedComponent`:

```text
lemma
stem
linking_form
surface
is_head
source_step_index
```

`source_step_index` is one-based in the compound's stored inner-to-outer order.
Surface ordering reverses modifier steps, so those indexes normally descend from
`N-1` to `1`, followed by the head with no step index.

`LinearizationResult` contains the realized component tuple and final word. Its
`linking_forms` property exposes modifier links in surface order.

## Linking-form guarantees

A modifier realization is exactly:

```text
NFC(modifier.stem) + NFC(step.effective_linking_form)
```

The effective link must occur in the lexeme's curated `linking_forms`. The empty
string is a normal licensed allomorph and contributes no characters. A link may
contain several letters but contributes zero semantic components.

## Boundary diagnostics

`boundaries(compound)` consumes the same realized component records as final
linearization. For example:

```text
Arbeit[s]+Amt
```

This prevents explanatory boundaries and actual output from silently using
different morphology paths.

## Validation integration

Full validation runs `linearization_result` and checks that its component-record
count equals the independent semantic-node count. It then checks capitalization,
alphabetic one-word spelling, and character count.

Semantic relation validation remains separate and runs before morphology.
Consequently, successful spelling cannot compensate for an invalid relation,
and a valid typed relation cannot bypass an unlicensed linking form.

## Complexity

Component realization and concatenation are linear in component and character
count. The implementation uses list/tuple accumulation and one final join; it
does not repeatedly rebuild the growing word during planning.
