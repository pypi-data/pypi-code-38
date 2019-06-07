"""
Module providing utilities for parallelization of operations on 5C data.

The most important thing exposed in this module is the ``@parallelize_regions``
decorator, which automatically overloads any function to accept regional dicts
of any of its arguments and process the regions in parallel via the
``multiprocess`` package.

The other functions in this module are either example functions to show how it
works (``test_function_one``, etc.) or private helper functions.
"""

from functools import wraps
import inspect
import multiprocessing as mp
import dill

from lib5c.util.pretty_decorator import pretty_decorator


def _regional_param_depth(param, regions, depth=0):
    depth += 1
    if hasattr(param, 'keys') and param.keys():
        if set(param.keys()) == set(regions):
            return depth
        else:
            return _regional_param_depth(param[param.keys()[0]], regions, depth)
    return 0


def _regionalize_param(param, region, depth=1):
    if depth == 0:
        return param
    elif depth == 1:
        return param[region]
    elif depth == 2:
        return {upper_key: param[upper_key][region]
                for upper_key in param.keys()}
    else:
        raise NotImplementedError('regions too deep in parameter')


def _regionalize_params(f, region, regions, args, kwargs):
    return (
        [_regionalize_param(arg, region, _regional_param_depth(arg, regions))
         for arg in args],
        {key: _regionalize_param(kwargs[key], region,
                                 _regional_param_depth(kwargs[key], regions))
         for key in kwargs})


def _unpack_for_map(payload):
    fn, args, kwargs = dill.loads(payload)
    return fn(args, kwargs)


def _pack_for_map(fn, args_kwargs_list):
    return [dill.dumps((fn, args, kwargs)) for args, kwargs in args_kwargs_list]


@pretty_decorator
def parallelize_regions(f, suppress_warnings=True):
    """
    A function decorator for parallelizing arbitrary functions to make them
    operate on regional dicts in parallel.

    Parameters
    ----------
    f : Callable[[...], Any]
        The function to parallelize.
    suppress_warnings : bool
        Make the wrapped functions suppress warnings, which prevents each of
        them from writing their own errors when run by ``multiprocess``.

    Returns
    -------
    Callable[[...], Any]
        The parallelized version of ``f``.

    Notes
    -----
    When the decorated function is called, the first positional argument is
    checked to see if it defines a ``keys()`` function. If it doesn't, then the
    original, non-parallel version of the function is executed. If it does, then
    the keys of the first positional argument are taken to be the region names.
    The other positional and keyword arguments are searched for any dict-like
    structures with a matching set of keys, up to a depth of two nested dicts
    deep, which are then identified as region-specific parameters. The function
    is then executed in parallel for each region, using the appropriate
    combination of region-specific and non-region-specific parameters. When all
    the parallel executions return, their values are repackaged into a dict. If
    the original non-parallel version of the function returns a tuple, the
    return type of the parallelized invocation of the function will be a tuple
    of dicts.
    """
    def wrapped_function(args, kwargs):
        if suppress_warnings:
            import warnings
            warnings.simplefilter('ignore')
        return f(*args, **kwargs)

    @wraps(f)
    def parallel_func(*args, **kwargs):
        # if the first arg is not a dict then give them the normal version
        if len(args) == 0 or not hasattr(args[0], 'keys'):
            return f(*args, **kwargs)

        # condense and resolve all kwargs into args
        all_arg_names, _, _, defaults = inspect.getargspec(f)

        # repackage defaults into a dict for convenience
        if defaults:
            n_args = len(all_arg_names) - len(defaults)
            defaults = {all_arg_names[n_args + i]: defaults[i]
                        for i in range(len(defaults))}

        # this condition is false if args already represents args+kwargs
        if len(args) != len(all_arg_names):
            args = list(args)
            for arg_name in all_arg_names:
                if arg_name in kwargs:
                    args.append(kwargs[arg_name])
                elif arg_name in defaults:
                    args.append(defaults[arg_name])

        # guess regions based on keys of first arg
        regions = args[0].keys()

        # construct appropriate args list for parallel execution
        args_kwargs_list = [
            _regionalize_params(f, region, regions, args, kwargs)
            for region in regions]

        # process in parallel
        try:
            num_cpus = mp.cpu_count()
            p = mp.Pool(num_cpus)
            results = p.map(_unpack_for_map,
                            _pack_for_map(wrapped_function, args_kwargs_list))
            p.close()
        except Exception:
            print('encountered exception, falling back to series operation')
            results = map(wrapped_function, *zip(*args_kwargs_list))

        # repackage results
        if type(results[0]) == tuple:
            result = ({regions[i]: results[i][j]
                       for i in range(len(regions))}
                      for j in range(len(results[0])))
        else:
            result = {regions[i]: results[i] for i in range(len(regions))}

        return result

    return parallel_func


@parallelize_regions
def test_function_one(count):
    return count * 2


@parallelize_regions
def test_function_two(count, multiplier=4):
    return count * multiplier


@parallelize_regions
def test_function_three(x, y):
    return x * y, x + y


@parallelize_regions
def test_function_four(x, y):
    return x + y['s'] + y['t']


def main():
    print test_function_one(5)
    print test_function_one({'a': 4, 'b': 6})

    print test_function_two(5)
    print test_function_two({'a': 4, 'b': 6})
    print test_function_two({'a': 4, 'b': 6}, multiplier=3)
    print test_function_two({'a': 4, 'b': 6}, multiplier={'a': 5, 'b': 10})

    p, s = test_function_three(3, 4)
    print p, s
    p, s = test_function_three({'a': 4, 'b': 6}, 9)
    print p, s
    p, s = test_function_three({'a': 4, 'b': 6}, {'a': 4, 'b': 6})
    print p, s

    print test_function_four(7, {'s': 1, 't': -1})
    print test_function_four({'a': 6, 'b': 5},
                             {'s': {'a': 10, 'b': -10},
                              't': {'a': -100, 'b': 100}})


if __name__ == '__main__':
    main()
