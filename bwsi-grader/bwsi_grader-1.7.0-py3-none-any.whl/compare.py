from collections.abc import Sequence
import numpy as np
from typing import Any, Optional, Callable
from math import isclose
from numbers import Real, Integral


def _same_dtype(x: np.ndarray, y: np.ndarray) -> bool:
    """
    Checks if `x` and `y` are subtypes of the same generic
    numpy data type. E.g. if `x` and `y` both store integers.

    Parameters
    ----------
    x : np.ndarray
    y : np.ndarray

    Returns
    -------
    bool
        `True` if `x` and `y` have the same generic dtype.
    """
    return np.issubdtype(x.dtype, np.floating) and np.issubdtype(y.dtype, np.floating) or \
           np.issubdtype(x.dtype, np.integer) and np.issubdtype(y.dtype, np.integer) or \
           np.issubdtype(x.dtype, np.bool_) and np.issubdtype(y.dtype, np.bool_)


def _same_abstract_numeric(x: Any, y: Any) -> bool:
    """
    Checks if `x` and `y` both numeric types and belong to the
    same abstract numeric type

    Parameters
    ----------
    x : Any
    y : Any

    Returns
    -------
    bool
    """
    if isinstance(x, bool) or isinstance(y, bool):
        return False

    if not isinstance(x, Real) or not isinstance(y, Real):
        return False

    if isinstance(x, Integral):
        return isinstance(y, Integral)

    if isinstance(y, Integral):
        return isinstance(x, Integral)
    return True


def check_arrays(actual: np.ndarray, desired: np.ndarray) -> str:
    if isinstance(actual, np.ndarray):
        if actual.shape != desired.shape:
            return f"Expected a shape-{desired.shape} array with value:\n" \
                   f"{repr(desired)}\n\n" \
                   f"Got a shape-{actual.shape} array with value:\n" \
                   f"{repr(actual)}"

        if not _same_dtype(actual, desired):
            return f"Expected an array of dtype-{desired.dtype} with value:\n" \
                   f"{repr(desired)}\n\n" \
                   f"Got an array of dtype-{actual.dtype} with value:\n" \
                   f"{repr(actual)}"

        if not np.allclose(actual, desired, atol=1e-5, rtol=1e-5):
            return f"Expected a shape-{desired.shape} array with value:\n" \
                   f"{repr(desired)}\n\n" \
                   f"Got a shape-{actual.shape} array with value:\n" \
                   f"{repr(actual)}"
    return ""


def mismatch_error(actual: Any, desired: Any,
                   comparison_function: Optional[Callable[[Any, Any], bool]] = None) -> str:
    """
    Compares two objects and returns a descriptive message
    describing the nature of their mismatched types/values.

    Returns an empty string if the two objects match.

    Parameters
    ----------
    actual : Any
        The actual object that was produced.

    desired : Any
        The desired object.

    comparison_function : Optional[Callable[[Any, Any], Union[bool, str]]]
        If specified, this will be used to compare the outputs of
        the respective functions. If it returns `False` and error
        message will print. If it returns a string, that will be printed
        as the error message.

    Returns
    -------
    mismatch_msg : str
        A message describing the nature of the mismatch between the
        actual object and the desired one. The string is empty if the
        two are found to match.

    Notes
    -----
    NumPy arrays are handled gracefully - shapes are compared up front,
    and data types are assured to be of the same parent-type (e.g.
    float64 and float32 are agreeable).
    """
    from .errors import DeveloperError

    if comparison_function is not None:
        o = comparison_function(actual, desired)
        if not isinstance(o, (bool, str)):
            raise DeveloperError(f"comparison_function({repr(actual)}, {repr(desired)}) "
                                 f"returned type `{type(o)}`.")
        else:
            return o if o else ""

    if type(actual) is not type(desired) and not _same_abstract_numeric(actual, desired):
        return f"Expected an output of type-{type(desired)} with value:\n{repr(desired)}\n\n" \
               f"Got an output of type-{type(actual)} with value:\n{repr(actual)}"

    if isinstance(actual, float) or isinstance(desired, float):
        if not isclose(actual, desired, rel_tol=1e-6, abs_tol=1e-6):
            return f"Expected:\n" \
                   f"{repr(desired)}\n\n" \
                   f"Got:\n" \
                   f"{repr(actual)}"
        else:
            return ""

    if isinstance(actual, np.ndarray):
        return check_arrays(actual, desired)

    if isinstance(desired, Sequence):
        if len(desired) != len(actual):
            return f"The expected output has length-{len(desired)}:\n" \
                   f"{repr(desired)}\n\n" \
                   f"Got an output of length-{len(actual)}:\n" \
                   f"{repr(actual)}"

    # if type(desired).__name__ not in dir(__builtins__) and not hasattr(desired, "__eq__"):
    #     return ""

    if isinstance(desired, (list, tuple)) and any(isinstance(i, np.ndarray) for i in desired):
        for n, (desired_item, actual_item) in enumerate(zip(desired, actual)):
            msg = mismatch_error(desired=desired_item, actual=actual_item)
            if msg:
                return f"Element {n} of the student's solution " \
                       f"does not match the corresponding element of the solution:\n{msg}." \
                       f"\n\nThe full expected solution is:\n"\
                       f"{repr(desired)}\n\n" \
                       f"Got:\n" \
                       f"{repr(actual)}"
    elif actual != desired:
        return f"Expected:\n" \
               f"{repr(desired)}\n\n" \
               f"Got:\n" \
               f"{repr(actual)}"
    return ""
