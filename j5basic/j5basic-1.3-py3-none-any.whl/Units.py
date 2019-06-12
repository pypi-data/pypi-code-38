# -*- coding: utf-8 -*-

from __future__ import division

import operator
import decimal
import sys

if sys.version_info.major < 3:
    numbers = (int, long, float, decimal.Decimal)
else:
    numbers = (int, float, decimal.Decimal)

def Identity(x):
    """Returns the object given to it"""
    return x

class Conversion(object):
    """Operation that converts a number from one unit to another"""
    def __init__(self, f, *args):
        self.f = f
        self.args = args

    def __call__(self, x):
        """Actually perform the conversion"""
        return self.f(x, *self.args)

    def __eq__(self, other):
        """Compare to another Conversion"""
        if type(other) != Conversion:
            raise NotImplementedError("Cannot compare %r and %r" % (self, other))
        return self.f == other.f and self.args == other.args

    def __repr__(self):
        """Represents the conversion"""
        return "%s(%s, *%r)" % (type(self).__name__, self.f, self.args)

    def __mul__(self, other):
        """Returns a related Conversion"""
        if not isinstance(other, Conversion):
            raise NotImplementedError("Cannot multiply %r and %r" % (self, other))
        return SequentialConversion(self, other)

    def __truediv__(self, other):
        """Returns a related Conversion"""
        if not isinstance(other, Conversion):
            raise NotImplementedError("Cannot divide %r and %r" % (self, other))
        return SequentialConversion(self, DivideBy(other))

def DivideBy(conversion):
    """Returns the inverse of a Conversion if possible"""
    if isinstance(conversion, SequentialConversion):
        return SequentialConversion(*[DivideBy(c) for c in conversion.conversions])
    if conversion.f == operator.mul:
        return Conversion(operator.truediv, *conversion.args)
    if conversion.f == operator.truediv:
        return Conversion(operator.mul, *conversion.args)
    if conversion.f == Identity:
        return conversion
    raise ValueError("Could not calculate the inverse of %r" % (conversion,))

class SequentialConversion(Conversion):
    """Performs conversions in sequence"""
    def __init__(self, *conversions):
        self.conversions = []
        for c in conversions:
            if c != identity:
                self.conversions.append(c)
        self.simplify()

    def simplify(self):
        """Perform the most basic simplifications"""
        # reduced nested sequences
        new_conversions = []
        for c in self.conversions:
            if type(c) == Conversion:
                new_conversions.append(c)
            elif type(c) == SequentialConversion:
                new_conversions.extend(c.conversions)
            else:
                break
        else:
            self.conversions = new_conversions
        # reduce sequences of multiplications and divisions
        while True:
            n, d = 1, 1
            have_sequence = False
            new_conversions = []
            for c in self.conversions:
                if type(c) == Conversion and c.f == operator.mul:
                    n = n * c.args[0]
                    have_sequence = True
                elif type(c) == Conversion and c.f == operator.truediv:
                    d = d * c.args[0]
                    have_sequence = True
                else:
                    if have_sequence:
                        if n == d:
                            pass
                        elif abs(n / d) > 1:
                            new_conversions.append(Conversion(operator.mul, n / d))
                        else:
                            new_conversions.append(Conversion(operator.truediv, d / n))
                        have_sequence = False
                        n, d = 1, 1
                    new_conversions.append(c)
            else:
                if have_sequence:
                    if n == d:
                        pass
                    elif abs(n / d) > 1:
                        new_conversions.append(Conversion(operator.mul, n / d))
                    else:
                        new_conversions.append(Conversion(operator.truediv, d / n))
            if len(new_conversions) >= len(self.conversions):
                break
            self.conversions = new_conversions

    def __call__(self, x):
        """Actually perform the conversions"""
        for c in self.conversions:
            x = c(x)
        return x

    def __repr__(self):
        """Represents the conversion"""
        return "%s(%s)" % (type(self).__name__, ",".join([repr(c) for c in self.conversions]))

    def __str__(self):
        """Simpler representation of conversion"""
        s = []
        for c in self.conversions:
            if type(c) == Conversion and c.f == operator.mul:
                s.append("*%s" % (c.args[0],))
            elif type(c) == Conversion and c.f == operator.truediv:
                s.append("/%s" % (c.args[0],))
            elif type(c) == Conversion and c.f == Identity:
                pass
            else:
                s.append(str(c))
        return "".join(s)

    def __eq__(self, other):
        """Compare to another Conversion"""
        if type(other) == Conversion:
            if not self.conversions:
                return other.f == Identity
            if len(self.conversions) != 1:
                return False
            return self.conversions[0] == other
        elif type(other) == SequentialConversion:
            if len(self.conversions) != len(other.conversions):
                return False
            for sc, oc in zip(self.conversions, other.conversions):
                if sc != oc:
                    return False
            return True
        else:
            raise NotImplementedError("Cannot compare %r and %r" % (self, other))

    def __ne__(self, other):
        """Compares self to other and returns whether they are unequal"""
        return not self.__eq__(other)

