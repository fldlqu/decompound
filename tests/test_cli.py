import io
import json
from contextlib import redirect_stderr, redirect_stdout

import pytest

from decompound.cli import infinite, main, parser, report_error
from decompound.contract import ContractError


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


@pytest.mark.parametrize("length", [1, 2, 50])
def test_default_contract_stdout_is_exactly_one_word_line(length):
    code, out, err = run(["--len", str(length), "--seed", "x"])
    assert code == 0
    assert out.endswith("\n")
    assert out.count("\n") == 1
    assert out[:-1].isalpha()
    assert not any(character.isspace() for character in out[:-1])
    assert err == ""


def test_default_contract_stdout_is_one_word_only():
    code, out, err = run(["--len", "7", "--seed", "x"])
    assert code == 0
    assert out.strip().isalpha()
    assert " " not in out.strip()
    assert err == ""


def test_cli_can_require_final_semantic_type():
    code, out, err = run([
        "--len", "12", "--seed", "x", "--type", "system", "--json"
    ])
    data = json.loads(out)
    assert code == 0
    assert data["semantic_type"] == "system"
    assert err == ""


def test_json_is_structured_and_exact():
    code, out, _ = run(["--len", "8", "--seed", "x", "--json"])
    data = json.loads(out)
    assert code == 0
    assert data["schema"] == "decompound.analysis"
    assert data["schema_version"] == 1
    assert data["components"] == 8
    assert data["word"].isalpha()
    assert len(data["relations_inner_to_outer"]) == 7
    assert data["generation"]["strategy"] == "constrained-dp"
    assert data["generation"]["fallback_used"] is False
    assert len(data["component_sequence"]) == 8
    assert data["validation"]["semantic_edges"] == 7


@pytest.mark.parametrize("value", ["0", "-4", "x", "1.2"])
def test_bad_cli_length(value):
    code, _, err = run(["--len", value])
    assert code == 2
    assert "integer >= 1" in err


def test_explain_has_stable_required_lines():
    code, out, err = run(["--len", "5", "--seed", "explain", "--explain"])
    lines = out.splitlines()
    assert code == 0 and err == ""
    assert lines[0].isalpha()
    assert "components: 5" in lines
    assert any(line.startswith("boundaries: ") for line in lines)
    assert any(line.startswith("type: ") for line in lines)
    assert any(line.startswith("head: ") for line in lines)
    assert any(line.startswith("gloss: ") for line in lines)
    assert any(line.startswith("strategy: ") for line in lines)


def test_runtime_contract_error_uses_only_stderr(monkeypatch):
    def fail(_request):
        raise ContractError("forced failure")

    monkeypatch.setattr("decompound.cli.generate_contract", fail)
    code, out, err = run(["--len", "3"])
    assert code == 2
    assert out == ""
    assert err == "decompound: error: forced failure\n"


def test_report_error_resolves_redirected_stderr_at_call_time():
    err = io.StringIO()
    with redirect_stderr(err):
        report_error("redirected")
    assert err.getvalue() == "decompound: error: redirected\n"


def test_explicit_output_modes_do_not_leak_to_stderr():
    for option in ("--json", "--explain", "--show-boundaries"):
        code, out, err = run(["--len", "4", "--seed", "streams", option])
        assert code == 0
        assert out
        assert err == ""


def test_non_tty_infinite_prints_each_version():
    args = parser().parse_args(["--infinite", "--seed", "5"])
    stdin = io.StringIO("\n\nq\n")
    stdout = io.StringIO()
    assert infinite(args, stdin, stdout) == 0
    words = stdout.getvalue().splitlines()
    assert len(words) == 3
    assert words[1].lower().endswith(words[0].lower())
    assert words[2].lower().endswith(words[1].lower())
