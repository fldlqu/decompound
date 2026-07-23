# Complete-state rebuilding after extension

The displayed word is always rebuilt from the complete canonical compound model.
Infinite mode never treats the previously displayed string as authoritative
state and never constructs output by merely prefixing text to a cached word.

## Canonical state

The only linguistic state required to reconstruct a compound is:

```text
head
steps_inner_to_outer
```

Every step contains its modifier, typed relation, and selected linking form.
Generation metadata is retained on the `Compound` but does not affect spelling.

## Rebuild operation

`rebuild(compound)` independently derives:

1. a frozen copy of all steps in inner-to-outer order;
2. all lexical components in surface order;
3. all realized stems and linking forms;
4. the complete NFC-normalized word.

It returns `RebuildResult` with:

```text
compound
components
steps_inner_to_outer
realization
word
component_count
```

## Consistency checks

Before returning, rebuilding requires:

- rebuilt component order equals `compound.components()`;
- rebuilt count equals `compound.component_count`;
- morphological realization has one record per rebuilt component;
- realized lemma order equals rebuilt lexical lemma order.

These checks detect omissions, duplication, ordering errors, and divergence
between model traversal and morphology.

## Extension integration

`extend_left` rebuilds both the previous state and the newly extended state from
their full models. The exact left-extension word equation remains a checked
post-condition, but it is not the implementation used to produce the new word.

This distinction matters:

- **production**: rebuild from `head + all steps`;
- **verification**: compare that rebuilt result to `new modifier + old word`.

Therefore a stale or externally supplied previous display string cannot corrupt
the next state.

## Interaction integration

Infinite CLI mode displays `LeftExtensionResult.word`, which comes from the new
`RebuildResult`. Each Enter consequently reprocesses every selected linking form,
component order, casing rule, and normalization rule for the complete state.

The approach is linear in the current component/character count per interactive
redraw. This intentionally favors transparent canonical correctness over a
fragile incremental string cache. Contract generation still performs one final
linear rebuild after planning.
