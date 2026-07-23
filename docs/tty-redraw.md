# TTY redraw and non-TTY line rendering

Interactive presentation is isolated in `TerminalRenderer`. Linguistic state and
word rebuilding do not depend on terminal capabilities.

## Capability detection

Unless explicitly overridden for testing, the renderer calls:

```python
stream.isatty()
```

A missing `isatty` method is treated as non-TTY. ANSI control sequences are used
only when this result is true.

## TTY publication

The first complete word is written directly and flushed. Every later complete
word is published as:

```text
carriage return + ANSI erase-entire-line + complete word
```

The exact prefix is:

```text
\r\x1b[2K
```

Erasing the whole line prevents visible suffix fragments when terminal display
width or a future presentation change makes the replacement shorter. The
renderer always writes a complete rebuilt word, never an incremental text delta.

On normal quit, EOF, or keyboard interruption, `close()` writes one final newline
so the shell prompt begins on a fresh line. Repeated close calls are idempotent.

## Non-TTY publication

For redirected files, pipes, `StringIO`, and other non-TTY streams, each complete
state is printed as:

```text
<word>\n
```

No carriage return or escape byte is emitted. Closing adds no extra blank line.
This yields a stable append-only history suitable for tools such as `head`,
`tail`, and line-oriented consumers.

## Safety conditions

`publish` rejects empty strings and strings containing carriage returns or
newlines. Publication after close is rejected. Successful publication flushes
the stream immediately in both modes, so an Enter-driven update is visible
without buffering delay.

## Separation of responsibilities

The renderer does not generate, validate, rebuild, or inspect German compounds.
It accepts one already complete single-line word. The infinite interaction flow
therefore remains:

```text
input -> legal extension -> full rebuild -> validation -> renderer.publish
```

This keeps ANSI behavior testable independently from linguistic correctness.
