# Structured lexeme model

Strict generation uses noun senses, not bare strings. `Lexeme` records the data
needed to decide whether and how a noun may participate in a compound.

## Fields

| Field | Meaning |
| --- | --- |
| `lemma` | Capitalized German noun citation form |
| `stem` | Capitalized compound stem/allomorph |
| `semantic_type` | Selected controlled sense type |
| `linking_forms` | Non-empty tuple of licensed linking forms |
| `preferred_linking_form` | Form used by deterministic linearization |
| `gender` | Masculine, feminine, neuter, or plural |
| `gloss` | Short explanatory sense gloss |
| `allowed_as_modifier` | Whether the entry may occur left of a head |
| `allowed_as_head` | Whether the entry may be the rightmost head |
| `register` | Neutral, technical, or administrative |
| `source` | Provenance identifier for auditability |
| `sense_id` | Stable optional identifier for this sense/form record |

The model distinguishes `linking_forms` from the preferred form so later
resource adapters can record genuine alternatives without asking the core
linearizer to guess. The current strict generator chooses the preferred form.

## Invariants

`Lexeme.__post_init__` requires:

- non-empty capitalized lemma and stem;
- at least one licensed linking form;
- preferred form membership in the licensed set;
- alphabetic non-empty linking forms;
- at least one permitted syntactic role;
- non-empty provenance.

`modifier_form` refuses to realize a lexeme that is not modifier-licensed.
Selectable heads are stored as explicit head records whose rightmost realization
has no linking element.

## Sense granularity

A surface lemma may have multiple records when senses, semantic types, compound
stems, registers, or role permissions differ. `sense_id`, not surface spelling,
is the intended stable identity. This prevents unrestricted polysemy from
silently licensing a relation.

## Indexes

The curated lexicon exports:

- `LEXEMES`: modifier-capable core records;
- `HEADS`: explicitly selectable rightmost head records;
- `BY_TYPE`: modifier-capable records indexed by semantic type;
- `BY_SENSE_ID`: records indexed by provenance-aware sense identity.

`audit_lexicon()` checks identity uniqueness and role-index consistency at import
time.

## External entries

An external dictionary item is not directly a strict `Lexeme`. An adapter must
normalize and validate its sense, stem, linking forms, role permissions, and
source before it can enter a generation pool. Unknown morphology should remain
outside strict generation rather than being represented as false certainty.
