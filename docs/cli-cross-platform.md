# CLI and cross-platform behavior

The CLI targets Python 3.11+ on POSIX terminals, Windows consoles, redirected
files, and pipes. Platform-specific presentation is confined to standard Python
text streams and TTY capability detection.

## Unicode stream policy

At CLI startup, `configure_cli_streams` requests UTF-8 with strict error handling
for stdout and stderr when their stream objects support `reconfigure`. This
avoids dependence on a legacy locale code page for German letters such as:

```text
ä ö ü Ä Ö Ü ß
```

Embedded streams, `StringIO`, and test doubles may not implement `reconfigure`.
That is nonfatal: configuration returns `False` and the supplied stream remains
in use. Reconfiguration failures are likewise nonfatal because the host may own
the stream policy.

## Newlines

The CLI uses Python text-mode newline handling. Source code writes `"\n"`; the
runtime translates it to the platform convention where appropriate. Tests use
`splitlines()` or `os.linesep` rather than assuming a particular host newline.

Default contract output remains exactly one platform text line. Non-TTY infinite
mode emits one complete state per platform text line.

## Terminal controls

ANSI erase-line controls are emitted only when `stdout.isatty()` is true. Pipes,
redirected files, captured subprocess output, and ordinary Windows/non-TTY
consumers receive no escape or carriage-return control bytes.

Terminal capability detection does not inspect operating-system names. This
allows ANSI-capable modern Windows terminals to use the same TTY path while
noninteractive streams stay clean on every platform.

## Process invocation

Both installed entry points are supported:

```text
decompound ...
python -m decompound ...
```

`argparse` provides platform-independent option parsing, usage text, stderr
argument diagnostics, and status 2 for invalid command lines.

## Exit codes

```text
0 successful generation or normal infinite-mode termination
1 requested resource check reports unavailable package/data
2 command-line, contract, validation, or morphology error
```

## Cross-platform subprocess coverage

Subprocess tests cover:

- module entry-point help;
- word-only output and platform newline;
- UTF-8 JSON under both Python UTF-8 mode settings;
- non-TTY infinite pipelines without ANSI controls;
- unknown-option stderr behavior;
- direct stream reconfiguration support and graceful fallback.
