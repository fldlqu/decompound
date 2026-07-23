# decompound

`decompound` generates German nominal compounds from a small, typed and
explicitly curated grammar. It has two modes:

```bash
python -m decompound --len 12 --seed 42
python -m decompound --infinite
```

`--len N` means **N semantic lexical components**. Linking elements such as
`-s-`, `-es-`, `-n-` and `-en-` belong to their left lexeme and are not counted.
The default output is exactly one word on stdout, suitable for shell pipelines.

## What “correct” means

The program guarantees that every result is:

* one orthographic German noun;
* right-headed and structurally complete;
* assembled only with recorded compound stems/linking elements;
* licensed by a typed semantic relation at every binary composition;
* exactly the requested number of components.

It does **not** claim that arbitrarily long output is dictionary-attested or
idiomatic everyday vocabulary. German compounding is productive: long results
are controlled, interpretable coinages. Semantic plausibility is guaranteed
inside this deliberately narrow grammar, not for unrestricted German.

The normative boundary—including the exact meaning of “semantic”, what
validation proves, and what external NLP resources cannot prove—is specified in
[`docs/linguistic-guarantees.md`](docs/linguistic-guarantees.md). The recursive
state equations, tree encoding, invariants, and preservation argument are in
[`docs/formal-recursive-model.md`](docs/formal-recursive-model.md). The
constructive closure witnesses and arbitrary-finite-length proof are documented
in [`docs/safe-recursive-skeleton.md`](docs/safe-recursive-skeleton.md). The
semantic ontology, relation signatures, indexes, and interpretation rules are in
[`docs/typed-semantic-relations.md`](docs/typed-semantic-relations.md). Lexeme
fields, morphology provenance, role permissions, and sense identity are defined
in [`docs/structured-lexeme-model.md`](docs/structured-lexeme-model.md). Linking
allomorph selection, capitalization, Unicode, and compound-boundary spelling are
specified in [`docs/morphology-and-orthography.md`](docs/morphology-and-orthography.md).
Generic external-candidate admission and non-authoritative splitter diagnostics
are covered by
[`docs/external-nlp-resources.md`](docs/external-nlp-resources.md).

## Installation

Python 3.11 or newer is required.

```bash
python -m pip install .
# development
python -m pip install -e '.[test]'
pytest
```

## Contract mode

```bash
decompound --len 1
decompound --len 100 --seed reproducible
decompound --len 20 --type system
decompound --len 8 --show-boundaries
decompound --len 8 --explain
decompound --len 8 --json
```

Generation is iterative. It starts with a head noun and prepends one licensed
modifier per step. Some rules are closure rules:

```text
INSTITUTION + INSTITUTION -> INSTITUTION
SYSTEM      + SYSTEM      -> SYSTEM
PROCESS     + PROCESS     -> PROCESS
DOCUMENT    + DOCUMENT    -> DOCUMENT
```

Therefore, after any valid state there is another valid state of the same type.
By induction, a structure exists for every finite `N >= 1`. Random choices are
made only among valid edges and do not determine whether generation succeeds.

## Infinite mode

With a terminal, the current word is redrawn after each Enter. A new modifier is
inserted on the **left**, because German nominal compounds are right-headed.
Type `q`, `quit`, or `exit`, send EOF, or press Ctrl-C to stop. When stdout is not
a TTY, every version is printed on a separate line and no ANSI escapes are used.

## Architecture

* `model.py` — immutable lexemes, rules, steps and compounds
* `lexicon.py` — curated stems, semantic types and linking allomorphs
* `relations.py` — typed relation signatures and indexes
* `safety.py` — constructive recursive closure witnesses
* `planning.py` — constrained exact-step semantic planning
* `generator.py` — finite and incremental generation
* `contract.py` — exact-length request/result service
* `morphology.py` — spelling and boundary rendering
* `validation.py` — independent structural/type checks
* `adapters/` — optional external resource integrations
* `cli.py` — contract, interactive and diagnostic interfaces

The complete package map, dependency direction, public API, execution flows, and
extension rules are documented in [`docs/architecture.md`](docs/architecture.md).
The library and CLI semantics of exact-length generation are specified in
[`docs/contract-mode.md`](docs/contract-mode.md). Target semantic-type and
rightmost-head selection are defined in
[`docs/head-and-target-selection.md`](docs/head-and-target-selection.md). The
exact-step dynamic program and constrained random transition selection are in
[`docs/constrained-semantic-planning.md`](docs/constrained-semantic-planning.md).
Fallback triggers, the safe construction algorithm, and generation provenance
are specified in
[`docs/rich-planning-fallback.md`](docs/rich-planning-fallback.md). Exact
semantic-node counting and its independent consistency checks are defined in
[`docs/component-count-validation.md`](docs/component-count-validation.md).
Per-edge relation folding, reports, and localized failures are specified in
[`docs/semantic-edge-validation.md`](docs/semantic-edge-validation.md). Explicit
link allomorph application and the auditable spelling pipeline are defined in
[`docs/linearization-pipeline.md`](docs/linearization-pipeline.md). CLI stdout,
stderr, and exit-status behavior is specified in
[`docs/cli-stream-contract.md`](docs/cli-stream-contract.md). The Enter-driven
state machine, input classification, and termination behavior are defined in
[`docs/infinite-interaction-protocol.md`](docs/infinite-interaction-protocol.md).
The realizable relation-option index, randomized selection, and safe total
fallback are specified in
[`docs/legal-extension-selection.md`](docs/legal-extension-selection.md). The
exact structural and orthographic invariant for adding one new leftmost component
is defined in
[`docs/left-extension-invariant.md`](docs/left-extension-invariant.md). Canonical
reconstruction of the complete state after every extension is specified in
[`docs/complete-state-rebuild.md`](docs/complete-state-rebuild.md). TTY line
replacement, flushing, termination newline, and non-TTY append-only rendering are
defined in [`docs/tty-redraw.md`](docs/tty-redraw.md). The optional human
explanation and versioned machine-readable schema are specified in
[`docs/explanation-and-json-output.md`](docs/explanation-and-json-output.md).
The ordered structure, semantics, morphology, and orthography validation layers
are specified in [`docs/layered-validation.md`](docs/layered-validation.md).
Algebraic, inductive, deterministic, and finite-extensibility test properties are
documented in
[`docs/property-based-contract-testing.md`](docs/property-based-contract-testing.md).
Curated regression examples for German linking forms, ordering, spelling,
Unicode, and interpretation are listed in
[`docs/deterministic-linguistic-fixtures.md`](docs/deterministic-linguistic-fixtures.md).
UTF-8 streams, platform newlines, terminal controls, entry points, and process
exit codes are documented in
[`docs/cli-cross-platform.md`](docs/cli-cross-platform.md). External-candidate
admission boundaries and consolidated linguistic limitations are in
[`docs/resource-configuration-and-limitations.md`](docs/resource-configuration-and-limitations.md).
The release gate and complete final acceptance checklist are defined in
[`docs/final-acceptance.md`](docs/final-acceptance.md); the dependency-free gate
runs with `python scripts/acceptance.py`.

To expand strict generation, do not add a bare word list. Add a `Lexeme` with an
attested compound stem/linking form, assign a semantic type, and ensure at least
one relation accepts that type. New relation cycles must preserve their declared
result type if they are marked recursive.

## Limits and resource safety

Runtime and output size are necessarily linear in `N`; asking for millions of
components can exhaust memory or flood a terminal. The library deliberately has
no hidden linguistic maximum. Calling applications should enforce a limit suited
to their environment.
