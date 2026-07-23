# Mathematical property tests for contract guarantees

Contract correctness is tested as algebraic and metamorphic properties across
many lengths, seeds, and target types, rather than only as a list of example
words.

## Exact-size algebra

For every sampled request with `N >= 1`, tests require:

```text
count_semantic_components(C) = 1 + len(C.steps) = N
len(C.components()) = N
len(validation.edges) = N - 1
```

The requested final semantic type must equal both `C.semantic_type` and the
independently folded validation result.

## Inductive extension property

Starting from a valid one-component state, every sampled extension must preserve:

```text
count(C(k+1)) = count(C(k)) + 1
components(C(k+1)) = (new_modifier,) + components(C(k))
head(C(k+1)) is head(C(k))
type(C(k+1)) = selected_rule.result_type
```

The selected rule must accept the new modifier type and previous result type.
Full layered validation is run after every induction step.

The exact word equation is also checked:

```text
word(C(k+1)) = capitalize(new_modifier_surface) + internalize(word(C(k)))
```

## Determinism property

For equal version, lexicon, request, seed, target type, and length:

```text
generate(request) == generate(request)
linearize(generate(request)) == linearize(generate(request))
```

Seeded contract generation must leave Python's global random state unchanged.

## Linking-element property

For `N` lexical components there are exactly `N-1` modifier-step linking-form
selections, but neither empty nor non-empty linking material changes the semantic
node count. Tests use compounds with many non-empty links to prevent vacuous
success.

## Finite extensibility sampling

A test suite cannot prove execution for every natural number, but it can test the
constructive theorem at strategically varied finite sizes. The always-available
matrix includes one, boundary-small, medium, and thousand-component requests for
every selectable target type.

The proof itself remains in the safe-skeleton specification; testing checks that
the implementation continues to realize its premises and consequences.

## Optional generative framework

`tests/test_properties.py` retains Hypothesis-driven randomized properties when
the optional test dependency is installed. `tests/test_contract_properties.py`
contains deterministic parameterized equivalents that always run, so the core
mathematical property suite is not silently skipped in restricted environments.
