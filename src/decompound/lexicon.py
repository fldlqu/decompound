"""Curated core noun-sense lexicon with explicit compound allomorphy."""

from __future__ import annotations

from .model import Gender as G, Lexeme, Register as R, SemanticType as T


def _lexeme(
    lemma: str,
    kind: T,
    *,
    stem: str | None = None,
    links: tuple[str, ...] = ("",),
    preferred: str = "",
    gender: G = G.NEUTER,
    gloss: str,
    modifier: bool = True,
    head: bool = True,
    register: R = R.NEUTRAL,
    sense_id: str | None = None,
) -> Lexeme:
    return Lexeme(
        lemma=lemma,
        stem=stem or lemma,
        semantic_type=kind,
        linking_forms=links,
        preferred_linking_form=preferred,
        gender=gender,
        gloss=gloss,
        allowed_as_modifier=modifier,
        allowed_as_head=head,
        register=register,
        source="core-curated-v1",
        sense_id=sense_id or (
            f"core:{lemma.lower()}:{kind.value}:"
            f"{'modifier' if modifier else 'head'}"
        ),
    )


LEXEMES: tuple[Lexeme, ...] = (
    _lexeme("Arbeit", T.ACTIVITY, links=("s",), preferred="s", gender=G.FEMININE, gloss="work"),
    _lexeme("Forschung", T.ACTIVITY, links=("s",), preferred="s", gender=G.FEMININE, gloss="research"),
    _lexeme("Bildung", T.ACTIVITY, links=("s",), preferred="s", gender=G.FEMININE, gloss="education"),
    _lexeme("Verkehr", T.PROCESS, links=("s",), preferred="s", gender=G.MASCULINE, gloss="traffic"),
    _lexeme("Daten", T.SUBJECT, gender=G.PLURAL, gloss="data"),
    _lexeme("Umwelt", T.SUBJECT, gender=G.FEMININE, gloss="environment"),
    _lexeme("Wasser", T.MATERIAL, gloss="water"),
    _lexeme("Energie", T.SUBJECT, gender=G.FEMININE, gloss="energy"),
    _lexeme("Qualität", T.SUBJECT, links=("s",), preferred="s", gender=G.FEMININE, gloss="quality"),
    _lexeme("Sicherheit", T.SUBJECT, links=("s",), preferred="s", gender=G.FEMININE, gloss="safety"),
    _lexeme("Verwaltung", T.INSTITUTION, links=("s",), preferred="s", gender=G.FEMININE, gloss="administration", register=R.ADMINISTRATIVE),
    _lexeme("Behörde", T.INSTITUTION, links=("n",), preferred="n", gender=G.FEMININE, gloss="authority", register=R.ADMINISTRATIVE),
    _lexeme("Amt", T.INSTITUTION, links=("s",), preferred="s", gloss="office", register=R.ADMINISTRATIVE),
    _lexeme("System", T.SYSTEM, gloss="system", register=R.TECHNICAL),
    _lexeme("Netz", T.SYSTEM, gloss="network", register=R.TECHNICAL),
    _lexeme("Plan", T.DOCUMENT, links=("s",), preferred="s", gender=G.MASCULINE, gloss="plan"),
    _lexeme("Gesetz", T.DOCUMENT, links=("es",), preferred="es", gloss="law", register=R.ADMINISTRATIVE),
    _lexeme("Bericht", T.DOCUMENT, links=("s",), preferred="s", gender=G.MASCULINE, gloss="report"),
    _lexeme("Prüfung", T.PROCESS, links=("s",), preferred="s", gender=G.FEMININE, gloss="inspection"),
    _lexeme("Kontrolle", T.PROCESS, links=("n",), preferred="n", gender=G.FEMININE, gloss="control"),
    _lexeme("Verarbeitung", T.PROCESS, links=("s",), preferred="s", gender=G.FEMININE, gloss="processing"),
    _lexeme("Zentrum", T.LOCATION, links=("s",), preferred="s", gloss="centre"),
    _lexeme("Stelle", T.INSTITUTION, links=("n",), preferred="n", gender=G.FEMININE, gloss="office/unit", register=R.ADMINISTRATIVE),
)

# Heads are separate senses/forms because a rightmost head does not realize its
# modifier linking form. Every selectable head is explicitly head-licensed.
HEADS: tuple[Lexeme, ...] = (
    _lexeme("Verwaltung", T.INSTITUTION, gender=G.FEMININE, gloss="administration", modifier=False, register=R.ADMINISTRATIVE),
    _lexeme("System", T.SYSTEM, gloss="system", modifier=False, register=R.TECHNICAL),
    _lexeme("Prüfung", T.PROCESS, gender=G.FEMININE, gloss="inspection", modifier=False),
    _lexeme("Regelung", T.DOCUMENT, gender=G.FEMININE, gloss="regulation", modifier=False, register=R.ADMINISTRATIVE),
    _lexeme("Stelle", T.INSTITUTION, gender=G.FEMININE, gloss="office/unit", modifier=False, register=R.ADMINISTRATIVE),
)

BY_TYPE: dict[T, tuple[Lexeme, ...]] = {
    kind: tuple(
        lexeme for lexeme in LEXEMES
        if lexeme.semantic_type == kind and lexeme.allowed_as_modifier
    )
    for kind in T
}

BY_SENSE_ID: dict[str, Lexeme] = {
    lexeme.sense_id: lexeme
    for lexeme in (*LEXEMES, *HEADS)
    if lexeme.sense_id is not None
}


def audit_lexicon() -> None:
    identities = [(x.sense_id, x.allowed_as_modifier, x.allowed_as_head) for x in (*LEXEMES, *HEADS)]
    if len(identities) != len(set(identities)):
        raise RuntimeError("duplicate structured lexeme identity")
    if any(not head.allowed_as_head for head in HEADS):
        raise RuntimeError("selectable head is not head-licensed")
    if any(not lexeme.allowed_as_modifier for pool in BY_TYPE.values() for lexeme in pool):
        raise RuntimeError("modifier index contains an unlicensed lexeme")


audit_lexicon()
