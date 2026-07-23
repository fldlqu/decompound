# Final acceptance criteria

Release `0.1.0` is acceptable only when every mandatory criterion below passes.
The runtime has no external lexical-resource dependency.

## A. Installation and entry points

- Python metadata requires 3.11 or newer.
- Editable installation succeeds with no required third-party runtime package.
- `decompound --help` and `python -m decompound --help` succeed.

## B. Exact contract

For every accepted `N >= 1`, successful contract generation has exactly `N`
semantic lexical components and `N-1` typed relation edges. Invalid lengths fail
with status 2, emit no stdout data, and diagnose on stderr.

Seeded requests are deterministic and isolated from global random state. Each
available target type can be requested explicitly and is preserved by independent
semantic folding.

## C. Linguistic structure and morphology

Every result is right-headed. Every edge matches its rule signature. Every
modifier and head role is licensed. Every selected linking form belongs to its
lexeme. Linking material is excluded from semantic count.

Linearization preserves modern triple consonants, German Unicode letters, NFC,
and one-word noun capitalization. Curated deterministic fixture outputs remain
stable.

## D. Planning, fallback, and unbounded finite construction

The constrained planner returns exact-step paths when feasible. Only planning
failure activates the safe skeleton. Provenance records the selected strategy.
For each public target type, representative thousand-component requests validate
without a hidden linguistic ceiling.

## E. Infinite mode

A blank line performs exactly one verified left extension. The previous structure
becomes the exact right suffix after internal capitalization. Every state is
canonically rebuilt from the head and full step sequence and then independently
validated.

Quit commands, EOF, and Ctrl-C terminate normally. Invalid input does not mutate
state. Non-TTY output is append-only and contains no ANSI or carriage-return
controls. TTY rendering redraws the complete word and finishes with a newline.

## F. Presentation and streams

Default successful stdout is exactly the generated word plus one platform
newline. Diagnostics use stderr and never leak partial result data to stdout.
Human explanation is opt-in. JSON is deterministic, explicit, and carries:

```text
schema = decompound.analysis
schema_version = 1
```

Its validation section exposes ordered structure, semantics, morphology, and
orthography layers.

## G. External-evidence and guarantee boundary

The CLI exposes no external-resource configuration or resource-check command.
Application-supplied external evidence cannot directly enter strict generation
and splitter diagnostics are never authoritative. Documentation does not claim
dictionary attestation, corpus frequency, idiomaticity, universal speaker
agreement, or an actually infinite word.

## H. Quality gates

- all source and tests compile;
- the complete pytest suite passes when test dependencies are available;
- the dependency-free acceptance script passes in restricted environments;
- package architecture/public-export tests pass;
- the runtime package has no required third-party dependency;
- README links every normative specification used by the acceptance contract.

## Release command

Run the dependency-free gate:

```bash
python scripts/acceptance.py
```

Then, when the test extra is available:

```bash
python -m pytest
```

A missing optional test runner is an environment limitation to disclose, not a
reason to weaken or skip the dependency-free release gate.