identity = Conversion(Identity)

class Unit(object):
    """A Base Unit that can be used in calculations"""
    def __init__(self, name, base_units, op):
        """Constructs a Unit with the given name"""
        # TODO: handle abbreviations too
        self.name = name
        self.native_name = False
        self.base_units = base_units
        self.op = op

    def __repr__(self):
        """Returns a representation of the type"""
        n, d = [], []
        for base, exponent in list(self.base_units.items()):
            if exponent == 1:
                n.append(base.name)
            elif exponent > 0:
                n.append("%s ** %s" % (base.name, exponent))
            elif exponent == -1:
                d.append(base.name)
            elif exponent < 0:
                d.append("%s ** %s" % (base.name, exponent))
        if not n:
            n = ["1"]
        s = " * ".join(n)
        if d:
            if len(d) > 1:
                s += "/ (%s)" % (" * ".join(d))
            else:
                s += "/ %s" % (d[0])
        return "%s(%s, %r)" % (type(self).__name__, s, self.op)

    def __str__(self):
        if self.native_name:
            return self.name
        n, d = [], []
        for base, exponent in list(self.base_units.items()):
            if exponent == 1:
                n.append(base.name)
            elif exponent > 0:
                n.append("%s^%s" % (base.name, exponent))
            elif exponent == -1:
                d.append(base.name)
            elif exponent < 0:
                d.append("%s^%s" % (base.name, exponent))
        if not n:
            n = ["1"]
        s = "*".join(n)
        if d:
            if len(d) > 1:
                s += "/(%s)" % ("*".join(d))
            else:
                s += "/%s" % (d[0])
        return ("%s %s") % (s, self.op)

    def __eq__(self, other):
        """Compares self to other and returns whether they are equal"""
        if not isinstance(other, Unit):
            return False
        if list(sorted(self.base_units.items())) != list(sorted(other.base_units.items())):
            return False
        if self.op != other.op:
            return False
        return True

    def __ne__(self, other):
        """Compares self to other and returns whether they are unequal"""
        return not self.__eq__(other)

    def __truediv__(self, other):
        """Calculates a derived unit by division"""
        if isinstance(other, numbers):
            return Unit("%s/%r" % (self.name, other), self.base_units, SequentialConversion(self.op, Conversion(operator.truediv, other)))
        elif isinstance(other, Unit):
            new_units = self.base_units.copy()
            for base_unit, exponent in list(other.base_units.items()):
                new_units[base_unit] = new_units.get(base_unit, 0) - exponent
                if new_units[base_unit] == 0:
                    del new_units[base_unit]
            new_op = self.op / other.op
            return Unit("%s/%s" % (self.name, other.name), new_units, new_op)
        else:
            raise NotImplementedError("Cannot calculate division of %r by %r" % (type(self), type(other)))

    def __rtruediv__(self, other):
        """Calculates a derived unit by division"""
        if isinstance(other, numbers):
            return Unit("%s/%r" % (self.name, other), self.base_units, SequentialConversion(self.op, Conversion(operator.truediv, other)))
        elif isinstance(other, Unit):
            raise TypeError("Unexpected reverse division call on %r, %r" % (self, other))
        else:
            raise NotImplementedError("Cannot calculate division of %r by %r" % (type(self), type(other)))

    def __mul__(self, other):
        """Calculates a derived unit by multiplication"""
        if isinstance(other, numbers):
            return Unit("%s*%r" % (self.name, other), self.base_units, SequentialConversion(self.op, Conversion(operator.mul, other)))
        elif isinstance(other, Unit):
            new_units = self.base_units.copy()
            for base_unit, exponent in list(other.base_units.items()):
                new_units[base_unit] = new_units.get(base_unit, 0) + exponent
                if new_units[base_unit] == 0:
                    del new_units[base_unit]
            new_op = self.op * other.op
            return Unit("%s*%s" % (self.name, other.name), new_units, new_op)
        else:
            raise NotImplementedError("Cannot calculate multiplication of %r by %r" % (type(self), type(other)))

    def __rmul__(self, other):
        """Calculates a derived unit by multiplication"""
        if isinstance(other, numbers):
            return self.__mul__(other)
        elif isinstance(other, Unit):
            raise TypeError("Unexpected reverse multiplication call on %r, %r" % (self, other))
        else:
            raise NotImplementedError("Cannot calculate multiplication of %r by %r" % (type(other), type(self)))

    def __call__(self, value):
        """Generates a Scalar from this Unit"""
        if isinstance(value, numbers):
            return Scalar(value, self)
        elif isinstance(value, Scalar):
            # convert scalar to this unit
            units_ratio = value.unit / self
            if units_ratio.base_units:
                raise ValueError("Cannot convert %s from %r to %r" % (value, value.unit, self))
            adjusted_value = units_ratio.op(value.value)
            return Scalar(adjusted_value, self)
        else:
            raise NotImplementedError("Can only generate Scalars for %r with numbers - got %r of type %r" % (self, value, type(value)))

    def __hash__(self):
        return id(self)

