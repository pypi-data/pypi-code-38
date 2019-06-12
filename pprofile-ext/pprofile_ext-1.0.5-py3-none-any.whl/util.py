import collections
import hashlib

import six

HASH_CACHE = dict()


def update(d, u):
    """
    Perform a recursive update of dictionary `d` with the dictionary `u`

    :param d: dictionary
    :param u: dictionary

    :return: updated dictionary
    """
    for k, v in six.iteritems(u):
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]

    return d


def hashkey(key):
    """Returns the sha1 hash for key"""
    # hash keys so we don't pay the sha1 overhead each time we call this one
    if key not in HASH_CACHE:
        HASH_CACHE[key] = hashlib.sha1(str.encode(key)).hexdigest()

    return HASH_CACHE[key]
