#/usr/bin/env python
# -*- coding:Utf-8 -*-

from random import randint, uniform, gauss, choice


def random_generator(length,
                     distrib=gauss, rd_args=(0, 1),
                     nbr_format=lambda x: round(x, 2),
                     v_min=None, v_max=None,
                     exact_mean=None):
    """ Generate a random list of value

    :param length: length of the dataset
    :param distrib: Distribution of the data set. It can be a function or string from ["randint", "uniform", "gauss", "choice"]
    :param rd_args: arguments to pass to distrib
    :param nbr_format: function which format value
    :param v_min: minimum accepted value
    :param v_max: maximum accepted value
    :param exact_mean: if set, the last generated number will be create in order that the computed mean is exacly equal to "exact_mean"

    >>> random_generator(10)
    >>> random_generator(10, distrib = uniform, rd_args = (5, 10))
    >>> random_generator(10, distrib = "uniform", rd_args = (5, 10))
    >>> random_generator(10, v_min = 0)
    >>> random_generator(10, exact_mean = 0)
    >>> random_generator(10, distrib = gauss, rd_args = (50,20), nbr_format = int)

    """
    # if exact_mean is set, we create automaticaly only length-1 value
    if exact_mean is not None:
        length = length - 1

    # build function to test created values
    if v_min is None:
        v1 = lambda x: True
    else:
        v1 = lambda x: x >= v_min
    if v_max is None:
        v2 = lambda x: True
    else:
        v2 = lambda x: x <= v_max
    validate = lambda x: v1(x) and v2(x)

    # get distrib function
    distribs = {
        "gauss": gauss,
        "uniform": uniform,
        "randint": randint,
        "choice": choice}
    try:
        distrib(*rd_args)
    except TypeError:
        distrib = distribs[distrib]

    # building values
    data = []
    for _ in range(length):
        valid = False
        while not valid:
            v = nbr_format(distrib(*rd_args))
            valid = validate(v)
        data.append(v)

    # Build last value
    if exact_mean is not None:
        last_v = nbr_format((length + 1) * exact_mean - sum(data))
        if not validate(last_v):
            raise ValueError(
                "Can't build the last value. Conflict between v_min/v_max and exact_mean")
        data.append(last_v)

    return data

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
