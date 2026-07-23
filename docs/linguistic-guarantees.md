# Linguistic guarantee boundary

This document defines exactly what `decompound` promises. These definitions are
part of the public contract: generation and validation must not silently claim a
stronger linguistic status. Operational resource configuration and the
consolidated limitation checklist are in
[`resource-configuration-and-limitations.md`](resource-configuration-and-limitations.md).

## Unit counted by `--len`

`--len N` counts **semantic lexical components** in the compound tree:

- the rightmost head noun counts as one component;
- every prepended modifier lexeme counts as one component;
- linking elements such as `-s-`, `-es-`, `-n-`, `-en-`, `-e-`, and `-er-`
  do not count as components;
- characters, syllables, morphemes, and whitespace-delimited tokens are not the
  contract's counting unit.

Consequently, the orthographic output is one German word even when `N > 1`.
Only integer values `N >= 1` are valid.

## Guaranteed properties

For every successfully generated compound, the controlled grammar guarantees:

1. **Nominal headedness** — the output is a German noun whose grammatical head
   is the rightmost lexical component.
2. **Structural completeness** — the internal representation is a complete
   right-branching binary composition, not an unanalysed concatenated string.
3. **Exact component count** — contract mode contains exactly the requested
   number of semantic lexical components.
4. **Typed compositionality** — every modifier/head edge is licensed by an
   explicit semantic relation signature, and the result has a declared semantic
   type that can be checked before further recursion.
5. **Licensed morphology** — strict core generation uses compound stems and
   linking forms recorded on curated lexemes; it does not invent a linking
   element from an unrestricted spelling heuristic.
6. **Orthographic unity** — default output is one capitalized alphabetic word,
   with no spaces or explanatory punctuation.
7. **Finite extensibility** — for every finite practical `N >= 1`, the core
   grammar has a type-preserving closure path and can construct a result without
   depending on an external NLP service.

Here, “semantic” means interpretable under the project's explicit relation and
gloss templates. It is a controlled computational guarantee, not an unrestricted
judgement about all possible real-world contexts.

## Properties deliberately not guaranteed

The project does **not** guarantee that a generated compound:

- occurs in Duden, a corpus, or any other dictionary;
- is conventional, frequent, stylistically elegant, or suitable for ordinary
  conversation;
- receives an identical preferred interpretation from every native speaker;
- remains easy for humans to process at arbitrary length;
- is pragmatically sensible outside the controlled relation chosen by the
  generator;
- proves that every imaginable German noun combination is acceptable;
- has been approved by an external language model or online service.

German nominal compounding is productive, so a structurally licensed result may
be a new coinage. The accurate description is therefore **a morphologically and
semantically licensed compound in the controlled grammar**, not necessarily an
attested lexical item.

## Strict core versus external enrichment

The curated offline core is the source of the hard guarantee. The package has no
external dictionary runtime dependency. An application-supplied external entry
becomes eligible for strict use only after it has been normalized to the
project's `Lexeme` model and has an explicitly licensed compound stem, linking
form, semantic type, and relation path.

Splitters, lemmatizers, corpus frequencies, dictionaries, and language models may
be used by applications as diagnostics or ranking evidence; none alone is
accepted as proof that a generated compound is valid.

## Resource and infinity boundary

“Infinite mode” means that no linguistic maximum component count is imposed and
each Enter can produce another valid finite state. At every moment the program
holds and displays a finite word. It does not construct an actually completed
infinite string.

Runtime, memory, and terminal output necessarily grow with the number of
components. Operating-system limits and available memory remain physical limits;
they are not linguistic failures.

## Validation interpretation

A successful internal validation means that the compound satisfies this
controlled contract: component count, relation signatures, result types, stored
linking forms, and one-word orthography. It must not be presented as corpus
attestation or universal native-speaker acceptance.
