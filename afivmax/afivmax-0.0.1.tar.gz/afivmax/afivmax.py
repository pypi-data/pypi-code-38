def afiv_max(*args, key=None, **kwargs):
    """

    max(iterable, *[, default=obj, key=func]) -> value
    max(arg1, arg2, *args, *[, key=func]) -> value

    参考了cpython的min_max的[实现](https://github.com/python/cpython/blob/master/Python/bltinmodule.c#L1583)



    [1]如果只有一个argument
        - 必须是iterable的
        - 将会返回最大的那个

    [2]如果有多个arguments:
        - 将会返回他们中最大的那个

    参数:
        - 其中default对于


    其他:
        - 原生的max在执行
            - max(1, 2, default=10) 会发生 TypeError
            - 所以如果定义: default=None 的话比较难完成这一个Feature

    """
    n_args = len(args)
    if n_args == 0:
        raise TypeError("No arguments provided!")
    n_kwargs = len(kwargs)
    if n_args > 1:
        try:
            it = iter(args)
        except TypeError:
            raise TypeError

        if kwargs.get("default", None) is not None:
            raise TypeError("Cannot specify a default for afiv_max() with multiple positional arguments")
    else:
        try:
            it = iter(args[0])
        except TypeError:
            raise TypeError("'{}' object is not iterable".format(type(args[0]).__name__))

        if n_kwargs > 1:
            raise TypeError("TypeError: function takes at most 2 arguments ({} given)".format(n_kwargs))

        if n_kwargs == 1:
            if "default" not in kwargs:
                raise TypeError(
                    "TypeError: '{}' is an invalid keyword argument for this function".format(list(kwargs.keys())[0]))

    max_item, max_val = None, None

    # one-pass
    for item in it:
        if key is not None:
            # if key is not None
            # we use what key func return as the value
            val = key(item)
            if val is None:
                raise TypeError("key func should return something!")
        else:
            val = item

        if max_val is None:
            max_item = item
            max_val = val
        else:
            try:
                is_new_king = val > max_val
            except TypeError:
                raise TypeError("'>' not supported between instances of '{}' and '{}'".format(
                    type(val).__name__, type(max_val).__name__))
            if is_new_king:
                max_item = item
                max_val = val

    if max_val is None:
        default = kwargs.get("default", None)
        if default is not None:
            max_item = default
        else:
            raise TypeError("Find the max value from an iterable which is empty!")

    return max_item
