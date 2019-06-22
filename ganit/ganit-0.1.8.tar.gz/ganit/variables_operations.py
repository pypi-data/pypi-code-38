from .arithmetic_operations import basic_arithmetic
from .algebraic_operations import algebraic
from .trigonometric import trigonometric
from .logical import logical
from math import *
from datetime import *
from .handle_invalid_scenarios import ParserError

default_variables = {
    "pi": pi,
    "e": e,
    "tau": 2 * pi,
    "True": True,
    "False": False,
    "now": datetime.now(),
    "today": date.today()
}


def perform_operation(operator, arg):
    all_operations = {**basic_arithmetic, **algebraic,  **trigonometric, **logical}
    try:
        operation = all_operations.get(operator, None)
        return all_operations.get(operator, None)(arg)
    except Exception as e:
        raise ParserError(str(e))