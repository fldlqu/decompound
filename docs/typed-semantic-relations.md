# Typed semantic relation system

`decompound` treats semantic composition as a small typed grammar rather than as
unrestricted noun concatenation.

## Signature

Every `Rule` has the signature:

```text
(modifier_type, head_type) -> result_type
```

and carries:

- a `Relation` label describing the interpretation;
- a gloss template containing both `{modifier}` and `{head}`;
- a `recursive` marker used only for closed `(T, T) -> T` rules.

A rule is applicable exactly when both input types match. Checking only the
modifier or only the head is insufficient.

## Semantic types

The controlled ontology currently contains:

| Type | Intended scope |
| --- | --- |
| `SUBJECT` | topic or abstract subject matter |
| `ACTIVITY` | intentional or organized activity |
| `PROCESS` | event, procedure, inspection, processing |
| `SYSTEM` | organized technical or conceptual system |
| `INSTITUTION` | office, authority, administrative unit |
| `DOCUMENT` | plan, law, report, regulation |
| `ARTIFACT` | physical or designed object |
| `LOCATION` | place or facility |
| `MATERIAL` | substance or processable material |

These are generation types, not a complete ontology of German. A lexeme enters
strict generation under one selected sense/type; unrestricted polysemy is not
silently inferred.

## Relations

| Relation | Controlled interpretation |
| --- | --- |
| `CONCERNS` | the head concerns or belongs to the modifier concept |
| `MANAGES` | the institutional head manages the modifier activity/process |
| `REGULATES` | the document head regulates the modifier subject/activity |
| `EXAMINES` | the process head examines the modifier subject/activity/process |
| `USED_FOR` | the system head is used for the modifier activity |
| `LOCATED_AT` | the head is associated with a modifier location |
| `PROCESSES` | the system head processes the modifier subject/material |

A relation label alone is not a license. The complete typed signature is the
license. For example, `REGULATES` is currently defined for subject/document and
activity/document input pairs; it is not automatically valid for every pair of
nouns that could be described with the verb “regulate”.

## Result-type inheritance

German nominal compounds are right-headed, so most controlled rules preserve
the broad type of the head:

```text
SUBJECT  + DOCUMENT    -> DOCUMENT
ACTIVITY + SYSTEM      -> SYSTEM
PROCESS  + INSTITUTION -> INSTITUTION
```

The explicit `result_type` is nevertheless stored instead of being inferred.
This makes type changes representable and lets validation verify every edge.

## Recursive relations

A rule marked `recursive=True` must satisfy:

```text
(T, T) -> T
```

`Rule.__post_init__` rejects any recursive rule that is not closed. The core
relation audit additionally rejects duplicate typed relation identities and
multiple closure rules for the same semantic type.

The safe-recursion module then adds the stronger requirement that a non-empty
modifier pool exists for each closure rule used as a length witness.

## Indexes and queries

`relations.py` exposes:

- `BY_HEAD[T]` for choosing rules compatible with a current compound;
- `BY_SIGNATURE[(modifier_type, head_type)]` for exact two-input lookup;
- `applicable_rules(modifier_type, head_type)` as the public query;
- `CLOSURE_RULE[T]` for audited recursive witnesses.

Generation uses the head index and filters out rules whose modifier pools are
empty. Validation calls `Rule.accepts` on the actual modifier and current head
result types.

## Interpretation

`Rule.interpret(modifier=..., head=...)` produces a compositional gloss. Folding
this operation from the innermost step to the outermost recovers an explanation
for the full right-branching tree.

Glosses are explanatory witnesses for the controlled relation; they are not
claims about a unique dictionary definition or preferred translation.
