import functools

from acache import strategy, runners


def cache(size=1024, strat=strategy.Basic, runner=runners.normal):
    cache = strat(size)
    def dec(func):
        return runner(func, cache)
    return dec


acache = functools.partial(cache, runner=runners.as_async)
