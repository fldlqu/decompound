import json
import os
import subprocess
import sys

import pytest


def invoke(*args):
    env = os.environ.copy()
    src = os.path.abspath("src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "decompound", *args],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


@pytest.mark.parametrize("length", [1, 7, 100])
def test_real_process_default_stdout_is_word_only(length):
    result = invoke("--len", str(length), "--seed", "subprocess")
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.endswith("\n")
    assert result.stdout.count("\n") == 1
    assert result.stdout[:-1].isalpha()


def test_real_process_json_stdout_is_one_document():
    result = invoke("--len", "12", "--seed", "subprocess", "--json")
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.count("\n") == 1
    assert json.loads(result.stdout)["components"] == 12


def test_real_process_infinite_protocol_is_enter_driven():
    env = os.environ.copy()
    src = os.path.abspath("src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "decompound", "--infinite", "--seed", "flow"],
        input="\n\nq\n",
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    words = result.stdout.splitlines()
    assert result.returncode == 0
    assert result.stderr == ""
    assert len(words) == 3
    assert words[1].lower().endswith(words[0].lower())
    assert words[2].lower().endswith(words[1].lower())


def test_real_process_argument_failure_has_empty_stdout():
    result = invoke("--len", "0")
    assert result.returncode == 2
    assert result.stdout == ""
    assert "integer >= 1" in result.stderr
