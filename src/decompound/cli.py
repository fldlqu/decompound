"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from typing import TextIO

from .contract import ContractError, ContractRequest, generate_contract
from .generator import Generator
from .interaction import InteractionAction, classify_input
from .model import Compound, SemanticType
from .morphology import MorphologyError, boundaries, linearize
from .platform import configure_cli_streams
from .presentation import analysis_data, analysis_json, explanation_lines
from .terminal import TerminalRenderer
from .validation import ValidationError, validate


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer >= 1") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("must be an integer >= 1")
    return number


def analysis(compound: Compound) -> dict[str, object]:
    """Backward-compatible alias for the versioned presentation API."""
    return analysis_data(compound)


def emit(compound: Compound, args: argparse.Namespace, stream: TextIO) -> None:
    validate(compound, getattr(args, "length", None))
    if args.json:
        print(analysis_json(compound), file=stream)
    elif args.explain:
        for line in explanation_lines(compound):
            print(line, file=stream)
    elif args.show_boundaries:
        print(boundaries(compound), file=stream)
    else:
        print(linearize(compound), file=stream)


def infinite(args: argparse.Namespace, stdin: TextIO, stdout: TextIO) -> int:
    generator = Generator.seeded(args.seed)
    compound = generator.start(args.target_type)
    renderer = TerminalRenderer(stdout)
    word = linearize(compound)
    renderer.publish(word)
    while True:
        try:
            line = stdin.readline()
        except KeyboardInterrupt:
            renderer.close()
            return 0
        interaction = classify_input(line)
        if interaction.action == InteractionAction.QUIT:
            renderer.close()
            return 0
        if interaction.action == InteractionAction.INVALID:
            report_error(
                "in infinite mode, press Enter to extend or type q to quit"
            )
            continue
        extension = generator.extend_left(compound)
        compound = extension.compound
        validate(compound)
        word = extension.word
        renderer.publish(word)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="decompound",
        description="Generate typed, recursively extensible German compounds.",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--len", dest="length", type=positive_int,
                      help="generate exactly N semantic components")
    mode.add_argument("--infinite", action="store_true",
                      help="append one left modifier per Enter")
    p.add_argument("--seed", help="reproducible random seed")
    p.add_argument(
        "--type",
        dest="target_type",
        choices=[kind.value for kind in Generator.seeded(0).available_head_types()],
        help="require the final compound to have this semantic head type",
    )
    output = p.add_mutually_exclusive_group()
    output.add_argument("--explain", action="store_true")
    output.add_argument("--json", action="store_true")
    output.add_argument("--show-boundaries", action="store_true")
    return p


def report_error(message: str, stream: TextIO | None = None) -> None:
    """Write a human diagnostic without contaminating the data stream."""
    destination = sys.stderr if stream is None else stream
    print(f"decompound: error: {message}", file=destination)


def main(argv: list[str] | None = None) -> int:
    configure_cli_streams(sys.stdout, sys.stderr)
    args = parser().parse_args(argv)
    try:
        if args.length is not None:
            result = generate_contract(
                ContractRequest(args.length, args.seed, args.target_type)
            )
            emit(result.compound, args, sys.stdout)
            return 0
        return infinite(args, sys.stdin, sys.stdout)
    except (ContractError, ValidationError, MorphologyError) as exc:
        report_error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