class BaseUnit(Unit):
    """A simply constructed Scalar Unit"""
    def __init__(self, name):
        super(BaseUnit, self).__init__(name, {self: 1}, identity)
        self.native_name = True

def scalar_operation(operation, unit_combination, reversed=False):
    """returns a method that can be used for operations on Scalars"""
    def __operation__(self, other):
        if isinstance(other, numbers):
            if unit_combination in (None, operator.mul, operator.truediv):
                return type(self)(operation(self.value, other), self.unit)
            raise ValueError("Cannot perform %s on %r and %r - RHS cannot be number" % (operation, self, other))
        elif isinstance(other, Scalar):
            units_ratio = other.unit / self.unit
            if unit_combination is Identity:
                if units_ratio.base_units:
                    raise ValueError("Cannot perform %s on %r and %r" % (operation, self, other))
                adjusted_value = units_ratio.op(other.value)
                return type(self)(operation(self.value, adjusted_value), self.unit)
            elif unit_combination is None:
                raise ValueError("Cannot perform %s on %r and %r - RHS must be number" % (operation, self, other))
            else:
                new_units = unit_combination(self.unit, other.unit)
                return type(self)(operation(self.value, other.value), new_units)
        else:
            raise ValueError("Cannot perform %s on %r and %r - RHS must be number or Scalar" % (operation, self, other))
    def __reversedoperation__(self, other):
        if isinstance(other, numbers):
            if unit_combination in (None, operator.mul, operator.truediv):
                return type(self)(operation(other, self.value), self.unit)
            raise ValueError("Cannot perform %s on %r and %r - RHS cannot be number" % (operation, self, other))
        elif isinstance(other, Scalar):
            raise ValueError("Unexpected reversed operation %s on %r and %r" % (operation, self, other))
        else:
            raise ValueError("Cannot perform %s on %r and %r - RHS must be number or Scalar" % (operation, self, other))
    if reversed:
        return __reversedoperation__
    else:
        return __operation__

