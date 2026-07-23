import json
import os
import subprocess
import sys

import pytest


ROOT = os.path.abspath(".")
SRC = os.path.join(ROOT, "src")


def invoke(args, *, input_text=None, env_updates=None):
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC + os.pathsep + env.get("PYTHONPATH", "")
    if env_updates:
        env.update(env_updates)
    return subprocess.run(
        [sys.executable, "-m", "decompound", *args],
        input=input_text,
        text=True,
        capture_output=True,
        cwd=ROOT,
        env=env,
        check=False,
    )


@pytest.mark.parametrize("utf8_mode", ["0", "1"])
def test_unicode_output_survives_python_utf8_mode_setting(utf8_mode):
    result = invoke(
        ["--len", "100", "--seed", "unicode", "--json"],
        env_updates={"PYTHONUTF8": utf8_mode, "PYTHONIOENCODING": "utf-8"},
    )
    data = json.loads(result.stdout)
    assert result.returncode == 0
    assert result.stderr == ""
    assert data["word"].isalpha()
    assert any(character in result.stdout for character in "äöüÄÖÜß")


def test_contract_output_uses_single_platform_text_line():
    result = invoke(["--len", "20", "--seed", "newline"])
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.endswith(os.linesep)
    assert result.stdout.splitlines() == [result.stdout.strip()]
    assert result.stdout.strip().isalpha()


def test_non_tty_infinite_has_no_terminal_control_bytes():
    result = invoke(
        ["--infinite", "--seed", "pipe"],
        input_text="\n\nq\n",
    )
    assert result.returncode == 0
    assert result.stderr == ""
    assert len(result.stdout.splitlines()) == 3
    assert "\x1b" not in result.stdout
    assert "\r" not in result.stdout


def test_module_help_and_entry_point_name_are_stable():
    result = invoke(["--help"])
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.startswith("usage: decompound")
    assert "--len" in result.stdout
    assert "--infinite" in result.stdout


def test_unknown_option_fails_without_stdout_data():
    result = invoke(["--definitely-unknown"])
    assert result.returncode == 2
    assert result.stdout == ""
    assert "unrecognized arguments" in result.stderr
