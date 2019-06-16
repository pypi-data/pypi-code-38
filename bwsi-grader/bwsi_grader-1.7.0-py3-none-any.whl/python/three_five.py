"""
# Three, Five, Three-Five
Write code that detects if a number is divisible by 3, 5, both, or neither.
Specifically, write a function that, given `x` (an integer), returns:

    - the string "threefive", if x is a multiple of both 3 and 5.
    - the string "three", if x is a multiple of 3 and not 5.
    - the string "five", if x is a multiple of 5 and not 3.
    - the integer x, if x is not divisible by either 3 or 5.

You may assume that your input is an integer greater than 0.

## Required Concepts
Basic Object Types
- basic math with Python
- strings

Conditional Statements
- basic usage of: if, else, elif


Basics of Functions
- the return statement
- basic function arguments

## Examples
```python
>>> student_func(3)
'three'

>>> student_func(5)
'five'

>>> student_func(15)
'threefive'

>>> student_func(2)
2
```
"""

from typing import Callable, Union


__seed__ = ["threefive"]


def grader(student_func: Callable[[int], Union[str, int]]):
    """ Tests the student's solution to "Three, Five, Three-Five"

    Parameters
    ----------
    student_func: Callable[[int], Union[str, int]]
       The student's solution function.
    """
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from random import randint
    from hashlib import sha224

    def soln(x: int) -> Union[str, int]:
        out = ''
        if x % 3 == 0:
            out += 'three'

        if x % 5 == 0:
            out += 'five'
        return out if out else x

    for input_ in (3, 5, 15, 2):
        compare_functions(student=student_func, soln=soln, fn_args=(input_,))

    for i in range(1000):
        compare_functions(student=student_func, soln=soln, fn_args=(randint(1, 1000),))

    print_passed(sha224(str.encode(__seed__[0])).hexdigest())
