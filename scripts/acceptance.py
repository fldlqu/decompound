#!/usr/bin/env python3
"""Dependency-free final acceptance gate for decompound."""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from decompound import (  # noqa: E402
    ContractRequest,
    Generator,
    SCHEMA_NAME,
    SCHEMA_VERSION,
    SemanticType,
    analysis_json,
    generate_contract,
    validate,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "decompound", *args],
        input=input_text,
        text=True,
        capture_output=True,
        cwd=ROOT,
        env=env,
        check=False,
    )


def contract_gate() -> tuple[int, int]:
    targets = (
        SemanticType.INSTITUTION,
        SemanticType.SYSTEM,
        SemanticType.PROCESS,
        SemanticType.DOCUMENT,
    )
    compounds = edges = 0
    for target in targets:
        for seed in range(12):
            for length in (1, 2, 17, 100, 1000):
                request = ContractRequest(length, seed, target)
                left = generate_contract(request).compound
                right = generate_contract(request).compound
                report = validate(left, length)
                require(left == right, "seeded structure is not deterministic")
                require(report.final_semantic_type == target, "target type changed")
                require(len(report.edges) == length - 1, "wrong edge count")
                require(all(layer.valid for layer in report.layers), "invalid layer")
                compounds += 1
                edges += len(report.edges)
    return compounds, edges


def extension_gate() -> int:
    transactions = 0
    for target in (
        SemanticType.INSTITUTION,
        SemanticType.SYSTEM,
        SemanticType.PROCESS,
        SemanticType.DOCUMENT,
    ):
        for seed in range(10):
            generator = Generator.seeded(seed)
            compound = generator.start(target)
            for expected in range(2, 102):
                previous = compound
                result = generator.extend_left(previous)
                compound = result.compound
                require(compound.head is previous.head, "head identity changed")
                require(
                    compound.components() == (result.step.modifier,) + previous.components(),
                    "left-extension structure changed",
                )
                validate(compound, expected)
                transactions += 1
    return transactions


def presentation_gate() -> None:
    compound = generate_contract(ContractRequest(30, "json", SemanticType.SYSTEM)).compound
    first = analysis_json(compound)
    second = analysis_json(compound)
    require(first == second, "JSON output is not deterministic")
    data = json.loads(first)
    require(data["schema"] == SCHEMA_NAME, "wrong schema name")
    require(data["schema_version"] == SCHEMA_VERSION, "wrong schema version")
    require(
        [layer["name"] for layer in data["validation"]["layers"]]
        == ["structure", "semantics", "morphology", "orthography"],
        "wrong validation layer order",
    )


def random_isolation_gate() -> None:
    random.seed(314159)
    before = random.getstate()
    generate_contract(ContractRequest(100, "private", SemanticType.DOCUMENT))
    require(random.getstate() == before, "global random state was mutated")


def cli_gate() -> int:
    runs = 0
    for seed in range(20):
        result = run_cli("--len", "50", "--seed", str(seed))
        require(result.returncode == 0, "contract CLI failed")
        require(result.stderr == "", "successful CLI wrote stderr")
        require(len(result.stdout.splitlines()) == 1, "stdout is not one line")
        require(result.stdout.strip().isalpha(), "stdout is not one word")
        runs += 1

    result = run_cli("--len", "0")
    require(result.returncode == 2, "invalid length status changed")
    require(result.stdout == "", "invalid length leaked stdout")
    require("decompound: error:" in result.stderr, "error format changed")
    require(result.stderr.rstrip().splitlines()[-1].startswith("decompound: error:"), "error trailer changed")
    runs += 1

    result = run_cli("--infinite", "--seed", "pipe", input_text="\n\nq\n")
    require(result.returncode == 0, "infinite pipeline failed")
    require(len(result.stdout.splitlines()) == 3, "infinite state count changed")
    require("\x1b" not in result.stdout and "\r" not in result.stdout, "TTY bytes leaked")
    runs += 1
    return runs


def main() -> int:
    compounds, edges = contract_gate()
    transactions = extension_gate()
    presentation_gate()
    random_isolation_gate()
    processes = cli_gate()
    print(
        "ACCEPTANCE PASSED: "
        f"{compounds} contracts, {edges} typed edges, "
        f"{transactions} extensions, {processes} subprocesses"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
