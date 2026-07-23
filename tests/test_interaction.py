import io

import pytest

from decompound.cli import infinite, parser
from decompound.interaction import InteractionAction, classify_input


@pytest.mark.parametrize("line", ["\n", "   \n", "\t\n"])
def test_blank_lines_mean_extend(line):
    event = classify_input(line)
    assert event.action == InteractionAction.EXTEND
    assert event.command == "enter"


@pytest.mark.parametrize("line", ["", "q\n", " QUIT \n", "Exit\n"])
def test_quit_inputs_are_case_insensitive(line):
    assert classify_input(line).action == InteractionAction.QUIT


@pytest.mark.parametrize("line", ["x\n", "continue\n", "qq\n"])
def test_other_text_is_invalid_not_extension(line):
    assert classify_input(line).action == InteractionAction.INVALID


def test_invalid_input_does_not_extend_or_publish(capsys):
    args = parser().parse_args(["--infinite", "--seed", "protocol"])
    stdin = io.StringIO("mistake\n\nq\n")
    stdout = io.StringIO()
    assert infinite(args, stdin, stdout) == 0
    words = stdout.getvalue().splitlines()
    assert len(words) == 2
    assert words[1].lower().endswith(words[0].lower())
    assert "press Enter to extend" in capsys.readouterr().err


def test_tty_infinite_redraws_complete_words_and_finishes_line(capsys):
    class TTY(io.StringIO):
        def isatty(self):
            return True

    args = parser().parse_args(["--infinite", "--seed", "tty"])
    stdout = TTY()
    assert infinite(args, io.StringIO("\n\nq\n"), stdout) == 0
    value = stdout.getvalue()
    assert value.count("\r\x1b[2K") == 2
    assert value.endswith("\n")
    assert value.count("\n") == 1
    states = value[:-1].split("\r\x1b[2K")
    assert len(states) == 3
    assert all(state.isalpha() for state in states)
    assert states[1].lower().endswith(states[0].lower())
    assert states[2].lower().endswith(states[1].lower())
    assert capsys.readouterr().err == ""


def test_eof_stops_after_initial_state_without_diagnostic(capsys):
    args = parser().parse_args(["--infinite", "--seed", "protocol"])
    stdout = io.StringIO()
    assert infinite(args, io.StringIO(""), stdout) == 0
    assert len(stdout.getvalue().splitlines()) == 1
    assert capsys.readouterr().err == ""
