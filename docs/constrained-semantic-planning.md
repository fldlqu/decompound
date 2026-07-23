# Constrained randomized semantic planning

Exact-size generation plans the semantic structure before orthographic
linearization. It does not concatenate random nouns and attempt to repair the
result afterward.

## Transition graph

Every usable typed rule becomes a `Transition`:

```text
input head type --(relation + non-empty modifier pool)--> output result type
```

A transition is admitted only when:

- the rule is indexed for its declared head type;
- at least one modifier lexeme exists for the rule's modifier type;
- every candidate modifier is role-licensed and has that exact type.

Selecting a transition and one member of its modifier pool creates one `Step`.
Thus every planned step corresponds to one semantic lexical component.

## Exact-length dynamic programming

For a requested final type \(T\), define feasibility layers:

\[
F_0 = \{T\}
\]

and:

\[
F_{k+1} = \{h \mid \exists\ transition\ h \rightarrow o,\ o \in F_k\}
\]

`F_k` is the set of current semantic types that can reach the requested final
type in exactly `k` extension steps.

For a contract of `N` components, the planner needs exactly `N-1` transitions.
It first builds `F_0 ... F_(N-1)`. The selected head type must belong to
`F_(N-1)` or the rich plan is impossible.

## Constrained random construction

After feasibility is proven, construction proceeds from the head outward. With
`k` steps remaining, only transitions whose output belongs to `F_(k-1)` are
eligible. Randomness chooses:

1. one transition among those exact-length-safe candidates;
2. one modifier from that transition's non-empty typed pool.

Therefore random choice can vary the result but cannot consume too many steps,
end at the wrong target type, choose an empty pool, or violate a relation
signature.

The planner returns `GenerationPlan(head, steps, target_type)`. Its component
count is definitionally `1 + len(steps)`.

## Why dynamic programming

The current core relation grammar mostly preserves the head's broad semantic
type, so a simpler loop would often work. The dynamic-programming formulation is
intentional because it remains correct if future approved rules change result
types or introduce multi-type cycles.

It also separates three questions:

- **existence**: does an exact-step typed path exist?
- **selection**: which feasible relation and modifier should randomness choose?
- **realization**: how should the completed plan be spelled?

## Complexity

Let `N` be component count, `|T|` semantic-type count, and `|E|` transition
count. Feasibility construction is `O(N * |E|)` and stores `O(N * |T|)` small
sets. With the controlled finite ontology, both `|T|` and `|E|` are constants,
so planning is linear in `N`.

Step construction is also linear in `N`. No recursive Python calls or
exponential path enumeration are used.

## Failure boundary

`PlanningError` means the rich typed transition graph cannot satisfy the exact
requested path from the selected head. It does not mean the length contract must
fail. Contract generation catches this condition and invokes the separately
proved safe skeleton, which is the subject of the fallback step of the plan.
