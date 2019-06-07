import aiotoolz


__all__ = ['merge_with', 'merge']


@aiotoolz.curry
def merge_with(func, d, *dicts, **kwargs):
    return aiotoolz.merge_with(func, d, *dicts, **kwargs)


@aiotoolz.curry
def merge(d, *dicts, **kwargs):
    return aiotoolz.merge(d, *dicts, **kwargs)


merge_with.__doc__ = aiotoolz.merge_with.__doc__
merge.__doc__ = aiotoolz.merge.__doc__
