"""# Heat Dispersion
Learn about a numerical approach to simulating the spread of heat through a material

## Required Concepts
For-Loops and While-Loops
- basic usage of for-loops

Accessing Data Along Multiple Dimensions in an Array
- Indexing into, and updating a multi-dimensional array

“Vectorized” Operations: Optimized Computations on NumPy Arrays
- Using vectorized binary functions to perform basic arithmetic on arrays
"""


from typing import *
from numpy import ndarray


__seed__ = ["heatdispersion1", "heatdispersion2"]


def _time_it(student_func: Callable[[ndarray], ndarray],
             soln: Callable[[ndarray], ndarray],
             x: ndarray):
    from timeit import timeit
    from bwsi_grader.errors import StudentError
    soln_time = timeit("soln(x)", number=10, globals=locals())
    student_time = timeit("student_func(x)", number=10, globals=locals())
    if student_time > 3*soln_time:
        msg = """Your function's runtime is too long. Are you using for-loops?
                 
                 Your function is a {}-times slower than the vectorized solution.""".format(round(student_time/soln_time, 1))
        raise StudentError(msg)


def grader(student_func: Callable[[ndarray], ndarray], grade_ver: int):
    """ Tests the student's solution to "Three, Five, Three-Five"

    Parameters
    ----------
    student_func: Callable[[int], Union[str, int]]
       The student's solution function.

    grade_ver: int
    """
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from hashlib import sha224
    from bwsi_grader.errors import StudentError
    import numpy as np

    if grade_ver not in (1, 2):
        raise StudentError("Invalid grader setting: `grade_ver` was {}, must be 1 or 2".format(grade_ver))

    def soln(u: ndarray) -> ndarray:
        t = np.copy(u)
        t[1:-1, 1:-1] = (u[2:, 1:-1] + u[0:-2, 1:-1] + u[1:-1, 2:] + u[1:-1, 0:-2])/4
        return t
    # pad
    # pad
    # pad
    # pad
    # pad
    # test case from notebook
    u = np.ones((5, 5)) * 100
    u[1:-1, 1:-1] = 0
    compare_functions(student=student_func, soln=soln, fn_args=(u,))
    if grade_ver == 2:
        u = np.ones((100, 100)) * 100
        _time_it(student_func=student_func, soln=soln, x=u)

    # test case no.2
    u = np.ones((3, 5)) * 100
    u[1:-1, 1:-1] = 0
    compare_functions(student=student_func, soln=soln, fn_args=(u,))
    if grade_ver == 2:
        _time_it(student_func=student_func, soln=soln, x=u)

    for i in range(100):
        rand_shape = tuple(np.random.randint(2, 8, 2))
        u = np.round(np.random.rand(*rand_shape), 2)
        compare_functions(student=student_func, soln=soln, fn_args=(u,))

    print_passed(sha224(str.encode(__seed__[grade_ver - 1])).hexdigest())
