import tempfile

from tailf.base import TailBase as Tail
from .helpers import write_through


def test_internal_read1():
    with tempfile.NamedTemporaryFile("w+b") as f:
        with Tail(f.name) as tail:
            assert tail._read1() == b"", "Newly created file should be empty"
            assert not tail.is_truncated()
            write_through(f, b"a")
            assert tail._read1() == b"a", "One byte was written"
            assert not tail.is_truncated()
            assert tail._read1() == b"", "No more data expected after the first byte"
            assert not tail.is_truncated()
            write_through(f, b"b")
            assert tail._read1() == b"b", "Second byte was written"
            assert not tail.is_truncated()
            assert tail._read1() == b"", "No more data expected after the second byte"
            assert not tail.is_truncated()
            # truncations
            f.truncate(0)
            f.seek(0)
            assert tail._read1() == b"", "Just truncated"
            assert tail.is_truncated(), "Just truncated"
            assert tail.get_truncated(), "Just truncated"
            assert tail.is_truncated() is False, "Truncation consumed"
            assert tail.get_truncated() is False, "Truncation consumed"
