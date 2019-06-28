"""Wrapper Functions for pandas, numpy, and scikit learn"""

__version__ = "0.1.5"
__author__ = "adityasidharta"

from bamboos.color import color
from bamboos.date import date_single, date_double
from bamboos.encode import (
    fit_binary,
    fit_categorical,
    fit_label,
    fit_onehot,
    transform_binary,
    transform_categorical,
    transform_label,
    transform_onehot,
)
