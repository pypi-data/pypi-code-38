from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from future.utils import string_types
standard_library.install_aliases()
from collections import Sequence
import inspect
import sys
import logging
import warnings


logger = logging.getLogger(__name__)
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


def generic_op(self, other, func, format_alias):
    ''' Allows timedeltas to be summed/subtracted to everything that can be casted to self type'''

    try:
        other = self.__class__(other)
    except (TypeError, ValueError):
        return NotImplemented

    res = self.__class__(func(other))

    try:
        if self.has_custom_alias() or other.has_custom_alias():
            res.alias = format_alias.format(self.alias, other.alias)
    except AttributeError:
        warnings.warn("Object does not seem to support alias.")

    return res

class NoDuplicatesDict(dict):
    def __setitem__(self, key, value):
        if key in self.keys():
            raise ValueError("The name {} is already defined as a mark.".format(key))
        dict.__setitem__(self, key, value)



def _copy_signature(wrapper, wrapped):
    if sys.version_info.major < 3:
        # Not suported on Python 2.x
        pass
    else:
        wrapper.__signature__ = inspect.signature(wrapped)


def _recursive_map(seq, func):
    for item in seq:
        if isinstance(item, Sequence) and not isinstance(item, string_types):
            yield type(item)(recursive_map(item, func))
        else:
            yield func(item)


def recursive_map(item, func):
    if isinstance(item, Sequence) and not isinstance(item, string_types):
        return tuple(_recursive_map(item, func))
    else:
        return func(item)


def parse_to_tuple(item):
    """If is a single value instead of tuple, create a tuple with the same value"""

    # I think it looks better without this on the plot title, less polluted.
    # So we cast back to tuple whenever we have an AliasTuple
    #if isinstance(item, AliasTuple):
    #    return item

    try:
        item0 = item[0]
        item1 = item[1]
    except TypeError:  # not a tuple/list, single value
        item0 = item
        item1 = item
    return (item0, item1)


def validate_range(item, reference=None, type_cast=None, limit=False):
    """Converts single numbers to tuple, cast them to same type as reference if provided and adjust limits to the reference limits."""

    item = parse_to_tuple(item)
    item0 = item[0]
    item1 = item[1]
    range_consistent = item0 <= item1

    if not range_consistent:
        raise ValueError("Lower value is greater than the upper value for item {}. Range is nonexistant.".format(item))

    if reference is not None:
        if type_cast is None:
            type_cast = reference[0].__class__

        if type_cast != type(item0):
            try:
                item0 = type_cast(item0)
                item1 = type_cast(item1)
            except:
                raise TypeError("Arguments {} couldn't be converted to type {}".format(item, type_cast))
        if limit:

            minimum = reference[0]
            maximum = reference[-1]

            # item0 = item0 if item0 >= minimum else minimum
            # item1 = item1 if item1 <= maximum else maximum
            if item0 < minimum:
                logger.warning(
                    "Desired time [{}] is anterior to earliest signal time. Using earlist signal time [{}]".format(
                        item0, minimum))
                item0 = minimum
            if item1 > maximum:
                logger.warning(
                    "Desired time [{}] is later to latest signal time. Using latest signal time [{}]".format(item1,
                                                                                                             maximum))
                item1 = maximum
    return item0, item1

