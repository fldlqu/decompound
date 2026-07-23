# Project architecture

`decompound` is organized as a dependency-free runtime core with generic
external-evidence boundaries and a thin CLI. The architecture keeps the hard
generation guarantee independent of network access, licensed datasets, and
third-party NLP packages.

## Package layout

```text
pyproject.toml                 packaging, extras, CLI entry point, test config
README.md                      user-facing installation and usage
docs/                          normative design and linguistic documentation
src/decompound/
  __init__.py                  stable public library surface
  __main__.py                  `python -m decompound` entry point
  model.py                     immutable domain objects and local invariants
  lexicon.py                   curated structured core lexicon and indexes
  relations.py                 typed semantic grammar and relation indexes
  safety.py                    constructive closure witnesses and head audit
  planning.py                  constrained exact-step semantic path planning
  extension.py                 legal incremental relation-option selection
  rebuild.py                   canonical complete-state reconstruction
  left_extension.py            verified one-component left-state transition
  generator.py                 finite generation and incremental extension
  contract.py                  exact-length request/result service boundary
  morphology.py                linking-form realization and orthography
  validation.py                independent post-construction checks
  interaction.py               transport-independent infinite input protocol
  terminal.py                  TTY redraw and non-TTY line rendering
  presentation.py              versioned JSON and human explanation views
  platform.py                  cross-platform text-stream configuration
  cli.py                       argument parsing, rendering, interaction
  adapters/
    base.py                    generic external-candidate admission boundary
    splitter.py                non-authoritative splitter diagnostics
tests/                         unit, property, linguistic, and CLI tests
```

## Dependency direction

The intended dependency graph is acyclic at the architectural level:

```text
model
  ↑
lexicon     relations
  ↑            ↑
  └── safety ──┘
          ↑
      generator
          ↑
       contract
          ↑
       validation ← morphology
          ↑           ↑
          └──── cli ──┘

model ← adapters/base
model ← adapters/splitter (protocol-only diagnostics)
```

More concretely:

- `model` imports no project module;
- `lexicon` and `relations` depend only on `model`;
- `safety` combines curated lexemes and recursive rules;
- `planning` proves exact-step typed feasibility and selects valid transitions;
- `generator` consumes plans, indexes, and safety witnesses;
- `contract` validates exact-length requests and independently verifies results;
- `morphology` realizes model structures without choosing semantics;
- `validation` checks structures independently of generation choices;
- `cli` orchestrates library calls but contains no linguistic rules;
- generic adapters define evidence boundaries without importing any third-party
  NLP package.

## Public API

`decompound.__init__` exposes the supported library primitives:

```python
Generator
Compound, Step, Lexeme, Rule
SemanticType, Relation, Gender, Register
linearize, boundaries
validate, ValidationError
```

Implementation indexes and curated data remain importable from their modules for
advanced use, but are not promised as the minimal stable surface.

## Core versus optional dependencies

The runtime has no third-party dependency. Optional extras are limited to
development tooling:

```text
test  -> pytest, hypothesis
dev   -> test extra plus build tooling
```

No external lexical database, licensed dataset, or NLP runtime is bundled or
required.

## Data ownership

Core lexical and relation data currently live as typed Python records. This gives
import-time validation, enum checking, and straightforward packaging. If the
curated dataset grows substantially, serialization may move to package resources,
but loading must still produce the same audited domain objects before generation.

External resource records remain evidence outside the core lexicon until explicit
normalization supplies missing morphology and permissions.

## Execution flows

### Contract mode

```text
CLI parse -> ContractRequest -> generate_contract -> Compound -> linearize -> stdout
```

### Infinite mode

```text
CLI parse -> Generator.start -> display
Enter -> Generator.extend -> validate -> linearize -> redraw/display -> repeat
```

### Application-supplied external evidence

```text
application source -> ExternalCandidate
                   -> explicit normalization -> Lexeme (application use)
```

The CLI has no external-resource options and never merges external candidates
into the strict core.
## Testing boundaries

- model tests verify immutable tree encoding and local invariants;
- lexicon/relation/safety tests audit the controlled grammar;
- morphology tests verify stored allomorph realization and spelling;
- generator/property tests verify exact length and extension invariants;
- adapter tests verify generic candidate admission and non-authoritative split diagnostics;
- CLI tests verify stdout/stderr and TTY-independent behavior.

## Extension rules

When adding a core modifier:

1. create a structured, sourced `Lexeme`;
2. record licensed compound allomorphs rather than guessing;
3. map one controlled sense to a semantic type;
4. ensure a typed relation accepts it;
5. add linguistic and generation tests.

When adding a selectable head type, also provide and test a safe skeleton. When
adding an adapter, return evidence-only candidates and preserve lazy imports.
