# External evidence and linguistic limitations

The curated offline grammar is the complete authoritative generation source.
The CLI has no external-resource configuration or resource-check command.

## Application-supplied evidence

Library applications may use their own dictionaries, corpora, splitters,
lemmatizers, or language models outside the package. External lexical evidence
cannot directly become a strict `Lexeme`. Admission additionally requires
project-approved:

- semantic type;
- compound stem;
- complete licensed linking-form set;
- preferred linking form;
- head/modifier role permissions;
- provenance and, where available, sense identity.

The generic `ExternalCandidate`, `NormalizationSpec`, and `normalize_candidate`
APIs model this boundary without depending on a specific external database.
Splitter diagnostics are forcibly non-authoritative.

## Linguistic limitations

A successful output is guaranteed to be a typed, right-headed, morphologically
licensed compound inside the controlled grammar. It is not guaranteed to be:

- dictionary-attested;
- corpus-frequent;
- conventional or idiomatic;
- stylistically elegant;
- easy to process at large length;
- assigned the same preferred interpretation by every speaker;
- pragmatically appropriate outside its generated relation gloss;
- evidence that arbitrary German noun concatenation is acceptable.

The semantic ontology is intentionally broad and small. Relation templates give
controlled compositional interpretations, not full world knowledge. Curated
linking forms cover only included noun senses; the project does not infer general
German linking morphology from spelling.

## Infinite and physical limits

Infinite mode means indefinitely repeatable production of another valid finite
state. It never creates an actually completed infinite word. Memory, CPU time,
terminal width, pipe capacity, and operating-system limits remain physical
constraints. Applications should impose operational bounds suitable for their
environment.

## Accurate result wording

Documentation and integrations should describe output as:

> a morphologically and semantically licensed German compound in decompound's
> controlled grammar

They should not describe validation as dictionary attestation, corpus proof, or
universal native-speaker approval.
