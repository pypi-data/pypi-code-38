#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

import six


class ReadOnlyDict(dict):
    def __init__(self, dict_to_protect=None):
        super(ReadOnlyDict, self).__init__(dict_to_protect)

    def __setitem__(self, key, value):
        raise TypeError("__setitem__ is not permitted")

    def __delitem__(self, key):
        raise TypeError("__delitem__ is not permitted")

    def update(self, other=None, **kwargs):
        raise TypeError("update is not permitted")


def check_keys(keys):
    """
    Check the validity of the keys dict
    """
    assert keys and isinstance(keys, dict) and len(keys) > 0, "Keys are mandatory (non empty dict)"

    # Make sure values are unique
    assert len(set(six.viewvalues(keys))) == len(keys), "Same value for more than one key"


def encode_dict(d):
    """
    Encode dictionary into utf-8

    :param dict[basestring, object] d: Dict to encode
    :rtype: dict[str, str]
    """
    return {k.encode(): v.encode() if isinstance(v, six.text_type) else v for k, v in six.iteritems(d)}


def decode_dict(d):
    """
    Decode dictionary back into unicode

    :param dict[str, object] d: Keys
    :rtype: dict[unicode, object]
    """
    return {k.decode(): v.decode() if isinstance(v, bytes) else v for k, v in six.iteritems(d)}
