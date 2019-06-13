import tailf
import tempfile


def test_sequence():
    with tempfile.NamedTemporaryFile("w+b") as f:
        with tailf.Tail(f.name) as tail:
            f.write(b"alpha")
            f.flush()
            assert tail.read(2) == b"al", "Expected 'al'"
            assert tail.read() == b"pha", "Expected 'pha'"
            assert tail.read() == b"", "Expected ''"
            f.truncate(0)
            assert tail.read() == b"", "Expected '' after truncation"
            assert (
                tail.is_truncated()
            ), "Expected is_truncated() == True after truncation"
            assert (
                tail.is_truncated()
            ), "Expected is_truncated() to be consistently True after truncation"
            f.seek(0)
            f.write(b"beta")
            f.flush()
            assert tail.read() == b"", "Expected '' until truncation event is consumed"
            assert (
                tail.is_truncated()
            ), "Expected is_truncated() until truncation event is consumed"

            assert (
                tail.get_truncated()
            ), "Expected get_truncated() == True after truncation"
            assert (
                not tail.get_truncated()
            ), "Expected get_truncated() to consume Truncated event"
            assert (
                not tail.is_truncated()
            ), "Expected is_truncated() == False after consuming truncation event"
            assert tail.read() == b"beta", "Expected 'beta'"
