# -*- coding: utf-8 -*-

from .main import solution as solve
from .main import closest_k_pairs, get_index_of_quantile, show_linkage, distance_matrix

__version__ = "19.0.2.dev0"

__title__ = "closely"
__description__ = "Closely find closest pairs of points, eg duplicates, in a dataset"
__url__ = "https://github.com/justinshenk/closely"
__uri__ = __url__
__doc__ = __description__ + " <" + __url__ + ">"

__author__ = "Justin Shenk"
__email__ = "shenkjustin@gmail.com"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2019 " + __author__

__all__ = [
    "solve",
    "closest_k_pairs",
    "get_index_of_quantile",
    "show_linkage",
    "distance_matrix",
]
