"""max的一个implementation
"""


def afiv_max(*args, key=None, **kwargs):
    """取出最大值
    max(iterable, \*[, default=obj, key=func]) -> value\n
    max(arg1, arg2, \*args, \*[, key=func]) -> value

    Note:
        使用``kwargs``是因为原生的max在执行``max(1, 2, default=10)``会raise一个TypeError, 使用``default=None``比较难完成这一个Feature.

    Args:
        args: iterable or arg1,arg2,...
            取最大值的source
        key: func, optional
            从args取出比较对象的函数
        default: None or DEFAULT_VALUE
            1. 如果args的第一个元素为iterable且为空时返回的值\n
            2. 如果是arg1,arg2,的形式会raise一个TypeError

    Returns:
        max_item: 就是返回最大值

    Raises:
        TypeError:
            1. 当args为空的时候\n
            2. 有除了default和key以外参数的时候\n
            3. 当arg1,arg2,...的时候有default参数的时候\n
            4. key返回的值不支持'>'的时候\n
            5. args为iterable且为空且default没有提供的时候


    """
    n_args = len(args)
    if n_args == 0:
        raise TypeError("No arguments provided!")
    n_kwargs = len(kwargs)
    if n_args > 1:
        # args is always iterable since itself is a list
        it = iter(args)

        if "default" in kwargs:
            raise TypeError("Cannot specify a default for afiv_max() with multiple positional arguments")

        if n_kwargs > 0:
            raise TypeError("TypeError: function takes at most 2 arguments ({} given)".format(n_kwargs))

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
        if "default" in kwargs:
            max_item = kwargs["default"]
        else:
            raise TypeError("Find the max value from an iterable which is empty!")

    return max_item
