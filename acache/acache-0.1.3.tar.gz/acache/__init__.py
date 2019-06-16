import functools

from acache import strategy, runners


class Handler:

    def __init__(self, func, strat=None, runner=None):
        self.func = func
        self.strat = strat
        self.runner = runner(self.func, self.strat)

    def __call__(self, *args, **kwargs):
        return self.runner(*args, **kwargs)


def cache(size=1024, strat=strategy.Basic, runner=runners.normal,
          handler=Handler):
    return functools.partial(handler, strat=strat(size), runner=runner)


acache = functools.partial(cache, runner=runners.as_async)
