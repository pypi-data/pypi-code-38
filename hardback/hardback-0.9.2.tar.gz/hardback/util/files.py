BLOCK_SIZE = 4096


def file_blocks(filename, block_size=BLOCK_SIZE):
    with open(filename, 'rb') as fp:
        while True:
            buf = fp.read(block_size)
            if not buf:
                return
            yield buf
