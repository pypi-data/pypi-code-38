from .attribute_dict import AttributeDict
from .paths import cwd
from .k_grid import d2k
from .geometry import get_cubicness
from .numerics import clean_matrix
from .utils import Timer, progressbar, bold, talk
from .warnings import warn


def list_dim(a):
    """ dimension of a (nested) pure Python list """
    if not type(a) == list:
        return []
    return [len(a)] + list_dim(a[0])


def list2str(lis):
    """convert list to string"""
    return "[{}]".format(", ".join([str(el) for el in lis]))

