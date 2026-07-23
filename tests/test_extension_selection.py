import random
from unittest.mock import patch

import pytest

from decompound import Generator, SemanticType as T
from decompound.extension import (
    ExtensionOption,
    audit_extension_options,
    choose_extension_step,
    legal_extension_options,
)
from decompound.lexicon import HEADS
from decompound.model import Lexeme


SELECTABLE_TYPES = tuple(dict.fromkeys(head.semantic_type for head in HEADS))


@pytest.mark.parametrize("kind", SELECTABLE_TYPES)
def test_every_enumerated_option_is_realizable_and_typed(kind):
    options = legal_extension_options(kind)
    assert options
    for option in options:
        assert option.head_type == kind
        assert option.modifiers
        for modifier in option.modifiers:
            assert modifier.allowed_as_modifier
            assert option.rule.accepts(modifier.semantic_type, kind)


@pytest.mark.parametrize("kind", SELECTABLE_TYPES)
def test_many_random_choices_are_legal(kind):
    rng = random.Random(kind.value)
    for _ in range(1000):
        step = choose_extension_step(kind, rng)
        assert step.rule.accepts(step.modifier.semantic_type, kind)
        assert step.modifier.allowed_as_modifier
        assert step.effective_linking_form in step.modifier.linking_forms


def test_option_rejects_mistyped_modifier_pool():
    option = legal_extension_options(T.SYSTEM)[0]
    wrong = Lexeme("Amt", "Amt", T.INSTITUTION)
    with pytest.raises(ValueError, match="violates rule signature"):
        ExtensionOption(option.rule, (wrong,))


def test_empty_rich_options_use_safe_step():
    with patch("decompound.extension.legal_extension_options", return_value=()):
        step = choose_extension_step(T.DOCUMENT, random.Random(2))
    assert step.rule.signature == (T.DOCUMENT, T.DOCUMENT, T.DOCUMENT)
    assert step.modifier.semantic_type == T.DOCUMENT


def test_generator_defensively_rejects_bad_selector_result():
    generator = Generator.seeded(1)
    compound = generator.start(T.SYSTEM)
    bad_option = legal_extension_options(T.DOCUMENT)[0]
    bad_step = bad_option.choose(random.Random(1))
    with patch.object(generator, "_step_for_type", return_value=bad_step):
        with pytest.raises(RuntimeError, match="illegal relation edge"):
            generator.next_step(compound)


def test_extension_option_audit_passes_for_selectable_types():
    audit_extension_options(SELECTABLE_TYPES)
