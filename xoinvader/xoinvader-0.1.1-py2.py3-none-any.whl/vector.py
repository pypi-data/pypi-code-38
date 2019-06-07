"""Vector data structure."""

from functools import wraps
from math import sqrt
from typing import Any, TypeVar, Union, Tuple, Callable

import numpy as np


Numeric = TypeVar('Numeric', int, float)
#ForwardRef = TypeVar('ForwardRef', str)
OperandType = Union[str, type]#Union[ForwardRef, type]


def hypot(x: Numeric, y: Numeric, z: Numeric = 0) -> Numeric:
    return sqrt(x * x + y * y + z * z)


class OperandTypeError(ValueError):
    """Raises when the operand has unsupported type for the operation."""

    def __init__(self, value: Any, opname: str, optype: type) -> None:
        super().__init__(
         f'Operand {value} has unsupported type {type(value).__name__}, must be {optype.__name__}'
        )


def singlecontract(opname: str, optype: Union[Tuple[OperandType], OperandType]) -> Callable:
    """Simple runtime type checker for first function argument."""

    def wrapper(func):
        @wraps(func)
        def guard(value, *args, **kwargs):

            optypes = (optype,) if not isinstance(optype, tuple) else optype
            resolved = []
            for optype in optypes:
                if isinstance(optype, str):
                    resolved.append(_parse_type(optype))
                else:
                    resolved.append(optype)

            if not isinstance(value, tuple(resolved)):
                raise OperandTypeError(value, opname, optype)

            return func(value, *args, **kwargs)

        return guard

    return wrapper


def _parse_type(type_literal: str) -> type:
    try:
        return eval(compile(type_literal, '<string>', 'eval'))
    except SyntaxError:
        raise SyntaxError(f'Forward reference must be an expression, got {type_literal!r}')


class Vec2:

    __slots__ = ('x', 'y')

    def __init__(self, x: Numeric = 0, y: Numeric = 0) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f'Vec2(x={self.x}, y={self.y})'

    def __abs__(self) -> float:
        return hypot(self.x, self.y)

    def __add__(self, other: 'Vec2') -> 'Vec2':
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, other):
        if isinstance(other, Vec2):
            pass
        elif isinstance(other, (int, float)):
            pass
        else:
            raise ValueError(f'Type {0} is unsupported for {1}')

    def __truediv__(self, other):
        pass

    def __eq__(self, other):
        if isinstance(other, Vec2):
            return self.x == other.x and self.y == other.y

        raise ValueError()

class Vec3:

    __slots__ = ('x', 'y', 'z')

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    @property
    def opposite(self, other):
        pass

    def __repr__(self):
        return f'Vec3(x={self.x}, y={self.y}, z={self.z})'

    def __abs__(self):
        return hypot(self.x, self.y, self.z)

    @singlecontract('add', 'Vec3')
    def __add__(self, other):
        """Vec3(1, 2, 3) + Vec3(4, 5, 6) = Vec3(5, 7, 9)"""

        return Vec3(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    @singlecontract('sub', 'Vec3')
    def __sub__(self, other):
        """Vec3(3, 3, 3) - Vec3(2, 2, 2) = Vec3(1, 1, 1)"""

        return self.__add__(-other)

    @singlecontract('mul', (int, float, 'Vec3'))
    def __mul__(self, other):
        """-->
        * Vec3(3, 3, 3) * 3 = Vec3(9, 9, 9)
        * Vec3(3, 3, 3) * 
        """

        raise NotImplementedError

    def __truediv__(self, other):
        pass

    @singlecontract('eq', 'Vec3')
    def __eq__(self, other):

        return self.x == other.x and self.y == other.y and self.z == other.z
