r"""
# Pizza Shop
You work at a pizza restaurant, which is starting to accept orders online. You need to
provide a python function that will accept an arbitrary order as its arguments,
and compute the correct price for the order.

Your cost-calculator function should have four arguments:
- pizzas
- drinks
- wings
- coupon


A single pizza order is formed as a list of toppings. For example
- A pizza with no toppings (other than cheese and sauce is: [] (an empty list)
- A pizza with pepperoni and a double order of olives is : ["pepperoni", "olives", "olives"]

*An arbitrary number of pizzas may be ordered, including no pizzas as all*

Drinks come in as a named order (i.e. a keyword argument 'drinks'). If drinks are ordered,
they are specified as a list of sizes (possible sizes: "small", "medium", "large", "tub"). For example, `drinks=["small", "small", "large"]` would indicate an order including two small drinks and a large drink.

Wings come in as a named order as well (keyword argument 'wings'). If wings are ordered,
they are specified as a list of integers (possible sizes: 10, 20, 40, 100). For example, `wings=[20]` would indicate a single order of 20-piece wings.

A coupon may be specified as the keyword argument 'coupon'. It is will be a single
floating point number between 0 and 1. This indicates the fraction of the *pre-tax*
price that is to be subtracted. For example `coupon=.25` would indicate a 25%-off coupon.

A 6.25% tax is applied to every order. The tax is computed on the total cost of the
order *before a coupon is applied*

Round the price to the nearest cent, using the built-in function round. `round(x, 2)` will round `x` to two decimal places.

## Prices
The prices are as follows:

**Pizza**
- \$13.00

**Toppings**
- pepperoni : \$1.00
- mushroom : \$0.50
- olive : \$0.50
- anchovy : \$2.00
- ham : \$1.50

**Drinks**
- small : \$2.00
- medium : \$3.00
- large : \$3.50
- tub : \$3.75

**Wings**
- 10 : \$5.00
- 20 : \$9.00
- 40 : \$17.50
- 100 : \$48.00


## Examples
The following is an order for a plain pizza, a ham and anchovy pizza, two "tub"-sized
drinks, with a 10%-off coupon:
```python
>>> cost_calculator([], ["ham", "anchovy"], drinks=["tub", "tub"], coupon=0.1)
35.61
```

This order consists only of a small drink.
```python
>>> cost_calculator(drinks=["small"])
2.12
```

This is an order of two plain pizzas, a pizza with double-pepperoni, an order of a 10-piece and a 20-piece wings, and a small drink.
```python
>>> cost_calculator([], [], ["pepperoni", "pepperoni"], wings=[10, 20], drinks=["small"])
60.56
```

## Details
You can assume that the front-end of the website will never pass your function erroneous
orders. That is, you will never receive orders for items that do not exist nor
items that contain typos.

Consider defining individual functions responsible for computing
the cost of the pizzas, drinks, and wings, respectively. Have `cost_calculator`
invoke these internally. Alternatively, you can read ahead about dictionaries and make nice
use of these in this problem.

Our `cost_calculator` signature is empty. Part of the assignment is to come up with the
correct function signature!

## Required Concepts
Basic Object Types
- basic math with python

For-Loops and While-Loops
- basic use of for-loops and/or iterables

Basics of Functions
- functions
  - passing a function an arbitrary number of positional arguments
  - specifying default values for arguments
- dictionaries would be useful here
```
"""

from typing import *


__seed__ = ["pizzashop"]


def gen_pizza(toppings, max_num=4):
    from random import randint, choices
    num = randint(0, max_num)
    return [choices(list(toppings), k=randint(0,3)) for i in range(num)]


def gen_items(items, max_num=3):
    from random import randint, choices
    num = randint(0, max_num)
    return choices(list(items), k=num) if num else None


order = List[str], Optional[List[str]], Optional[List[int]], Optional[float]


def grader(student_func: Callable[[*order], float]):
    """ Tests the student's solution to "pizza shope"

    Parameters
    ----------
    student_func: Callable[[order], float]
       The student's solution function.
    """
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from hashlib import sha224
    from collections import OrderedDict

    toppings = dict(pepperoni=1.,
                    mushroom=0.5,
                    olive=0.5,
                    anchovy=2.,
                    ham=1.5)

    dr = dict(small=2.,
              medium=3.,
              large=3.5,
              tub=3.75)

    wi = {10: 5.,
          20: 9,
          40: 17.5,
          100: 48.}

    def soln(*pizzas: List[str],
             drinks: Optional[List[str]] = None,
             wings: Optional[List[int]] = None,
             coupon: Optional[float] = None) -> float:
        # total cost due to pizzas
        cost = 13.*len(pizzas)
        cost += sum(sum(toppings[i] for i in x) for x in pizzas)

        # total cost due to drinks
        if drinks is not None:
            cost += sum(dr[i] for i in drinks)

        # total cost due to wings
        if wings is not None:
            cost += sum(wi[i] for i in wings)

        discount = cost*coupon if coupon is not None else 0.
        cost += cost*.0625
        cost -= discount
        return round(cost, 2)

    std_pizzas = [[[]],
                  [],
                  [["pepperoni"], []],
                  [[],[]]]

    std_orders = [{},
                  OrderedDict([("drinks", ["tub"]), ("coupon", 0.1)]),
                  {"wings": [10, 20]},
                  OrderedDict([("drinks", ["tub", "small"]),
                               ("wings", [10, 10]), ("coupon", 0.1)])]

    for pizzas, items in zip(std_pizzas, std_orders):
        compare_functions(student=student_func, soln=soln,
                          fn_args=tuple(pizzas), fn_kwargs=items)

    for i in range(1000):
        pizzas = gen_pizza(toppings)
        items = {}

        d = gen_items(dr)
        if d is not None:
            items["drinks"] = d

        w = gen_items(wi)
        if w is not None:
            items["wings"] = w

        compare_functions(student=student_func, soln=soln,
                          fn_args=tuple(pizzas), fn_kwargs=items)

    print_passed(sha224(str.encode(__seed__[0])).hexdigest())
