# extended by op() and logic_op() below
__all__ = ['take', 'div', 'not_']

import operator

from ._operand import Operand
from ._tester import Tester, NotTester


def not_(value):
    return not value


def op(func):
    if isinstance(func, str):
        name = func
        logic = getattr(operator, func)
    else:
        name = func.__name__

    __all__.append(name)

    opclass = Operand[logic]

    def op(value, *right):
        if right:
            return logic(value, *right)
        return opclass(value)

    op.__name__ = name
    return op


add = op('add')
sub = op('sub')
mul = op('mul')
div = truediv = op('truediv')


def logic_op(logic):
    if isinstance(logic, str):
        name = logic
        logic = getattr(operator, logic)
    else:
        name = logic.__name__

    __all__.append(name)

    testerclass = Tester[logic]

    def op(value, *right):
        if right:
            return logic(value, *right)
        return testerclass(value)

    def not_tester(value):
        return NotTester(testerclass(value))

    setattr(not_, name, not_tester)

    op.__name__ = name
    return op


eq = logic_op('eq')
ne = logic_op('ne')
lt = logic_op('lt')
le = logic_op('le')
gt = logic_op('gt')
ge = logic_op('ge')


def in_(item, seq):
    return item in seq


in_ = logic_op(in_)
contains = logic_op('contains')


from ._take import take
from ._is import is_, is_not
