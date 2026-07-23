import io

from decompound.platform import (
    StreamConfiguration,
    configure_cli_streams,
    configure_text_stream,
)


class RecordingStream:
    def __init__(self):
        self.calls = []

    def reconfigure(self, **kwargs):
        self.calls.append(kwargs)


class RejectingStream:
    def reconfigure(self, **_kwargs):
        raise OSError("unsupported")


def test_stream_configuration_requests_utf8_strict():
    stream = RecordingStream()
    assert configure_text_stream(stream) is True
    assert stream.calls == [{"encoding": "utf-8", "errors": "strict"}]


def test_custom_stream_configuration_is_supported():
    stream = RecordingStream()
    config = StreamConfiguration("utf-8", "backslashreplace")
    assert configure_text_stream(stream, config) is True
    assert stream.calls[-1] == {
        "encoding": "utf-8", "errors": "backslashreplace",
    }


def test_stringio_without_reconfigure_remains_usable():
    stream = io.StringIO()
    assert configure_text_stream(stream) is False
    stream.write("Größeprüfung")
    assert stream.getvalue() == "Größeprüfung"


def test_reconfigure_failure_is_nonfatal():
    assert configure_text_stream(RejectingStream()) is False


def test_both_cli_streams_are_configured_independently():
    stdout, stderr = RecordingStream(), RecordingStream()
    assert configure_cli_streams(stdout, stderr) == (True, True)
    assert len(stdout.calls) == len(stderr.calls) == 1
