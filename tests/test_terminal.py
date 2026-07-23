import io

import pytest

from decompound.terminal import TerminalRenderer


class FakeTTY(io.StringIO):
    def isatty(self):
        return True


class FlushCountingTTY(FakeTTY):
    def __init__(self):
        super().__init__()
        self.flushes = 0

    def flush(self):
        self.flushes += 1
        super().flush()


def test_tty_first_word_and_complete_redraw_protocol():
    stream = FakeTTY()
    renderer = TerminalRenderer(stream)
    renderer.publish("Amt")
    renderer.publish("Arbeitsamt")
    renderer.publish("Forschungsarbeitsamt")
    renderer.close()
    assert stream.getvalue() == (
        "Amt"
        "\r\x1b[2KArbeitsamt"
        "\r\x1b[2KForschungsarbeitsamt"
        "\n"
    )


def test_non_tty_is_append_only_without_ansi():
    stream = io.StringIO()
    renderer = TerminalRenderer(stream)
    renderer.publish("Amt")
    renderer.publish("Arbeitsamt")
    renderer.close()
    value = stream.getvalue()
    assert value == "Amt\nArbeitsamt\n"
    assert "\x1b" not in value
    assert "\r" not in value


def test_close_is_idempotent_and_publish_after_close_fails():
    stream = FakeTTY()
    renderer = TerminalRenderer(stream)
    renderer.publish("Amt")
    renderer.close()
    renderer.close()
    assert stream.getvalue() == "Amt\n"
    with pytest.raises(RuntimeError, match="after renderer close"):
        renderer.publish("Arbeitsamt")


@pytest.mark.parametrize("bad", ["", "Amt\n", "Amt\rSystem"])
def test_renderer_rejects_non_single_line_states(bad):
    with pytest.raises(ValueError, match="single-line word"):
        TerminalRenderer(io.StringIO()).publish(bad)


def test_each_tty_publication_and_close_flushes():
    stream = FlushCountingTTY()
    renderer = TerminalRenderer(stream)
    renderer.publish("Amt")
    renderer.publish("Arbeitsamt")
    renderer.close()
    assert stream.flushes == 3
