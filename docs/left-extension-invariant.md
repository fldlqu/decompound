# Verified left-extension invariant

Every infinite-mode Enter action adds exactly one new outermost modifier. In the
German surface word this is exactly one new lexical component on the left.

## Structural operation

For a current flat state:

```text
Compound(head=h, steps=(s1, ..., sk))
```

and a legal new step `s(k+1)`, left extension produces:

```text
Compound(head=h, steps=(s1, ..., sk, s(k+1)))
```

Because `components()` reverses steps before appending the head, the resulting
surface-order component tuple is:

```text
(new_modifier,) + old_components
```

The old rightmost head object and every old step remain unchanged.

## Word equation

Let `M` be the new modifier stem plus its selected linking form, and let `W` be
the previous capitalized standalone compound. Then:

```text
new_word = capitalize_initial(M) + internalize(W)
```

`internalize(W)` lowercases only the initial character that ceases to be the
initial of the complete German noun. All remaining old characters are preserved
exactly.

Thus the often-used case-insensitive suffix property is strengthened to an exact
orthographic equation rather than tested only with `.lower().endswith(...)`.

## Verified transaction

`extend_left(compound, step)` returns `LeftExtensionResult` only after checking:

1. component count increased by exactly one;
2. the rightmost head is the identical object;
3. all previous steps remain an unchanged prefix;
4. the selected step is the sole new final stored step;
5. surface-order components equal `(new_modifier,) + old_components`;
6. final spelling satisfies the exact word equation.

The old immutable `Compound` remains available as `result.previous`; the new
state is `result.compound`.

## Result data

`LeftExtensionResult` records:

```text
previous
compound
step
previous_word
word
added_surface
added_components
```

`added_surface` includes the selected linking allomorph. `added_components` is
always one for a successful result; the linking allomorph does not add a node.

## Generator and interaction integration

`Generator.extend_left` selects a legal typed step and invokes the verified
transaction. `Generator.extend` remains a compatibility convenience that returns
only the verified new `Compound`.

Infinite CLI mode consumes `Generator.extend_left` and displays its already
verified complete `word`, then independently validates the new compound before
publication.
