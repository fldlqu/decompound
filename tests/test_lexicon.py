import pytest

from decompound.lexicon import BY_SENSE_ID, BY_TYPE, HEADS, LEXEMES, audit_lexicon
from decompound.model import Gender, Lexeme, SemanticType as T


def test_core_lexicon_is_structured_and_audited():
    audit_lexicon()
    for lexeme in (*LEXEMES, *HEADS):
        assert lexeme.source
        assert lexeme.sense_id
        assert BY_SENSE_ID[lexeme.sense_id] == lexeme
        assert lexeme.preferred_linking_form in lexeme.linking_forms
        assert isinstance(lexeme.gender, Gender)


def test_modifier_index_contains_only_modifier_licensed_entries():
    for kind, pool in BY_TYPE.items():
        for lexeme in pool:
            assert lexeme.semantic_type == kind
            assert lexeme.allowed_as_modifier


def test_selectable_heads_are_explicitly_head_licensed():
    assert HEADS
    assert all(head.allowed_as_head for head in HEADS)


def test_preferred_link_must_be_licensed():
    with pytest.raises(ValueError, match="preferred linking form"):
        Lexeme(
            "Arbeit", "Arbeit", T.ACTIVITY,
            linking_forms=("",), preferred_linking_form="s",
        )


def test_modifier_form_rejects_head_only_entry():
    entry = Lexeme("Amt", "Amt", T.INSTITUTION, allowed_as_modifier=False)
    with pytest.raises(ValueError, match="not licensed as a modifier"):
        _ = entry.modifier_form


def test_lexeme_requires_provenance():
    with pytest.raises(ValueError, match="source"):
        Lexeme("Amt", "Amt", T.INSTITUTION, source="")