def scalar_unary_operation(operation):
    """returns a method that can be used for unary operations on Scalars"""
    def __operation__(self):
        return type(self)(operation(self.value), self.unit)
    return __operation__

def scalar_conversion(target_type):
    """returns a method that converts the scalar to the target numeric type (by just returning the value)"""
    def __conversion__(self):
        return target_type(self.value)
    return __conversion__

class Scalar(object):
    """An object representing a value with units"""
    def __init__(self, value, unit):
        """Construct a scalar with the given value and units"""
        self.value = value
        self.unit = unit

    def __repr__(self):
        return "%s(%s, %s)" % (type(self).__name__, self.value, self.unit)

    def __str__(self):
        return "%s %s" % (self.value, self.unit.name)

    def __eq__(self, other):
        """Checks whether this has a value equivalent to that represented by other"""
        if not type(other) == type(self):
            raise NotImplementedError("Cannot compare %r with %r" % (self, other))
        units_ratio = self.unit / other.unit
        if units_ratio.base_units:
            return False
        adjusted_value = units_ratio.op(self.value)
        return adjusted_value == other.value

    def __ne__(self, other):
        """Checks whether this is a different value to other"""
        return not self.__eq__(other)

    def __cmp__(self, other):
        """Compares the two values"""
        if not type(other) == type(self):
            raise NotImplementedError("Cannot compare %r with %r" % (self, other))
        units_ratio = self.unit / other.unit
        if units_ratio.base_units:
            return False
        adjusted_value = units_ratio.op(self.value)
        return (adjusted_value > other.value) - (adjusted_value < other.value)

    def __lt__(self, other):
        return self.__cmp__(other) == -1

    def __le__(self, other):
        return self.__cmp__(other) < 1

    def __ge__(self, other):
        return self.__cmp__(other) > -1

    def __gt__(self, other):
        return self.__cmp__(other) == 1

    __add__ = scalar_operation(operator.add, Identity)
    __radd__ = scalar_operation(operator.add, Identity, reversed=True)
    __sub__ = scalar_operation(operator.sub, Identity)
    __rsub__ = scalar_operation(operator.sub, Identity, reversed=True)
    __mul__ = scalar_operation(operator.mul, operator.mul)
    __rmul__ = scalar_operation(operator.mul, operator.mul, reversed=True)
    # __floordiv__ not defined
    # __rfloordiv__ not defined
    # __div__ not defined - we only support true division
    # __rdiv__ not defined - we only support true division
    __truediv__ = scalar_operation(operator.truediv, operator.truediv)
    __rtruediv__ = scalar_operation(operator.truediv, operator.truediv, reversed=True)
    # __mod__ not defined
    # __rmod__ not defined
    # __divmod__ not defined
    # __rdivmod__ not defined
    __pow__ = scalar_operation(operator.pow, None)
    # __rpow__ not defined
    # __lshift__ not defined
    # __rlshift__ not defined
    # __rshift__ not defined
    # __rrshift__ not defined
    # __and__ not defined
    # __rand__ not defined
    # __xor__ not defined
    # __rxor__ not defined
    # __or__ not defined
    # __ror__ not defined

    # unary operations on the values
    __neg__ = scalar_unary_operation(operator.neg)
    __pos__ = scalar_unary_operation(operator.pos)
    __abs__ = scalar_unary_operation(operator.abs)
    # __invert__ not defined

    # conversions back to values
    # These conversions are of debatable value, but are included at the moment
    __complex__ = scalar_conversion(complex)
    __int__ = scalar_conversion(int)
    if sys.version_info.major < 3:
        __long__ = scalar_conversion(long)
    __float__ = scalar_conversion(float)

    # __oct__ not defined
    # __hex__ not defined
    # __index__ not defined
    # __coerce__ not defined

