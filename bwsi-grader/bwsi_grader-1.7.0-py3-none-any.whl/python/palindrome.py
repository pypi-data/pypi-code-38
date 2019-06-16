"""
# Is it a palindrome?

A palindrome is a word, phrase, or sequence that reads the same backward as forward, e.g., madam or nurses run.

Write code that takes a string and returns `True` if that string is a palindrome.
Your analysis should be case-insensitive and should disregard spaces. E.g. "Race car" should be considered a palindrome,
despite beginning with a capitalized letter and containing a space. None of the strings will contain punctuation.
Thus your function should produce the following behavior:

- "Are we not drawn onward to new era" -> True
- "batman" -> False

## Required Concepts
Basic Object Types
- strings
- checking equality

Sequence Types
- slicing

## Examples
```python
>>> student_func("Race car")
True

>>> student_func("RaCeCaR")
True

>>> student_func("apple")
False
```
"""

from typing import Callable


__seed__ = ["palindrome"]


def grader(student_func: Callable[[str], bool]):
    """ Tests the student's solution to "Is it a Palindrome?"

    Parameters
    ----------
    student_func: Callable[[str], bool]
       The student's solution function.
    """
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from hashlib import sha224

    def soln(x: str) -> bool:
        x = x.lower().replace(" ", "")
        return x == x[::-1]

    # check some standard cases
    for input_ in ("cat", "Race Car", "RaCeCaR", "Python", "nurses run", "HHH"):
        compare_functions(student=student_func, soln=soln, fn_args=(input_,))

    phrases = ['A but tuba',
               'A car a man a maraca',
               'A dog a plan a canal pagoda',
               'A dog A panic in a pagoda',
               'A lad named E Mandala',
               'A man a plan a canal Panama',
               'A man a plan a cat a ham a yak a yam a hat a canalPanama',
               'A new order began a more Roman age bred Rowena',
               'A nut for a jar of tuna',
               'A Santa at Nasa',
               'Desserts I desire not so long no lost one rise distressed',
               'Drat such custard',
               'Evil axis sides reversed is six alive',
               'Gate man sees name garage man sees name tag',
               'Im a fool aloof am I',
               'Socrates Socrates',
               'B',
               'aaabaaa',
               'aaabcaaa']

    for phrase in phrases:
        compare_functions(student=student_func, soln=soln, fn_args=(phrase,))

    print_passed(sha224(str.encode(__seed__[0])).hexdigest())
