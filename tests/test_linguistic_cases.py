"""Deterministic fixtures for curated German linguistic behavior."""

import unicodedata

import pytest

from decompound import boundaries, linearize, validate
from decompound.model import Compound, Lexeme, Relation, Rule, SemanticType as T, Step


def rule(modifier_type, head_type, relation=Relation.CONCERNS):
    templates = {
        Relation.CONCERNS: "the {head} concerning {modifier}",
        Relation.MANAGES: "the {head} managing {modifier}",
        Relation.REGULATES: "the {head} regulating {modifier}",
        Relation.PROCESSES: "the {head} processing {modifier}",
        Relation.EXAMINES: "the {head} examining {modifier}",
        Relation.USED_FOR: "the {head} used for {modifier}",
    }
    return Rule(modifier_type, head_type, head_type, relation, templates[relation])


@pytest.mark.parametrize(
    ("modifier", "head", "expected", "marked"),
    [
        (
            Lexeme("Arbeit", "Arbeit", T.ACTIVITY, ("s",), "s"),
            Lexeme("Amt", "Amt", T.INSTITUTION),
            "Arbeitsamt", "Arbeit[s]+Amt",
        ),
        (
            Lexeme("Gesetz", "Gesetz", T.DOCUMENT, ("es",), "es"),
            Lexeme("Text", "Text", T.DOCUMENT),
            "Gesetzestext", "Gesetz[es]+Text",
        ),
        (
            Lexeme("Behörde", "Behörde", T.INSTITUTION, ("n",), "n"),
            Lexeme("Plan", "Plan", T.DOCUMENT),
            "Behördenplan", "Behörde[n]+Plan",
        ),
        (
            Lexeme("Name", "Name", T.SUBJECT, ("n", "ns"), "ns"),
            Lexeme("Liste", "Liste", T.DOCUMENT),
            "Namensliste", "Name[ns]+Liste",
        ),
        (
            Lexeme("Wasser", "Wasser", T.MATERIAL),
            Lexeme("System", "System", T.SYSTEM),
            "Wassersystem", "Wasser+System",
        ),
    ],
)
def test_curated_linking_allomorph_cases(modifier, head, expected, marked):
    compound = Compound(head, (Step(modifier, rule(modifier.semantic_type, head.semantic_type)),))
    assert linearize(compound) == expected
    assert boundaries(compound) == marked
    validate(compound, 2)


def test_explicit_nonpreferred_licensed_name_allomorph():
    modifier = Lexeme("Name", "Name", T.SUBJECT, ("n", "ns"), "ns")
    head = Lexeme("Liste", "Liste", T.DOCUMENT)
    compound = Compound(
        head,
        (Step(modifier, rule(T.SUBJECT, T.DOCUMENT), linking_form="n"),),
    )
    assert linearize(compound) == "Namenliste"
    assert boundaries(compound) == "Name[n]+Liste"


def test_multi_edge_surface_order_and_right_headedness():
    system = Lexeme("System", "System", T.SYSTEM)
    arbeit = Lexeme("Arbeit", "Arbeit", T.ACTIVITY, ("s",), "s")
    daten = Lexeme("Daten", "Daten", T.SUBJECT)
    compound = Compound(system, (
        Step(arbeit, rule(T.ACTIVITY, T.SYSTEM, Relation.USED_FOR)),
        Step(daten, rule(T.SUBJECT, T.SYSTEM, Relation.PROCESSES)),
    ))
    assert compound.components() == (daten, arbeit, system)
    assert linearize(compound) == "Datenarbeitssystem"
    assert boundaries(compound) == "Daten+Arbeit[s]+System"
    assert compound.semantic_type == T.SYSTEM
    validate(compound, 3)


def test_modern_triple_consonant_is_preserved():
    stoff = Lexeme("Stoff", "Stoff", T.MATERIAL)
    schiff = Lexeme("Schiff", "Schiff", T.ARTIFACT)
    compound = Compound(stoff, (Step(schiff, rule(T.ARTIFACT, T.MATERIAL)),))
    assert linearize(compound) == "Schiffstoff"
    assert "fff" in linearize(compound)


def test_unicode_umlauts_and_sharp_s_are_nfc_and_preserved():
    modifier = Lexeme("Größe", "Gro\u0308ße", T.SUBJECT)
    head = Lexeme("Prüfung", "Prüfung", T.PROCESS)
    compound = Compound(head, (Step(modifier, rule(T.SUBJECT, T.PROCESS, Relation.EXAMINES)),))
    word = linearize(compound)
    assert word == "Größeprüfung"
    assert "ß" in word and "ö" in word and "ü" in word
    assert unicodedata.is_normalized("NFC", word)


def test_relation_interpretation_is_deterministic_and_compositional():
    system = Lexeme("System", "System", T.SYSTEM, gloss="system")
    arbeit = Lexeme(
        "Arbeit", "Arbeit", T.ACTIVITY, ("s",), "s", gloss="work"
    )
    daten = Lexeme("Daten", "Daten", T.SUBJECT, gloss="data")
    inner = rule(T.ACTIVITY, T.SYSTEM, Relation.USED_FOR)
    outer = rule(T.SUBJECT, T.SYSTEM, Relation.PROCESSES)
    compound = Compound(system, (Step(arbeit, inner), Step(daten, outer)))
    gloss = system.gloss
    gloss = inner.interpret(modifier=arbeit.gloss, head=gloss)
    gloss = outer.interpret(modifier=daten.gloss, head=gloss)
    assert gloss == "the the system used for work processing data"
    assert linearize(compound) == "Datenarbeitssystem"
