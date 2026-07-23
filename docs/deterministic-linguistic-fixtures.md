# Deterministic linguistic fixtures

Curated example tests complement broad mathematical properties by pinning down
specific German morphology, spelling, ordering, Unicode, and interpretation
behavior. These fixtures are intentionally deterministic and do not assert that
every generated coinage is dictionary-attested.

## Linking allomorph fixtures

The suite fixes representative licensed cases:

```text
Arbeit + s + Amt   -> Arbeitsamt
Gesetz + es + Text -> Gesetzestext
Behörde + n + Plan -> Behördenplan
Name + ns + Liste  -> Namensliste
Wasser + ø + System -> Wassersystem
```

Boundary diagnostics must expose the same selections:

```text
Arbeit[s]+Amt
Gesetz[es]+Text
Behörde[n]+Plan
Name[ns]+Liste
Wasser+System
```

A second `Name` fixture selects licensed nonpreferred `-n-` and requires
`Namenliste`, demonstrating that explicit step allomorphy overrides preference
without bypassing licensing.

## Right-headed multi-edge fixture

A fixed typed structure encodes an activity modifier nearest to a system head and
a subject modifier outside it:

```text
Daten + Arbeit[s] + System -> Datenarbeitssystem
```

The fixture checks surface component order, boundary rendering, final `SYSTEM`
type, and full validation. This catches accidental reversal of stored
inner-to-outer steps.

## Orthographic fixtures

Modern German retains three identical consonants at compound boundaries:

```text
Schiff + Stoff -> Schiffstoff
```

Unicode fixtures begin with decomposed input and require NFC output while
preserving umlauts and sharp s:

```text
Größe + Prüfung -> Größeprüfung
```

## Interpretation fixture

A fixed two-edge semantic structure folds rule templates in inner-to-outer order.
The resulting gloss is compared exactly, ensuring deterministic compositional
interpretation rather than only checking that argument words occur somewhere.

## Guarantee boundary

These cases are controlled regression examples for the declared grammar. They
establish that known curated allomorphs and orthographic rules remain stable.
They do not claim corpus frequency, universal German linking prediction, or
idiomatic acceptability outside the curated lexicon and relation signatures.
