import hashlib


def calc_checksum(f, hasher_cls):
    hasher = hasher_cls()
    while True:
        d = f.read(8096)
        if not d:
            break
        hasher.update(d)
    return hasher.hexdigest()


def md5sum(f):
    """Calculate the md5 checksum of a file-like object without reading its
    whole content in memory.

    >>> from io import BytesIO
    >>> md5sum(BytesIO(b'file content to hash'))
    '784406af91dd5a54fbb9c84c2236595a'
    """
    return calc_checksum(f, hashlib.md5)


def sha1sum(f):
    return calc_checksum(f, hashlib.sha1)


def sha256sum(f):
    return calc_checksum(f, hashlib.sha256)
