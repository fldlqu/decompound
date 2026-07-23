# Safe recursive skeleton

The generator's “every finite length succeeds” claim is constructive. It does
not rely on hoping that random search finds a path.

## Closure witness

For each semantic type selectable as an initial head, the core records a
`SafeSkeleton` containing:

1. a type \(T\);
2. a recursive rule with signature \((T,T) \rightarrow T\);
3. a non-empty, curated pool of modifier lexemes of type \(T\).

The current witnesses are:

```text
INSTITUTION + INSTITUTION -> INSTITUTION
SYSTEM      + SYSTEM      -> SYSTEM
PROCESS     + PROCESS     -> PROCESS
DOCUMENT    + DOCUMENT    -> DOCUMENT
```

These are implemented in `src/decompound/safety.py`. The module validates every
witness at import time: the rule must be recursive, both input types and the
output type must equal the skeleton type, and every modifier in the safe pool
must have that type.

## Existence proof for every finite N

Let \(T\) be the type of a selectable head and let \(S_T\) be its safe skeleton.

- Base case: for \(N=1\), the head itself is a valid compound.
- Inductive step: assume a valid \(N=k\) compound of type \(T\) exists.
  `S_T` has at least one modifier \(m:T\) and a rule \(r:(T,T)\to T\).
  Therefore \(r(m,C_k)\) is a valid compound with \(k+1\) components and still
  has type \(T\).

By induction, a valid structure exists for every finite \(N \ge 1\).

The proof is independent of random selection. Randomness chooses among members
of a non-empty safe modifier pool; it cannot make the witness unavailable.

## Rich generation and fallback

Normal generation first considers every relation whose head input matches the
current type and whose modifier type has at least one available lexeme. This
produces more varied compounds.

If that candidate set is empty—or a relation's modifier pool unexpectedly
becomes empty—the generator calls `safe_step`. The safe step preserves the
current type and restores the invariant that another extension remains possible.

Current curated data normally makes every rich candidate set non-empty, so the
fallback is a defense against future resource filtering, optional adapter
failures, or incomplete custom lexicons. The hard length guarantee belongs to
the safe skeleton, not to the richer candidate set.

## Head audit

`audit_safe_heads(HEADS)` runs when the generator module is imported. If a new
selectable head type is added without a safe skeleton, startup fails immediately
instead of allowing a length-dependent runtime failure.

Types that are not selectable heads do not need closure witnesses. They may be
used as modifiers while the compound result remains in one of the closed head
types.

## Scope of “arbitrary length”

The proof covers every finite mathematical component count. Actual execution is
bounded by finite memory, runtime, and output capacity. Those implementation
limits do not alter the grammatical closure argument.
