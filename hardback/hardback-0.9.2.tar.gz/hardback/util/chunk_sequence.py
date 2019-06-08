import math


def chunk_sequence(items, columns, rows):
    metadata_every = guess_metadata_every(columns * rows)
    metadata = None
    for i, item in enumerate(items):
        if i:
            if metadata_every and not i % metadata_every:
                yield metadata
        else:
            metadata = item
        yield item


def guess_metadata_every(page_size):
    p = 1.5 * page_size
    sizes = range(page_size, 2 * page_size)
    return -min((math.gcd(page_size, i + 1), abs(p - i), -i) for i in sizes)[2]
