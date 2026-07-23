# CLI stdout and diagnostic stream contract

The command-line interface treats standard output as a data channel and standard
error as a human diagnostic channel.

## Default contract mode

For:

```bash
decompound --len N
```

successful stdout contains exactly:

```text
<generated-word>\n
```

The word is one NFC-normalized alphabetic German noun. Stdout contains no label,
component count, progress message, seed, explanation, warning, or resource
status. Successful default contract mode writes nothing to stderr.

This permits safe composition such as:

```bash
word=$(decompound --len 20 --seed demo)
decompound --len 50 | consumer-process
```

## Explicit alternate output modes

Additional stdout content occurs only when requested:

- `--json` emits one JSON document;
- `--explain` emits a human-readable multiline explanation;
- `--show-boundaries` emits one annotated boundary representation;
- non-TTY `--infinite` emits one complete word per line.

These modes replace default word-only output; they are not unsolicited
diagnostics.

## Diagnostics and exit status

Argument-parser errors use argparse's standard stderr output and exit status 2.
Runtime contract, validation, and morphology errors are caught at the CLI
boundary and written only to stderr as:

```text
decompound: error: <message>
```

They return status 2 and write no partial result to stdout.

## Infinite mode

Interactive TTY redraws are stdout user-interface output. The complete current
word is redrawn in place after Enter. In non-TTY pipelines, every complete
version is emitted as a separate stdout line. Keyboard interruption and normal
quit do not emit diagnostics.

## Library logging

Core model, planning, morphology, validation, and contract modules do not print
or configure logging. They return values or raise typed exceptions. Only the CLI
decides how those exceptions map to process streams and exit codes.
