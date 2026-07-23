# Legal relation selection during infinite extension

Every Enter-driven extension selects from an explicitly enumerated set of
currently realizable typed relation edges. It does not choose a modifier first
and search for a relation afterward.

## Extension option

An `ExtensionOption` pairs:

```text
one typed Rule
one complete non-empty modifier pool
```

Construction verifies that every modifier:

- is licensed for modifier use;
- has exactly the rule's declared modifier type.

The option's applicable current type is `rule.head_type`; applying it produces
`rule.result_type`.

## Enumeration

`legal_extension_options(current_type)`:

1. reads only rules indexed under `BY_HEAD[current_type]`;
2. obtains modifier candidates from `BY_TYPE[rule.modifier_type]`;
3. rechecks role permission and exact modifier type;
4. omits rules with empty realizable modifier pools;
5. preserves curated rule order for deterministic seeded choice.

Consequently, every exposed pair satisfies:

```text
rule.accepts(modifier.semantic_type, current_type)
```

## Random selection

`choose_extension_step` chooses uniformly among legal relation options, then
uniformly within the selected option's modifier pool. This means relation
probability is not accidentally proportional to the number of lexical synonyms
available for its modifier type.

The same private `random.Random` instance used by the generator controls both
choices, preserving reproducibility without touching global random state.

## Total fallback

If the rich option enumeration is empty, selection invokes
`safe_step(current_type)`. Selectable head/result types are import-time audited
to have a constructive `(T, T) -> T` witness and non-empty modifier pool.

An empty rich option set is therefore recoverable. A missing safe witness is a
core configuration error and is not silently ignored.

## Defense in depth

`Generator.next_step` rechecks the chosen step against the actual compound's
current semantic type before returning it. `Compound.extend` checks the same
signature again while constructing the new immutable state. Full validation
later folds every edge independently.

The duplicated checks intentionally separate:

- option-index correctness;
- selector correctness;
- state-transition correctness;
- post-construction validation.

## Import-time audit

`audit_extension_options` inspects every selectable current type. It verifies all
enumerated options and confirms that types without rich options still have a
total safe step. This makes malformed relation or lexicon indexes fail early.
