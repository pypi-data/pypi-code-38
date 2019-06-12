import os
import os.path
import tailf
import tempfile


def test_nonexistent_file():
    with tempfile.TemporaryDirectory() as dirname:
        filename = os.path.join(dirname, "nonexistent.txt")
        with tailf.Tail(filename) as tail:
            events = list(iter(tail))
            assert len(events) == 0, "no events are expected"

            with open(filename, "wb") as f:
                events = list(iter(tail))
                assert len(events) == 0, "no events are expected"

                f.write(b"alpha")
                f.flush()
                events = list(iter(tail))
                assert b"".join(events) == b"alpha", "new data is expected"

                events = list(iter(tail))
                assert len(events) == 0, "no events are expected"


def test_preexisting_file():
    with tempfile.NamedTemporaryFile("w+b") as f:
        f.write(b"alpha")
        f.flush()
        with tailf.Tail(f.name) as tail:
            events = list(iter(tail))
            assert b"".join(events) == b"alpha", "pre-existing data is expected"

            events = list(iter(tail))
            assert len(events) == 0, "no events are expected"

            f.write(b"beta")
            f.flush()

            events = list(iter(tail))
            assert b"".join(events) == b"beta", "new data is expected"

            events = list(iter(tail))
            assert len(events) == 0, "no events are expected"


def test_truncate():
    with tempfile.NamedTemporaryFile("w+b") as f:
        with tailf.Tail(f.name) as tail:
            f.write(b"alpha")
            f.flush()
            events = list(iter(tail))
            assert b"".join(events) == b"alpha", "new data is expected"

            f.truncate(0)
            events = list(iter(tail))
            assert tailf.Truncated in events, "tailf.Truncated event is expected"
            assert all(
                not isinstance(event, (str, bytes)) for event in events
            ), "no data events are expected"

            f.seek(0)
            f.write(b"beta")
            f.flush()
            events = list(iter(tail))
            assert b"".join(events) == b"beta", "new data is expected"


def test_delete():
    with tempfile.NamedTemporaryFile("w+b", delete=False) as f:
        with tailf.Tail(f.name) as tail:
            f.write(b"alpha")
            f.flush()
            events = list(iter(tail))
            assert b"".join(events) == b"alpha", "new data is expected"
            os.unlink(f.name)
            events = list(iter(tail))
            assert tailf.Truncated in events, "tailf.Truncated event is expected"
            assert all(
                not isinstance(event, (str, bytes)) for event in events
            ), "no data events are expected"


def test_delete_recreate():
    with tempfile.TemporaryDirectory() as dirname:
        filename = os.path.join(dirname, "sneaky.txt")
        with tailf.Tail(filename) as tail:
            with open(filename, "wb") as f:
                f.write(b"alpha")
                f.flush()
                events = list(iter(tail))
                assert b"".join(events) == b"alpha", "new data is expected"
            os.unlink(filename)
            with open(filename, "wb") as f:
                f.write(b"gamma")  # len('alpha') == len('gamma') intentionally
                f.flush()
                events = list(iter(tail))
                print(events)
                assert tailf.Truncated in events, "tailf.Truncated event is expected"
                trunc = events.index(tailf.Truncated)
                before, after = events[:trunc], events[trunc + 1 :]
                assert b"".join(before) == b"", "no data are expected before truncation"
                assert (
                    b"".join(after) == b"gamma"
                ), "new data is expected after truncation"
