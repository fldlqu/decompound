# Rich-planning failure and safe-skeleton fallback

Exact-length generation has two construction strategies with different roles:

1. **constrained DP** chooses among the full typed relation graph for variety;
2. **safe skeleton** is the constructive total fallback that preserves the hard
   arbitrary-finite-length guarantee.

## Trigger

`SemanticPlanner.plan` raises `PlanningError` when the selected head cannot reach
the requested target type in exactly the required number of steps through the
currently available rich transition graph.

Possible causes include:

- optional/custom lexical filtering emptied required modifier pools;
- an application supplied an incomplete relation graph;
- future non-type-preserving rules make an exact step count unreachable;
- a resource adapter failed and removed enrichment candidates;
- curated data changed while the safe core remained intact.

Generator input errors are not fallback triggers. Invalid lengths and unknown or
unsupported target types are reported to the caller.

## Fallback algorithm

After target and head selection, if rich planning raises `PlanningError`:

```text
current_type = head.semantic_type
repeat N - 1 times:
    step = safe_step(current_type)
    append step
    current_type = step.rule.result_type
```

Every safe step has signature `(T, T) -> T` and a non-empty modifier pool. Since
selectable head types are audited against safe skeletons at import time, each
iteration is total and preserves the target type.

The fallback constructs exactly one head and `N-1` steps, so it still fulfils the
component-count contract.

## Provenance

Every generated `Compound` carries `GenerationMetadata`:

```text
strategy
fallback_used
fallback_reason
```

Normal contract generation records:

```json
{
  "strategy": "constrained-dp",
  "fallback_used": false,
  "fallback_reason": null
}
```

A fallback result records:

```json
{
  "strategy": "safe-skeleton",
  "fallback_used": true,
  "fallback_reason": "rich semantic planner found no exact path"
}
```

Default word-only output remains unchanged. `--json` and `--explain` expose this
provenance so applications and tests can distinguish variety-oriented planning
from guaranteed fallback generation.

## Failure after fallback

Failure of `safe_step` for a selectable head indicates a broken core invariant,
not an ordinary search miss. Import-time head audits and safe-skeleton tests are
intended to detect that configuration error before generation.

The generator deliberately catches only `PlanningError`. It does not broadly
catch every exception and hide programming, morphology, or data-integrity bugs
behind a fallback result.

## Guarantee separation

The rich planner is responsible for diversity and future multi-type paths. The
safe skeleton is responsible for total finite extensibility. Independent
validation remains responsible for checking the completed structure. No one
layer is treated as proof of all properties.
