def chunks(iterable, chunk):
    """Yield successive n-sized chunks from an iterable."""
    for i in range(0, len(iterable), chunk):
        yield iterable[i:i + chunk]


def dict_chunks(dictionary, chunk):
    """Return a list of dictionary with n-keys (chunk) per list."""
    return [{k: v for k, v in dictionary.items() if k in i} for i in chunks(list(dictionary.keys()), chunk)]
