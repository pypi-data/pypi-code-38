from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from typing import Callable, Optional, Tuple, Dict, Any, Sequence
from types import FunctionType, MethodType

from . import python
from .python import *

__all__ = ["compare_functions"]


print(f"Using grader version {__version__}")


def compare_functions(student: Callable,
                      soln: Callable,
                      fn_args: Optional[Tuple] = None,
                      fn_kwargs: Optional[Dict[str, Any]] = None,
                      function_name: str ="student_function",
                      comparison_function: Optional[Callable[[Any, Any], bool]] = None):
    """ Compares a student-function with a solution.

    Raises an exception with a descriptive error message that
    describes the nature of the mismatch, or, an error that
    occurred when calling one of the functions.

    Parameters
    ----------
    student : Callable
        The student's function
    soln : Callable
        The solution
    fn_args : Optional[Tuple]
        A tuple of the positional arguments to be unpacked to
        both functions.
    fn_kwargs : Optional[Dict[str, Any]]
        A dictionary of named arguments to be unpacked to both
        functions.
    comparison_function : Optional[Callable[[Any, Any], Union[bool, str]]]
        If specified, this will be used to compare the outputs of
        the respective functions. If it returns `False` and error
        message will print. If it returns a string, that will be printed
        as the error message.

    Raises
    ------
    DeveloperError
        An unexpected error or bad behavior (e.g. argument-mutation)
        occurred when invoking ``soln``.

    StudentError
        The student's result does not match the solution. Or, an
        unexpected error or bad behavior (e.g. argument-mutation)
        occurred when invoking ``fn_kwargs``.

    See Also
    --------
    bwsi_grader.compare.mismatch_error :  Responsible for comparing outputs/

    Examples
    --------
    >>> from bwsi_grader import compare_functions
    >>> def soln(x): return x**2
    >>> def student(x): return x + 2
    >>> compare_functions(student=student, soln=soln, fn_args=(3,))
    StudentError:
    Calling
        student_function(3)
    produced an incorrect result.

    Expected:
    9

    Got:
    5
    """
    from copy import deepcopy
    from .func_sig import form_func_sig, pad_indent
    from .compare import mismatch_error
    from .errors import DeveloperError, StudentError
    from itertools import chain

    if fn_args is None:
        fn_args = tuple()

    if not isinstance(fn_args, tuple):
        raise DeveloperError("`fn_args` must be a tuple "
                             "containing the positional arguments")

    if fn_kwargs is None:
        fn_kwargs = dict()

    if not isinstance(fn_kwargs, dict):
        raise DeveloperError("`fn_kwargs` must be a dictionary "
                             "containing the keyword arguments")

    # make copies of inputs to check for mutations
    args_orig = deepcopy(fn_args)
    kwargs_orig = deepcopy(fn_kwargs)

    sig = form_func_sig(*args_orig, **kwargs_orig, func_name=function_name)

    if not callable(student):
        raise StudentError(f"You must pass the grader your function. Instead, you "
                           f"passed the {type(student)}-type object: {repr(student)}.")

    # run student function, checking for Python errors and mutated inputs
    try:
        student_out = student(*fn_args, **fn_kwargs)
    except Exception as e:
        raise StudentError(f"\nCalling \n\t{pad_indent(sig, ln=4)}\nproduces the following error:"
                           f"\n\t{type(e).__name__}:{e}"
                           f"\nPlease run your function, as displayed above, in your Jupyter "
                           f"notebook to get a detailed stacktrace of the error, and debug "
                           f"your function.")

    # check for mutated inputs
    for f_arg, o_arg in zip(chain(fn_args, fn_kwargs.values()),
                            chain(args_orig, kwargs_orig.values())):
        if mismatch_error(f_arg, o_arg):
            raise StudentError(f"\nCalling \n\t{pad_indent(sig, ln=4)}\nmutated one of the function's "
                               f"input-arguments. The original argument:\n\n{repr(o_arg)}\n\nwas mutated to the "
                               f"value:\n\n{repr(f_arg)}\n\nRevise your function so that you copy this argument "
                               f"before changing it in-place.")

    # run solution function, checking for Python errors and mutated inputs
    try:
        soln_out = soln(*fn_args, **fn_kwargs)
    except Exception as e:
        raise DeveloperError(f"\nCalling \n\t{pad_indent(sig, ln=4)}\nproduces the following error:\n\t{e}\n")

    # check for mutated inputs
    for f_arg, o_arg in zip(chain(fn_args, fn_kwargs.values()),
                            chain(args_orig, kwargs_orig.values())):
        if mismatch_error(f_arg, o_arg):
            raise DeveloperError(f"\nCalling \n\t{pad_indent(sig, ln=4)}\nmutated one of the function's "
                                 f"input-arguments. The original argument:\n\n{repr(o_arg)}\n\nwas mutated to the "
                                 f"value:\n\n{repr(f_arg)}")

    # Return a string that reports any mismatch between function outputs
    # An empty string indicates that the results match
    mismatch_msg = mismatch_error(actual=student_out, desired=soln_out, comparison_function=comparison_function)
    if mismatch_msg:
        raise StudentError(f"\nCalling \n\t{pad_indent(sig, ln=4)}\nproduced an incorrect result.\n\n" + mismatch_msg)


