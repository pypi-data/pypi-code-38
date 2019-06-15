def normal(func, cache):
    def run(*args, **kwargs):
        cache.filter()
        try:
            key, value = cache.get(*args, **kwargs)
        except KeyError:
            value = func(*args, **kwargs)
            cache.set(value, *args, **kwargs)
        return value
    return run


def as_async(func, cache):
    async def run(*args, **kwargs):
        cache.filter()
        try:
            key, value = cache.get(*args, **kwargs)
        except KeyError:
            value = await func(*args, **kwargs)
            cache.set(value, *args, **kwargs)
        return value
    return run


def raw(func, cache):
    return cache(func)
