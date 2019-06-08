import hashlib
from . import files

HASHER = hashlib.sha256


def hash_digest(items, hasher=HASHER):
    h = HASHER()
    for i in items:
        h.update(i)
    return h


def hash_file(filename, block_size=files.BLOCK_SIZE, hasher=HASHER):
    blocks = files.file_blocks(filename, block_size)
    return hash_digest(blocks, hasher)


if __name__ == '__main__':
    import sys

    for arg in sys.argv[1:]:
        print(hash_file(arg).hexdigest())
