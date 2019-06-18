import itertools


def batches(iterable, batch_size):
    it = iter(iterable)
    while True:
        p = tuple(itertools.islice(it, batch_size))
        if not p:
            break
        yield p
