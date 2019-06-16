"""
# Relaxation Numerical Method
Learn about a numerical approach to solving math problems of the form: f(x) = x.

## Required Concepts
Basic Object Types
- basic math with Python
- the standard library's `math` module
- lists

Basics of Functions
- basic use of functions
- functions are objects

For-Loops and While-Loops
- basic usage of for-loops and while-loops

## Examples
Define the function:

```python
from math import tanh, exp

def f(x):
    return tanh(5*x)


def g(x):
    return 2 - exp(-x)
```

and then calling your relaxation function, passing it this function, an initial guess of $x_{o}=0.5$, and instructing it to perform 5 iterations, should produce the following list:

```python
>>> relaxation_method1(f, xo=-.5, num_it=5)
[-0.5,
 -0.98661429815143031,
 -0.99989620032332682,
 -0.99990910997226823,
 -0.99990912170456125,
 -0.99990912171522284]

 >>> relaxation_method2(func=g, xo=91.0, tol=1e-10, max_it=3)
 [91.0, 2.0, 1.8646647167633872]
```
"""

from typing import *


__seed__ = ["relaxationmethod1", "relaxationmethod2"]


def _reprd_func(f: Callable, string: str) -> Callable:
    class F():
        def __repr__(self): return f"lambda x: {string}"
        def __call__(self, x): return f(x)
        def __eq__(self, x): return True
    return F()


def grader1(student_func: Callable[[Callable[[float], float]], List[float]]):
    """ Tests the student's solution to "Three, Five, Three-Five"

    Parameters
    ----------
    student_func: Callable[[int], Union[str, int]]
       The student's solution function.
    """
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from random import randint, random
    from hashlib import sha224
    from math import tanh

    def soln(f, xo, num_it):
        rollout = [xo]
        for i in range(num_it):
            x = f(xo)
            rollout.append(x)
            xo = x
        return rollout

    # pad
    # pad
    # pad
    # pad
    # pad

    print("Finding fixed-points for the function: f(x) = x**2")
    f1 = _reprd_func(lambda x: x**2, "x**2")

    for input_ in range(100):
        input_ = (f1,)
        kwargs = dict(xo=round(random(), 2), num_it=randint(0, 10))
        compare_functions(student=student_func, soln=soln, fn_args=input_, fn_kwargs=kwargs)

    print("Finding fixed-points for the function: f(x) = tanh(4*x)")

    f2 = _reprd_func(lambda x: tanh(4*x), "tanh(4*x)")

    for input_ in range(100):
        input_ = (f2,)
        kwargs = dict(xo=round(random(), 2), num_it=randint(0, 10))
        compare_functions(student=student_func, soln=soln, fn_args=input_, fn_kwargs=kwargs)

    print_passed(sha224(str.encode(__seed__[0])).hexdigest())


def grader2(student_func: Callable[[Callable[[float], float], float, float, int], List[float]]):
    """ Tests the student's solution to "Three, Five, Three-Five"

    Parameters
    ----------
    student_func: Callable[[Callable[[float], float], float, float, int], List[float]]
       The student's solution function.
    """
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from random import randint, random
    from hashlib import sha224
    from math import exp

    def error_estimate(x0, x1, x2):
        denom = 2*x1 - x0 - x2
        if denom == 0:
            denom = 1e-14
        return abs((x1 - x2)**2/denom)

    def soln(f, xo, tol, max_it=500):
        rollout = [xo, f(xo), f(f(xo))]
        while max_it > len(rollout) and error_estimate(*rollout[-3:]) > tol:
            rollout.append(f(rollout[-1]))
        return rollout[:max_it]

    # pad
    # pad
    # pad
    # pad
    # pad

    f1 = _reprd_func(lambda x: 2 - exp(-x), "2 - exp(-x)")
    print("Finding fixed-points for the function: f(x) = 2 - exp(-x)")

    for it in [1, 2, 3, 10, 100]:
        input_ = (f1,)
        kwargs = dict(xo=91., tol=1e-10, max_it=it)
        compare_functions(student=student_func, soln=soln, fn_args=input_, fn_kwargs=kwargs)

    for i in range(1000):
        xo = random() * 100
        tol = random()/100
        max_it = randint(1, 1000)
        input_ = (f1,)
        kwargs = dict(xo=xo, tol=tol, max_it=max_it)
        compare_functions(student=student_func, soln=soln, fn_args=input_, fn_kwargs=kwargs)

    print_passed(sha224(str.encode(__seed__[1])).hexdigest())