def compare_objects(student_obj: Any, soln_obj: Any,
                    skip_attrs: Optional[Sequence[str]]=None,
                    included_private_attrs: Optional[Sequence[str]] = None):
    """ Compares two object and ensures that they have:
    - Matching names
    - Matching attributes (public only unless otherwise specified)

    Parameters
    ----------
    student_obj : Any,
    soln_obj : Any
    skip_attrs : Optional[Sequential[str]]
    included_private_attrs : Optional[Sequence[str]]

    Raises
    ------
    DeveloperError
        An unexpected error or bad behavior (e.g. non-existent attributes)
        occurred when inspecting ``soln``.

    StudentError
        The student's object does not match the solution.
    """
    from .errors import DeveloperError, StudentError

    def get_name(obj): return obj.__name__ if isinstance(obj, type) else type(obj)

    # ensure soln & student are both instance-objects or both class objects
    if isinstance(soln_obj, type) ^ isinstance(student_obj, type):
        type_ = "class-object" if isinstance(soln_obj, type) else "class-instance"
        other = "class-instance" if isinstance(soln_obj, type) else "class-object"
        raise StudentError(f"You passed the grader a {other}, it expected a {type_}")

    if get_name(student_obj) != get_name(soln_obj):
        raise StudentError(f"You passed the grader an object named {get_name(student_obj)}, expected "
                           f"an object named {get_name(soln_obj)}.")

    name = get_name(soln_obj)

    if skip_attrs is None:
        skip_attrs = []

    if included_private_attrs is None:
        included_private_attrs = []

    if set(included_private_attrs) - set(dir(soln_obj)):
        raise DeveloperError(f"The following attributes are not in the solution-object: "
                             f"{set(included_private_attrs) - set(dir(soln_obj))}")

    for attr in dir(soln_obj):
        if attr in skip_attrs or (attr not in included_private_attrs and attr.startswith("_")):
            continue
        if not hasattr(student_obj, attr):
            obj = getattr(soln_obj, attr)
            type_ = "method" if isinstance(obj, (MethodType, FunctionType)) else "attribute"
            raise StudentError(f"The provided class object, {name}, is missing the {type_}: `{attr}`\n"
                               f"Please revisit your class definition and implement `{name}.{type_}`")


def compare_attributes(*, student_attr: Any, soln_attr: Any, instance_repr: str, attr_name: str):
    from .errors import StudentError
    from .compare import mismatch_error
    mismatch_msg = mismatch_error(actual=student_attr, desired=soln_attr)
    if mismatch_error:
        raise StudentError(f"The attribute `{instance_repr}.{attr_name} returned the wrong value.\n"
                           + mismatch_msg)
