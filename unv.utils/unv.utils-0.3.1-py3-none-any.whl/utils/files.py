import zlib
import pathlib


def calc_crc32_for_file(path: pathlib.Path) -> int:
    """Read file by path and return crc32 sum integer.

    >>> import tempfile
    >>> import pathlib
    >>> fp = tempfile.NamedTemporaryFile()
    >>> fp.write(b'Some data')
    9
    >>> fp.flush()
    >>> calc_crc32_for_file(pathlib.Path(fp.name))
    1530096573
    """
    with open(str(path), 'rb') as f:
        return zlib.crc32(f.read())
