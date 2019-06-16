"""
Code for configs.

Load files into Python objects that the code can use.
Also perform common mutations to the config class.
"""

from .config import MutationInfo, NULL
from .load import load


__all__ = [
    'load',
    'NULL',
    'MutationInfo',
]
