# External NLP evidence boundaries

The strict grammar works entirely from the curated core lexicon. Generic APIs
allow applications to normalize evidence obtained outside the package.

## Generic candidate boundary

Applications may convert evidence from their own dictionaries, corpora, or NLP
systems into `ExternalCandidate` records containing:

- lemma;
- mapped semantic type, if available;
- source and optional sense identifier;
- gloss;
- confidence level.

An `ExternalCandidate` is deliberately not a `Lexeme`. It has no trusted compound
stem or linking form and cannot enter strict generation directly.

Admission uses `normalize_candidate(candidate, spec)`. A `NormalizationSpec`
records approved morphology and role permissions. Admission requires:

- a mapped or explicitly supplied semantic type;
- confidence above `UNVERIFIED`;
- an explicit stem;
- a non-empty set of licensed linking forms;
- a preferred licensed form;
- modifier/head permissions and provenance.

The resulting `Lexeme` remains subject to the ordinary model, relation,
morphology, and validation rules. The package does not automatically merge
external candidates into its core indexes.

## Splitter diagnostics

`adapters.splitter` defines a protocol for optional compound splitters supplied
by an application. Results are always non-authoritative. Re-splitting may help
inspect surprising boundaries, but it is neither necessary nor sufficient for
validity.

Lemmatizers, corpus frequencies, dictionaries, and language models likewise may
provide diagnostics or ranking evidence. They do not determine linking elements,
semantic relations, or acceptability under the controlled grammar.

## Failure isolation

External application integrations must fail outside the strict core. Missing or
incompatible tools cannot weaken validation, admit unrestricted strings, or make
the safe recursive skeleton unavailable.

No third-party lexical dataset or external NLP runtime is bundled or required.
