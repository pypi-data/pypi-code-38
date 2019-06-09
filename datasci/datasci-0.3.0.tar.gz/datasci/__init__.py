from typing import TypeVar
from numbers import Number
import math
import numpy as np

__version__ = None

try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution('datasci').version
except Exception:
    pass

Numeric = TypeVar('Numeric', Number, np.ndarray)


def logistic(x: Numeric) -> Numeric:
    """
    Compute the standard logistic function,
    which maps x ∈ ℝ into the range (0, 1).
    As x → +∞, logistic(x) → 1
    As x → -∞, logistic(x) → 0
    """
    return 1 / (1 + np.exp(-x))


def logit(p: Numeric) -> Numeric:
    """
    Compute the logit (AKA log-odds) function,
    which maps a probability into ℝ.
    """
    assert 0.0 <= p <= 1.0, 'p must be in the range [0, 1]'
    if p == 0:
        return -math.inf
    if p == 1:
        return math.inf
    return np.log(p / (1 - p))
