import math
import warnings
from numbers import Real
from typing import Union, Tuple

# todo create offset class to handle C to K or C to F
# todo decide whether to automatically reduce the units
# todo create __format__ to control return
si_prefixes = {  # dictionary of SI prefixes and their power
    'Y': 24,  # yotta
    'Z': 21,  # zetta
    'E': 18,  # exa
    'P': 15,  # peta
    'T': 12,  # tera
    'G': 9,  # giga
    'M': 6,  # mega
    'k': 3,  # kilo
    'h': 2,  # hecto
    'da': 1,  # deka
    '': 0,  # no prefix
    'd': -1,  # deci
    'c': -2,  # centi
    'm': -3,  # milli
    'u': -6,  # micro
    'n': -9,  # nano
    'p': -12,  # pico
    'f': -15,  # femto
    'a': -18,  # ato
    'z': -21,  # zepto
    'y': -24,  # yocto
}

# SI prefix conflicts
# todo figure out how to generate this from sets
# _conflicts = set(si_prefixes) & set(dir(unithandler.siunits))
_conflicts = {
    'P': ['Pa'],
    'T': ['T'],
    'k': ['kat', 'katal', 'kelvin', 'kg', 'kilogram'],
    'h': ['henry', 'hertz'],
    'c': ['candela', 'cd', 'coulomb'],
    'm': ['meter', 'mol', 'mole', 'min'],
    'n': ['newton'],
    'p': ['pascal'],
    'f': ['farad'],
    'a': ['ampere'],
}

unicode_superscripts = {  # superscript values for unit representations
    0: f'\u2070',
    1: f'\u00b9',
    2: f'\u00b2',
    3: f'\u00b3',
    4: f'\u2074',
    5: f'\u2075',
    6: f'\u2076',
    7: f'\u2077',
    8: f'\u2078',
    9: f'\u2079',
}
minus = f'\u207b'  # superscript minus sign
dot = f'\u00b7'  # dot symbol
unsub = str.maketrans(  # translation dictionary for removing superscripts
    "".join(unicode_superscripts[val] for val in sorted(unicode_superscripts.keys())),
    "0123456789"
)


def scale_value_by_prefix(
        value: Union[float, 'UnitFloat'],
        target_prefix: str,
        current_prefix: str = '',
) -> float:
    """
    Converts a value to a different SI prefix.

    :param float value: value to convert
    :param str target_prefix: target prefix to convert to
    :param str current_prefix: current prefix of the value
    :return: scaled value
    :rtype: float
    """
    if isinstance(value, UnitFloat):  # retrieves current prefix from instance
        current_prefix = value.prefix
        value = float(value.real)
    if target_prefix not in si_prefixes:
        raise KeyError(f'The specified target prefix "{target_prefix}" is not valid. Choose from '
                       f'{", ".join(x for x in si_prefixes)}')
    if current_prefix not in si_prefixes:
        raise KeyError(f'The current prefix "{target_prefix}" is not valid. Choose from '
                       f'{", ".join(x for x in si_prefixes)}')
    if current_prefix == target_prefix:  # catch for no change
        return float(value)
    return float(
        value
        * 10 ** (
            si_prefixes[current_prefix]   # convert to no prefix
            - si_prefixes[target_prefix]  # scale to target prefix
        )
    )


def prefix_from_power(power: int) -> str:
    """
    Returns the SI prefix associated with the provided power.

    :param int power: power
    :return: SI prefix
    :rtype: str
    """
    if power not in si_prefixes.values():
        raise ValueError(f'The power {power} is not in the SI prefixes dictionary')
    for prefix, p in si_prefixes.items():
        if power == p:
            return prefix


class UnitError(Exception):
    def __init__(self, msg):
        """
        An exception raised on unit discrepancies or mismatches

        :param msg: message to supply
        """
        super(UnitError, self).__init__(msg)


def interpret_unit_block(unitblock: str) -> dict:
    """
    Interprets a unit and breaks it into `unit: power` associations.

    :param unitblock: unit to interpret
    :return: dictionary of unit: power associations
    :rtype: dict
    """
    unitblock = unitblock.translate(unsub)
    unit = ''
    num = ''
    sign = 1
    if unitblock.startswith('/'):  # if a forward slash (special case for "per")
        sign = -1
        unitblock = unitblock[1:]
    for char in unitblock:  # for each character
        if char.isdigit():  # if a digit, increase counter
            num += char
        elif char == '-' or char == minus:  # if a negative sign, change sign
            sign = -1
        elif char in [' ', dot]:  # if a separator, ignore
            pass
        else:  # otherwise add to unit
            unit += char

    if num == '':  # if no number was found, assume 1
        num = sign
    else:  # convert to integer and multiply by sign
        num = int(num) * sign
    return {unit: num}


def chewunit(unit: str) -> Tuple[str, dict]:
    """
    Iterates through the provided unit, extracting and interpreting the blocks, then returning the unit minus the block.

    :param str unit: unit to be interpreted
    :return: remaining unit minus the block, interpreted block
    """
    block = ''  # unit block
    for i, char in enumerate(unit):
        # if an alpha has been reached and the previous was a digit
        if char.isalpha() and i != 0 and unit[i-1].isdigit():
            break
        elif char == '/' and len(block) > 0:  # special "per" case
            break
        elif char == dot and len(block) > 0:  # use dot as a break
            break
        elif char == ' ' and len(block) > 0:  # use space as a break
            break
        else:  # extend unit block
            block += char
    return unit[len(block):], interpret_unit_block(block)  # return remaining formula and the interpreted block


def interpret_unit(unit: str) -> dict:
    """
    Interprets a unit, converting it into unit: power associations

    :param unit: unit to interpret
    :return: unit dictionary
    :rtype: dict
    """
    units = {}
    while len(unit) > 0:  # chew through unit
        unit, interpreted = chewunit(unit)
        units = adjust_unit(  # adjust the units dictionary
            units,
            interpreted,
        )
    return units


def adjust_unit(original: dict, incoming: dict) -> dict:
    """
    Adjusts the original unit dictionary with the incoming dictionary

    :param dict original: original dictionary
    :param dict incoming: adjusting dictionary
    :return: adjusted dictionary
    :rtype: dict
    """
    out = dict(original)
    for unit in incoming:
        if unit in out:
            new = out[unit] + incoming[unit]
            if new == 0:  # if the new value will be zero, remove unit
                del out[unit]
            else:
                out[unit] = new
        else:
            out[unit] = incoming[unit]
    return out


si_derived_units = {  # derived SI units and their equivalency in base units
    'Hz': interpret_unit('s-1'),  # hertz
    'N': interpret_unit('m·kg·s-2'),  # newton
    'Pa': interpret_unit('m-1·kg·s-2'),  # pascal
    'J': interpret_unit('m2·kg·s-2'),  # joule
    'W': interpret_unit('m2·kg·s-3'),  # watt
    'C': interpret_unit('s·A'),  # coulomb
    'V': interpret_unit('m2·kg·s-3·A-1'),  # volt
    'F': interpret_unit('m-2·kg-1·s4·A2'),  # farad
    f'\u2126': interpret_unit('m2·kg·s-3·A-2'),  # ohm
    'S': interpret_unit('m-2·kg-1·s3·A2'),  # siemens
    'Wb': interpret_unit('m2·kg·s-2·A-1'),  # weber
    'T': interpret_unit('kg·s-2·A-1'),  # tesla
    'H': interpret_unit('m2·kg·s-2·A-2'),  # henry
    'lm': interpret_unit('cd'),  # lumen
    'lx': interpret_unit('m-2·cd'),  # lux
    'kat': interpret_unit('s-1·mol'),  # katal
}


def reduce_units(units: dict) -> dict:
    """
    Checks for unit equivalency in SI derived units and returns the converted units dictionary.

    :param dict units: dictionary of units
    :return: converted dictionary
    :rtype: dict
    """
    if isinstance(units, Unit):  # if a Unit instance, extract units
        units = dict(units.units)
    # while any([si_derived_units[der].keys() <= units.keys() for der in si_derived_units]):
    possible = []
    # todo figure out how to extract multiple derived units
    for der in sorted(  # order derived units according to highest power
            si_derived_units,
            key=lambda x: sum([abs(si_derived_units[x][val]) for val in si_derived_units[x]]),
            reverse=True
    ):
        # if the unit is contained
        if si_derived_units[der].keys() <= units.keys():
            eq = dict(si_derived_units[der])
            if all([_unit_bounded(units[key], eq[key]) for key in eq]):
                eq = {key: -eq[key] for key in eq}
                eq[der] = 1
                possible.append(adjust_unit(  # append the possible reduction
                    units,
                    eq,
                ))
            # if the inverse of the unit is contained
            elif all([_unit_bounded(units[key], eq[key]) for key in eq]):
                eq[der] = -1
                possible.append(adjust_unit(  # append the possible reduction
                    units,
                    eq,
                ))

    if len(possible) == 0:
        return units
    return min(  # return the solution with the minimum power size
        possible,
        key=lambda x: sum([abs(x[key]) for key in x])
    )


def expand_units(units: dict) -> dict:
    """
    Expands any derived SI units into their true SI unit equivalents.

    :param dict units: units dictionary
    :return: expanded units
    :rtype: dict
    """
    if isinstance(units, Unit):  # if a Unit instance, extract units
        units = dict(units.units)
    for der in units.keys() & si_derived_units.keys():  # if there are derived units
        # create the adjustment dictionary (negative of the derived dictionary times the number of units present)
        eq = {key: si_derived_units[der][key] * units[der] for key in si_derived_units[der]}
        # remove the derived unit
        eq[der] = -units[der]
        units = adjust_unit(  # adjust the unit dictionary
            units,
            eq,
        )
    return units


def to_superscript(val: int) -> str:
    """
    Returns the integer value represented as a superscript string.

    :param int val: value to represent
    :return: superscript string
    :rtype: str
    """
    return ''.join(
        [unicode_superscripts[int(val)] for val in str(abs(val))]
    )


def _unit_bounded(boundary: int, value: int) -> bool:
    """
    Checks wither the incoming value is bounded by the boundary value (between 0 and the boundary).

    :param int boundary: boundary value
    :param int value: value to check
    :rtype: bool
    """
    if value < 0 < boundary or boundary < 0 < value:  # if on opposite sides of zero
        return False
    if abs(value) > abs(boundary):  # if value is greater than the boundary
        return False
    return True


class Unit(object):
    def __init__(self,
                 unit: Union[str, dict] = '',
                 sep: str = dot,
                 ):
        """
        A class for storing and managing units. This class is structured with the intent of being subclassed to provide
        a meaningful representation of a unit to an object. The `unit` attribute provides access to an appropriately
        formatted representation of the unit, and the units are stored in dictionary format along with the power
        associated with that unit, so that the unit may be easily modified without redefinition.

        :param str or dict unit: Unit for the value.
            This may be a dictionary of units with `{unit: power, ...}` format for more complicated unit expressions.
            If a string is provided, an attempt at interpreting the unit will be made.

        :param str sep: separator for string representation

        *Examples*

        >>> uni = Unit('m')
        >>> uni.unit
        'm'

        A variety of unit conventions are supported.

        >>> uni = Unit('m/s')
        >>> uni.unit
        'm·s⁻¹'
        >>> uni = Unit('m s-1')
        >>> uni.unit
        'm·s⁻¹'

        The separator used in unit representation may be modified using the `sep` attribute.

        >>> uni.sep = '*'
        >>> uni.unit
        'm*s⁻¹'

        The unit of a `Unit` instance can be modified using multiplication or division operations. Augmented
        multiplication and division operations are also supported.

        >>> uni * 's'
        m
        >>> uni * Unit('kg')
        m·s⁻·kg
        >>> uni / 's'
        m·s⁻²

        Division and multiplication operations are supported for straightforward unit assignments. An instance of
        `UnitFloat` or `UnitInt` is returned depending on the type handed operated upon. This can be a convenient way of
        applying the same unit to several values.

        >>> vel = 10 * uni  # uni * 10 performs the same effective operation
        >>> vel
        10 m·s⁻¹
        >>> type(vel)
        <class 'unithandler.base.UnitInt'>
        >>> g = 9.8 * Unit('m/s2')
        >>> g
        9.8 m·s⁻²
        >>> type(g)
        <class 'unithandler.base.UnitFloat'>

        In/Equality comparison is supported for unit checks. The comparison supports several types: another `Unit`
        instance, `dict`, or `str`. Comparison is also available in subclasses of `Unit` using the `unit_equality`
        method. Other comparisons such as less than or greater than are invalid and therefore unsupported.

        >>> uni == {'m': 1, 's': -1}
        True
        >>> uni == 'm/s'
        True
        >>> uni == Unit('m/s')
        True

        `Unit` instances may also be queried whether they contain the specified unit(s) or the inverse of those units.

        >>> uni.contains_unit('m')
        True
        >>> uni.contains_unit('m/s2')
        False
        >>> uni.contains_inverse_unit('s')
        True

        """
        if type(unit) == dict:  # if handed a dictionary of units, store
            self.units = dict(unit)
        else:
            self.units = interpret_unit(unit)
        self.sep = sep

    def __repr__(self):
        # return f'{self.__class__.__name__}({self.units})'
        return self.__str__()

    def __str__(self):
        return self.unit

    def __contains__(self, item):
        """checks for the unit in the instance"""
        return self.contains_unit(item)

    @property
    def unit(self) -> str:
        """string representation of the unit"""
        return f'{self.sep}'.join(
            f'{unit}'  # unit
            f'{minus if self.units[unit] < 0 else ""}'  # negative sign if negative power
            f'{to_superscript(self.units[unit]) if self.units[unit] != 1 else ""}'
            for unit in self.units  # for each unit that is defined
        )

    @unit.setter
    def unit(self, newunit):
        if newunit is None:
            del self.unit
            return
        self.units = interpret_unit(newunit)

    @unit.deleter
    def unit(self):
        self.units = {}

    def inverse(self) -> dict:
        """Returns the inverse of the units"""
        return {unit: -self.units[unit] for unit in self.units}

    def _divide_units(self, units: dict):
        """
        Divides the units stored in the instance by the provided units.

        :param dict, Unit units: incoming units
        """
        if isinstance(units, Unit):
            units = units.units
        self.units = adjust_unit(
            self.units,
            {unit: -units[unit] for unit in units},  # inverted units
        )

    def _multiply_units(self, units: dict):
        """
        Multiplies the units stored in the instance by the provided units.

        :param dict, Unit units: incoming units
        """
        if isinstance(units, Unit):
            units = units.units
        self.units = adjust_unit(
            self.units,
            units,
        )

    def unit_equality(self, other: Union['Unit', dict, str]) -> bool:
        """
        Compares the units stored in the instance to the value provided.

        :param str, dict, Unit other: other units
        :return: whether the supplied units are identical to the stored units
        :rtype: bool
        """
        if isinstance(other, Unit):  # another unit instance
            return self.units == other.units
        elif type(other) == dict:  # a units dictionary
            return self.units == other
        elif type(other) == str:  # a unit string
            return self.units == interpret_unit(other)
        return False  # otherwas unequal

    def contains_unit(self, other) -> bool:
        """
        Checks whether the units in the instance contain the specified unit.

        :param str, dict, Unit other: other units
        :return: whether the other unit is conatined in the instance
        :rtype: bool
        """
        if isinstance(other, Unit):
            other = other.units
        elif type(other) == dict:
            pass
        elif type(other) == str:
            other = interpret_unit(other)
        else:
            raise TypeError(f'The unit type {type(other)} could not be compared to the instance. ')
        # perform comparison for all provided units
        return all([_unit_bounded(self.units[key], other[key]) for key in other])

    def contains_inverse_unit(self, other) -> bool:
        """
        Checks whether the units in the instance contain the inverse of the specified unit.

        :param str, dict, Unit other: other units
        :return: whether the other unit is conatined in the instance
        :rtype: bool
        """
        if isinstance(other, Unit):
            other = other.units
        elif type(other) == dict:
            pass
        elif type(other) == str:
            other = interpret_unit(other)
        else:
            raise TypeError(f'The unit type {type(other)} could not be compared to the instance. ')
        # perform comparison for all provided units
        return all([_unit_bounded(self.units[key], -other[key]) for key in other])

    def __neg__(self) -> 'Unit':
        """Negative of the instance"""
        return Unit(
            self.inverse(),
            self.sep,
        )

    def __eq__(self, other: Union[str, dict, 'Unit']):
        """equality test"""
        return self.unit_equality(other)

    def __ne__(self, other: Union[str, dict, 'Unit']):
        """inequality test"""
        return not self.unit_equality(other)

    def __mul__(self, other: Union[str, dict, 'Unit', float, int]) -> Union['Unit', 'UnitFloat', 'UnitInt']:
        """multiplication support"""
        if isinstance(other, Unit):
            other = other.units
        elif type(other) == str:  # interpret as a unit
            other = interpret_unit(other)
        elif type(other) == dict:  # assume dictionary of units
            pass
        elif isinstance(other, (float, int)):  # support operation of values (attaches a unit to a value)
            if isinstance(other, float):
                return UnitFloat(
                    other,
                    self.units,
                )
            if isinstance(other, int):
                return UnitInt(
                    other,
                    self.units
                )
        else:
            raise TypeError(f'unsupported operand type for {self.__class__.__name__}: {type(other)}')
        return Unit(
            adjust_unit(
                self.units,
                other,
            ),
            self.sep,
        )

    def __rmul__(self, other: Union[str, dict, 'Unit', float, int]) -> Union['Unit', 'UnitFloat', 'UnitInt']:
        """reverse multiplication"""
        return self.__mul__(other)

    def __imul__(self, other: Union[str, dict, 'Unit', float, int]) -> Union['Unit', 'UnitFloat', 'UnitInt']:
        """augmented multiplication"""
        if isinstance(other, Unit):
            other = other.units
        elif type(other) == str:
            other = interpret_unit(other)
        elif isinstance(other, (float, int)):  # support operation of values (attaches a unit to a value)
            return self.__mul__(other)  # regular multiplication applies
        else:
            raise TypeError(f'unsupported operand type for {self.__class__.__name__}: {type(other)}')
        self._multiply_units(other)
        return self

    def __truediv__(self, other: Union[str, dict, 'Unit', float, int]) -> Union['Unit', 'UnitFloat', 'UnitInt']:
        """division"""
        if isinstance(other, Unit):
            other = other.units
        elif type(other) == str:
            other = interpret_unit(other)
        elif isinstance(other, (float, int)):  # support operation of values (attaches a unit to a value)
            return self.__mul__(1./other)  # invert value and return multiple
        else:
            raise TypeError(f'unsupported operand type for {self.__class__.__name__}: {type(other)}')
        return Unit(
            adjust_unit(
                self.units,
                {unit: -other[unit] for unit in other},  # inverted units
            ),
            self.sep
        )

    def __rtruediv__(self, other: Union[str, dict, 'Unit', float, int]) -> Union['Unit', 'UnitFloat', 'UnitInt']:
        """reverse division"""
        if isinstance(other, Unit):
            other = other.units
        elif type(other) == str:
            other = interpret_unit(other)
        elif isinstance(other, (float, int)):  # support operation of values (attaches a unit to a value)
            if isinstance(other, float):
                return UnitFloat(
                    other,
                    self.inverse(),  # invert units
                )
            if isinstance(other, int):
                return UnitInt(
                    other,
                    self.inverse(),  # invert units
                )
        else:
            raise TypeError(f'unsupported operand type for {self.__class__.__name__}: {type(other)}')
        return Unit(
            adjust_unit(
                other,
                self.inverse(),
            ),
            self.sep
        )

    def __itruediv__(self, other: Union[str, dict, 'Unit', float, int]) -> Union['Unit', 'UnitFloat', 'UnitInt']:
        """augmented division"""
        if isinstance(other, Unit):
            other = other.units
        elif type(other) == str:
            other = interpret_unit(other)
        elif isinstance(other, (float, int)):  # support operation of values (attaches a unit to a value)
            if isinstance(other, float):
                return UnitFloat(
                    other,
                    self.inverse(),  # invert units
                )
            if isinstance(other, int):
                return UnitInt(
                    other,
                    self.inverse(),  # invert units
                )
        else:
            raise TypeError(f'unsupported operand type for {self.__class__.__name__}: {type(other)}')
        self._divide_units(other)
        return self

    def __idiv__(self, other: Union[str, dict, 'Unit', float, int]) -> Union['Unit', 'UnitFloat', 'UnitInt']:
        return self.__itruediv__(other)

    def __pow__(self, power: int, modulo=None) -> 'Unit':
        if type(power) != int:
            raise TypeError(f'Only integer powers are supported')
        return Unit(
            {unit: self.units[unit] * power for unit in self.units},
            self.sep
        )

    def __ipow__(self, power: int) -> 'Unit':
        if type(power) != int:
            raise TypeError(f'Only integer powers are supported')
        self.units = {unit: self.units[unit] * power for unit in self.units}
        return self

    def __getinitargs__(self):
        """initialization arguments"""
        return (
            self.units,
            self.sep,
        )

    def __reduce__(self):
        """pickle support"""
        return (
            Unit,
            self.__getinitargs__(),
        )


class UnitInt(Real, Unit):
    def __init__(self,
                 value: Union[int, float, str, 'UnitFloat', 'UnitInt'],
                 unit: Union[str, dict, Unit] = '',
                 sep: str = dot,
                 ):
        """
        An `int` mimic with a unit attribute.

        :param value: value to store
        :param str or dict unit: Unit for the value.
            This may be a dictionary of units with `{unit: power, ...}` format for more complicated unit expressions.
            If a string is provided, an attempt at interpreting the unit will be made.

        **Supported operations**

        - All normal, reversed, and augmented numeric Python operations (`*`, `/`, `+`, `-`, `**`, `//`, `%`,
          `*=`, `/=`, `+=`, `-=`, `**=`).
        - Bitwise operations
        - Comparison to numeric values (or other `Unit` subclasses)
        - Unary operations (`neg`, `pos`, `abs`, `round`, etc.)
        - `pickle` package
        - `copy` package
        - `math` package

        **Behaviour of numeric operations**

        All numeric Python operators are supported in normal, reversed, and augmented form. Comparisons to values, as
        well as bitwise operations are also supported.

        If the other value is *not* a `Unit` subclass:

        - For addition and subtraction, it will be assumed to have the same unit as the `UnitInt` value.
        - For multiplication and division, the other value will be interpreted as a scalar.

        If the other value is a `Unit` subclass:

        - For addition and subtraction, the units of the other value will be compared, and if they are unequal, a
          `UnitError` will be raised.
        - For multiplication and division, the units of the first value will be modified accordingly. If multiplied,
          the powers will be increased by the other unit's powers. If divided, the powers will be decreased by the other
          unit's power.

        **Examples**

        >>> distance = UnitInt(50, 'm')
        >>> distance
        50 m

        >>> new = distance + 50
        100 m
        >>> type(new)  # the new value is a new UnitInt instance
        <class 'unithandler.base.UnitInt'>

        Reversed operations will automatically return a `UnitInt` instance.

        >>> 50 + distance
        100 m
        >>> distance - 25
        25 m
        >>> 25 - distance
        -25 m
        >>> distance + UnitInt(50, 'm/s')  # mismatched units
        UnitError: The units of the two UnitInt instances are mismatched: m != m·s⁻¹

        Operations that result in non-integer values will automatically convert to UnitFloat

        >>> new = distance + 50.5
        >>> type(new)
        <class 'unithandler.base.UnitFloat'>

        >>> distance * 2
        100 m
        >>> distance / 2
        25 m
        >>> 100 / distance
        2 m⁻¹
        >>> 2 * distance
        100 m
        >>> distance * UnitInt(2, 'm')  # multiplication by another Unit subclass
        100 m²
        >>> distance / UnitInt(25, 's')  # division by another Unit subclass
        2 m·s⁻¹
        """
        if type(value) == str:  # if handed a string representation of a value
            try:  # split into value and unit
                value, unit = value.split(' ')
            except ValueError:  # unless only a value was specified
                pass
            try:
                float(value)
            except ValueError:
                raise ValueError(f'The string "{value}" could not be interpreted as a UnitInt value. ')
        Unit.__init__(self, unit, sep)  # initialize Unit
        self._real = int(value)

    @property
    def real(self) -> int:
        return self._real

    @real.setter
    def real(self, value):
        if type(value) != int:
            raise TypeError(f'A UnitInt value must be of type integer, provided: {type(value)}.')
        self._real = value

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """Support for numpy ufuncs"""
        warnings.warn('Numpy ufunc support is largely untested. Use this with care. ')
        if method == '__call__':
            return ufunc(
                *[float(val) for val in inputs],
                **kwargs
            )
        # todo work out what other ufunc operations would be relevant here
        raise NotImplementedError(f'The ufunc {ufunc} with method {method} is not currently supported. ')

    def __repr__(self):
        # return f'{self.__class__.__name__}({self.real}, {self.unit})'
        return self.__str__()

    def __str__(self):
        return f'{self.real} {self.unit}'

    def __float__(self):
        return float(self.real)

    def __int__(self):
        return int(self.real)

    # addition methods
    def __add__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> Union['UnitFloat', 'UnitInt']:
        """addition"""
        if isinstance(other, (UnitFloat, UnitInt)):  # if incoming is another UnitValue, scale incoming value to current
            if self.unit_equality(other) is False:
                raise UnitError(f'The units of the two {self.__class__.__name__} instances are mismatched: '
                                f'{self.unit} != {other.unit}')
            other = other.real
        newval = self.real + other
        if type(newval) == int or newval.is_integer():  # if the result is an integer, return an integer
            return UnitInt(
                newval,
                self.units,
            )
        else:  # otherwise return a float
            return UnitFloat(
                newval,
                self.units,
            )

    def __radd__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> Union['UnitFloat', 'UnitInt']:
        """reversed addition"""
        return self.__add__(other)

    def __iadd__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> Union['UnitFloat', 'UnitInt']:
        """augmented addition"""
        if isinstance(other, (UnitFloat, UnitInt)):  # if incoming is another UnitValue, scale incoming value to current
            if other.units != self.units:
                raise UnitError(f'The units of the two {self.__class__.__name__} instances are mismatched: '
                                f'{self.unit} != {other.unit}')
            other = other.real
        newval = self.real + other
        if type(newval) == int or newval.is_integer():  # if the result is an integer, return an integer
            self.real = newval
            return self
        else:  # otherwise return a float
            return UnitFloat(
                newval,
                self.units,
            )

    # subtraction methods
    def __sub__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> Union['UnitFloat', 'UnitInt']:
        """subtraction"""
        if isinstance(other, (UnitFloat, UnitInt)):  # if incoming is another UnitValue, scale incoming value to current
            if self.unit_equality(other) is False:
                raise UnitError(f'The units of the two {self.__class__.__name__} instances are mismatched: '
                                f'{self.unit} != {other.unit}')
            other = other.real
        newval = self.real - other
        if type(newval) == int or newval.is_integer():  # if the result is an integer, return an integer
            return UnitInt(
                newval,
                self.units,
            )
        else:  # otherwise return a float
            return UnitFloat(
                newval,
                self.units,
            )

    def __rsub__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> Union['UnitFloat', 'UnitInt']:
        """reverse subtraction"""
        if isinstance(other, (UnitFloat, UnitInt)):  # if incoming is another UnitValue, scale incoming value to current
            if self.unit_equality(other) is False:
                raise UnitError(f'The units of the two {self.__class__.__name__} instances are mismatched: '
                                f'{self.unit} != {other.unit}')
            other = other.real
        newval = other - self.real
        if type(newval) == int or newval.is_integer():  # if the result is an integer, return an integer
            return UnitInt(
                newval,
                self.units,
            )
        else:  # otherwise return a float
            return UnitFloat(
                newval,
                self.units,
            )

    def __isub__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> Union['UnitFloat', 'UnitInt']:
        """augmented subtraction"""
        return self.__iadd__(-other)

    # multiplication methods
    def __mul__(self, other: Union['Unit', 'UnitFloat', 'UnitInt', float, int, str]) -> Union['UnitFloat', 'UnitInt']:
        """multiplication"""
        if isinstance(other, (UnitFloat, UnitInt)):
            newunits = adjust_unit(
                self.units,
                other.units,
            )
            other = other.real
        elif isinstance(other, Unit):
            newunits = adjust_unit(
                self.units,
                other.units,
            )
            other = 1.
        elif type(other) is str:  # assume string is a new unit
            newunits = adjust_unit(self.units, interpret_unit(other))  # determine new units
            other = 1.
        else:
            newunits = self.units
        newval = self.real * other
        if type(newval) == int or newval.is_integer():
            return UnitInt(
                newval,
                newunits,
            )
        else:
            return UnitFloat(
                newval,
                newunits,
            )

    def __rmul__(self, other: Union['Unit', 'UnitFloat', 'UnitInt', float, int, str]) -> Union['UnitFloat', 'UnitInt']:
        """reversed multiplication"""
        return self.__mul__(other)

    def __imul__(self, other: Union['Unit', 'UnitFloat', 'UnitInt', float, int, str]) -> Union['UnitFloat', 'UnitInt']:
        """augmented multiplication"""
        if isinstance(other, (UnitFloat, UnitInt)):
            newunits = adjust_unit(
                self.units,
                other.units
            )
            other = other.real
        elif isinstance(other, Unit):
            newunits = adjust_unit(
                self.units,
                other.units,
            )
            other = 1.
        elif type(other) is str:  # assume string is a new unit
            newunits = adjust_unit(self.units, interpret_unit(other))  # determine new units
            other = 1.
        else:
            newunits = self.units
        newval = self.real * other
        if type(newval) == int or newval.is_integer():
            self.real = newval
            self.units = newunits
            return self
        else:
            return UnitFloat(
                newval,
                newunits,
            )

    # division methods
    def __truediv__(self, other: Union['Unit', 'UnitFloat', 'UnitInt', float, int, str]) -> Union['UnitFloat', 'UnitInt']:
        """true division"""
        if isinstance(other, (UnitFloat, UnitInt)):
            newunits = adjust_unit(
                self.units,
                other.inverse(),
            )
            other = other.real
        elif isinstance(other, Unit):
            newunits = adjust_unit(
                self.units,
                other.inverse()
            )
            other = 1.
        elif type(other) == str:
            incomingunit = interpret_unit(other)
            newunits = adjust_unit(
                self.units,
                {unit: -incomingunit[unit] for unit in incomingunit}
            )
            other = 1.
        else:
            newunits = self.units
        newval = self.real / other
        if type(newval) == int or newval.is_integer():
            return UnitInt(
                newval,
                newunits
            )
        else:
            return UnitFloat(
                newval,
                newunits,
            )

    def __rtruediv__(self, other: Union['Unit', 'UnitFloat', 'UnitInt', float, int, str]) -> Union['UnitFloat', 'UnitInt']:
        """reversed true division"""
        if isinstance(other, Unit):
            newunits = adjust_unit(
                other.units,
                self.units,
            )
            other = 1
        elif type(other) == str:
            newunits = adjust_unit(
                interpret_unit(other),
                self.inverse(),
            )
            other = 1.
        else:
            newunits = self.inverse()
        newval = other / self.real
        if type(newval) == int or newval.is_integer():
            return UnitInt(
                newval,
                newunits
            )
        else:
            return UnitFloat(
                newval,
                newunits,
            )

    def __rdiv__(self, other: Union['Unit', 'UnitFloat', 'UnitInt', float, int, str]) -> Union['UnitFloat', 'UnitInt']:
        """reversed division"""
        return self.__rtruediv__(other)

    def __itruediv__(self, other: Union['Unit', 'UnitFloat', 'UnitInt', float, int, str]) -> 'UnitFloat':
        """augmented division"""
        if isinstance(other, (UnitFloat, UnitInt)):
            newunits = adjust_unit(
                self.units,
                other.inverse(),
            )
            other = other.real
        elif isinstance(other, Unit):
            newunits = adjust_unit(
                self.units,
                other.inverse()
            )
            other = 1.
        elif type(other) == str:
            incomingunit = interpret_unit(other)
            newunits = adjust_unit(
                self.units,
                {unit: -incomingunit[unit] for unit in incomingunit}
            )
            other = 1.
        else:
            newunits = self.units
        newval = self.real / other
        if type(newval) == int or newval.is_integer():
            self.real = newval
            self.units = newunits
            return self
        else:
            return UnitFloat(
                newval,
                newunits,
            )

    # div/mod
    def __floordiv__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> int:
        """integer division"""
        if isinstance(other, (UnitFloat, UnitInt)):
            other = other.real
        return int(self.real // other)

    def __rfloordiv__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> int:
        return int(other // self.real)

    def __mod__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> Union['UnitFloat', 'UnitInt']:
        if isinstance(other, (UnitFloat, UnitInt)):
            other = other.real
        newval = self.real % other
        if type(newval) == int or newval.is_integer():
            return UnitInt(
                newval,
                self.units
            )
        else:
            return UnitFloat(
                newval,
                self.units,
            )

    def __rmod__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> int:
        return other % self.real

    def __divmod__(self, other):
        return (
            self.__floordiv__(other),
            self.__mod__(other),
        )

    # power
    def __pow__(self, power: int, modulo=None) -> 'UnitInt':
        """raising to a power"""
        return UnitInt(
            self.real ** power,
            {unit: self.units[unit] * power for unit in self.units},
        )

    def __rpow__(self, other):
        """reverse power raising (not supported/nonsensical)"""
        return NotImplemented

    def __ipow__(self, power: int) -> 'UnitInt':
        """augmented raising to a power (**=)"""
        self.units = {unit: self.units[unit] * power for unit in self.units}
        self.real = self.real ** power
        return self

    # bitwise modifications
    def __lshift__(self, other):
        return self.real << other

    def __rshift__(self, other):
        return self.real >> other

    def __and__(self, other):
        return self.real & other

    def __or__(self, other):
        return self.real | other

    def __xor__(self, other):
        return self.real ^ other

    def __rlshift__(self, other):
        return other << self.real

    def __rrshift__(self, other):
        return other >> self.real

    def __rand__(self, other):
        return other & self.real

    def __ror__(self, other):
        return other | self.real

    def __rxor__(self, other):
        return other ^ self.real

    # comparisons
    def __gt__(self, other):  # greater than
        if isinstance(other, (UnitFloat, UnitInt)):
            other = other.real
        return self.real > other

    def __lt__(self, other):  # less than
        if isinstance(other, (UnitFloat, UnitInt)):
            other = other.real
        return self.real < other

    def __eq__(self, other):  # equal to
        if isinstance(other, (UnitFloat, UnitInt)):
            other = other.real
        return self.real == other

    def __le__(self, other):  # less or equal to
        if isinstance(other, (UnitFloat, UnitInt)):
            other = other.real
        return self.real <= other

    def __ge__(self, other):  # greater or equal to
        if isinstance(other, (UnitFloat, UnitInt)):
            other = other.real
        return self.real >= other

    def __ne__(self, other):  # not equal to
        if isinstance(other, (UnitFloat, UnitInt)):
            other = other.real
        return self.real != other

    # unary operations/functions
    def __neg__(self) -> 'UnitInt':
        return UnitInt(
            -self.real,
            self.units,
        )

    def __pos__(self) -> 'UnitInt':
        return UnitInt(
            self.real,
            self.units,
        )

    def __abs__(self) -> 'UnitInt':
        return UnitInt(
            abs(self.real),
            self.units,
        )

    def __invert__(self):
        return ~ self.real

    def __round__(self, n=None):
        return round(self.real, n)

    def __floor__(self):
        return self.real.__floor__()

    def __ceil__(self):
        return self.real.__ceil__()

    def __trunc__(self):
        return self.real.__trunc__()

    def __copy__(self) -> 'UnitInt':
        return UnitInt(
            self.real,
            self.units,
        )

    def __deepcopy__(self, memodict={}) -> 'UnitInt':
        return UnitInt(
            self.real,
            self.units
        )

    def __index__(self):
        return self.real.__index__()

    def __hex__(self):
        return hex(self.real)

    def __oct__(self):
        return oct(self.real)

    def __getinitargs__(self):
        """init arguments"""
        return (
            self.real,
            self.units,
        )

    def __reduce__(self):
        """pickle support"""
        return (
            UnitInt,
            self.__getinitargs__(),
        )

    def as_constant(self) -> 'Constant':
        """Returns the value as a Constant instance"""
        return Constant(
            self.real,
            self.units,
        )


class UnitFloat(Unit, Real):
    # class level flag to control auto-scaling of values
    scale_representation = True

    def __init__(self,
                 value: Union[float, int, str, 'UnitFloat', 'UnitInt'],
                 unit: Union[str, dict, Unit] = '',
                 si_prefix: str = '',
                 stored_prefix: str = '',
                 uncertainty: float = None,
                 scale_representation: bool = None,
                 ):
        """
        A float mimic that stores a value, it's unit, and allows specification of both the incoming and stored SI
        prefix. When a string or representation of this class is called, the optimal representation of the value is
        returned. This true stored value (e.g. when `float()` or `int()` is called on a `UnitFloat` instance is
        determined by the `prefix` attribute.

        :param value: value to store
        :param str or dict unit: Unit for the value.
            This may be a dictionary of units with `{unit: power, ...}` format for more complicated unit expressions.
            If a string is provided, an attempt at interpreting the unit will be made.

        :param si_prefix: SI prefix for the incoming value
        :param stored_prefix: preferred SI prefix for stored value. The stored value will be scaled to reflect this
            prefix.
        :param float uncertainty: Uncertainty in the float value (this will be interpreted as a +/- value with the same
            prefix as the incoming value).
        :param bool scale_representation: Whether to scale the representation of the value. Set this to False to
            disable value scaling.

        **Supported operations**

        - All normal, reversed, and augmented numeric Python operations (`*`, `/`, `+`, `-`, `**`, `//`, `%`,
          `*=`, `/=`, `+=`, `-=`, `**=`).
        - Comparison to numeric values (or other `Unit` subclasses)
        - Unary operations (`neg`, `pos`, `abs`, `round`, etc.)
        - `pickle` package
        - `copy` package
        - `math` package

        **Behaviour of numeric operations**

        All numeric Python operators are supported in normal, reversed, and augmented form. Comparisons to values, as
        well as bitwise operations are also supported.

        If the other value is *not* a `Unit` subclass:

        - For addition and subtraction, it will be assumed to have the same unit as the `UnitFloat` value.
        - For multiplication and division, the other value will be interpreted as a scalar. It will be assumed that the
          other value has the same prefix scalar as the `UnitFloat` value. This may lead to unintended scaling of the
          resulting value, and can be controlled by creating two `UnitFloat` instances prior to operation, or by
          performing the operation on two `float` values, then converting to `UnitFloat`.

        If the other value is a `Unit` subclass:

        - For addition and subtraction, the units of the other value will be compared, and if they are unequal, a
          `UnitError` will be raised.
        - For multiplication and division, the units of the first value will be modified accordingly. If multiplied,
          the powers will be increased by the other unit's powers. If divided, the powers will be decreased by the other
          unit's power.

        **Examples**

        >>> val = UnitFloat(0.2, 'L')
        >>> val  # the optimal representation of this will be automatically determined
        200 mL
        >>> float(val)  # but the true value will reflect the prefix of the UnitFloat instance
        0.2

        If the value provided on instantiation is scaled to a particular SI prefix, it may be specified during
        instantiation with the `incoming_prefix` keyword argument.

        >>> vol = 2.  # represents 2 mL
        >>> uf_vol = UnitFloat(vol, 'L', si_prefix='m')  # equivalent to UnitFloat(2., 'L', 'm')
        >>> uf_vol
        2 mL
        >>> float(uf_vol)  # the value has been scaled to have no SI prefix by default
        0.002

        The desired prefix for the stored value of the `UnitFloat` instance may be set during instantiation using the
        `stored_prefix` keyword  argument, or modified after instantiation by changing the `prefix` attribute.
        The prefix may be changed to any SI prefix, and will scale the stored float value, but not affect the
        representation. The stored value scaled to a specific prefix may be conveniently accessed using the
        `specific_prefix` method.

        >>> uf_vol.prefix
        ''
        # this is equivalent to calling UnitFloat(vol, 'L', 'm', stored_prefix='m') or UnitFloat(vol, 'L', 'm', 'm')
        >>> uf_vol.prefix = 'm'  # the prefix may be changed to any SI prefix
        >>> uf_vol  # the representation will remain unchanged
        2 mL
        >>> float(uf_vol)  # the stored value will be scaled
        2.0
        >>> uf_vol.specific_prefix('u')
        2000.0

        For convenience, string values with units may be provided and automatically interpreted.

        >>> from_string = UnitFloat('9.8 m/s2')
        >>> from_string
        9.8 m·s⁻²
        >>> float(from_string)
        9.8
        >>> from_string.units
        {'m': 1, 's': -2}

        Additionally, SI prefixes may be included at the beginning of the unit and will be used to automatically scale
        the value.

        >>> auto_scaled = UnitFloat(1.5, 'ug')
        >>> auto_scaled
        1.5 ug
        >>> float(auto_scaled)  # the value was automatically interpreted and stored as micro
        1.5
        >>> auto_scaled.prefix
        'u'
        >>> auto_scaled_2 = UnitFloat(250., 'ug', stored_prefix='m')  # the stored prefix may still be overridden
        >>> auto_scaled_2
        250 ug
        >>> float(auto_scaled_2)
        0.25

        Operations on `UnitFloat` instances will result in a new `UnitFloat` instance. See the *Behaviour of numeric
        operations* section above for the assumptions and prescribed behaviour in Python operations on `UnitFloat`
        instances.

        >>> newval = val + 0.4
        >>> newval
        600 mL
        >>> type(newval)
        <class 'unithandler.base.UnitFloat'>
        >>> val - 0.05
        150 mL
        >>> 0.4 + val
        600 mL
        >>> 1.0 - val
        800 mL
        >>> val * 2
        400 mL
        >>> val / 2
        100 mL
        >>> 2. * val
        400 mL
        >>> 1 / val
        5 L⁻¹

        If the other value is a `Unit` or a `UnitInt`, the units will be compared the appropriate operation will be
        performed, returning a `UnitFloat` instance.

        >>> otherval = UnitInt(1., 'L')
        >>> val + otherval
        1.2 L
        >>> val - otherval
        -800 mL
        >>> val + UnitInt(1., 'm')  # addition/subtraction are not supported for mismatched units
        UnitError: The units of the two UnitFloat instances are mismatched: L != m
        >>> val * otherval
        200 mL²
        >>> val / otherval
        200 m  # now a unitless number

        If the other value is a `UnitFloat` value, both values will be scaled to have no prefix prior to operation,
        and a `UnitFloat` with the parent's stored_prefix will be returned.

        >>> val.prefix = 'k'
        >>> float(val)
        0.0002
        >>> val2 = UnitFloat(500000, 'L', 'n', 'n')
        >>> val2
        500 uL
        >>> float(val2)
        >>> val3 = val + val2  # matches the prefixes and returns a prefixless UnitFloat
        700 uL
        >>> float(val3)
        0.2005
        >>> val4 = UnitFloat(50, 'mol', 'm', 'm') / UnitFloat(100, 'L', 'm')
        >>> val4
        500 mmol·L⁻¹
        >>> val4.prefix  # the result inherits the stored prefix of the numerator
        'm'
        >>> val5 = UnitFloat(0.5, 'mol/L', 'm', 'n') * UnitFloat(50., 'L', 'm')
        >>> val5
        25 umol
        >>> val5.prefix  # the result inherits the stored prefix of the value operated on
        'n'
        """
        if type(value) == str:  # if handed a string representation of a value
            try:  # split into value and unit
                value, unit = value.split(' ')
            except ValueError:  # unless only a value was specified
                pass
            try:
                float(value)
            except ValueError:
                raise ValueError(f'The string "{value}" could not be interpreted as a UnitFloat value. ')

        # check for specified SI prefix
        if type(unit) == str and len(unit) > 1:
            for prefix in si_prefixes:
                if prefix == '':  # pass over no prefix
                    continue
                if unit.startswith(prefix):
                    if prefix in _conflicts:  # if the "prefix" might be an SI unit
                        # todo catch/ignore kg
                        # if the proceeding character is not an alpha (i.e. this is not a prefix)
                        if unit[1].isalpha() is False:
                            break
                        if any([unit.startswith(conflict) for conflict in _conflicts[prefix]]):
                            break
                    unit = unit[len(prefix):]  # strip off prefix
                    si_prefix = prefix  # override incoming prefix
                    if stored_prefix == '':  # if not specified, set stored prefix depending on provided prefix
                        stored_prefix = prefix
                    break

        # if a Unit subclass was passed, retrieve values
        elif isinstance(value, Unit):
            # if no unit was specified, retrieve
            if unit == '':
                unit = value.units
            # if a unitfloat was passed, retrieve values if not specified
            if isinstance(value, UnitFloat):
                # if no si_prefix was specified, retrieve incoming/stored prefix
                if si_prefix == '':
                    si_prefix = value.prefix
                if stored_prefix == '':
                    stored_prefix = value.prefix
                if scale_representation is None:
                    scale_representation = value.scale_representation

        Unit.__init__(self, unit)  # initialize Unit
        self._real = scale_value_by_prefix(  # scale incoming value to match return prefix
            value,
            target_prefix=stored_prefix,
            current_prefix=si_prefix
        )
        self._uncertainty = uncertainty
        self._prefix = stored_prefix  # sets the return prefix
        if scale_representation is not None:  # override if user specifies
            self.scale_representation = scale_representation

    # redefines the behaviour of the float's real attribute
    @property
    def real(self) -> float:
        return self._real

    @real.setter
    def real(self, value):
        self._real = value

    @property
    def imag(self) -> float:
        """imaginary components are not currently supported"""
        return 0.

    @property
    def stored_unit(self) -> str:
        return f'{self.prefix}{self.unit}'

    @property
    def prefix(self) -> str:
        """the SI prefix to store the value in (scales the stored float value)"""
        return self._prefix

    @prefix.setter
    def prefix(self, newprefix):
        if newprefix == self._prefix:  # if equal to current
            return
        elif newprefix is None:  # if None, set to default
            newprefix = ''
        self.real = scale_value_by_prefix(  # scale the value
            self.real,
            newprefix,
            self._prefix
        )
        self._prefix = newprefix  # store the prefix

    @prefix.deleter
    def prefix(self):
        self.prefix = ''

    @property
    def uncertainty(self) -> float:
        """The uncertainty in the value"""
        # todo add uncertainty combination on magic method operations
        return self._uncertainty

    @uncertainty.setter
    def uncertainty(self, value):
        self._uncertainty = value

    @property
    def upper(self) -> float:
        """The upper bound of the value (incorporating uncertainty)"""
        return self.real + self.uncertainty if self.uncertainty is not None else self.real

    @property
    def lower(self) -> float:
        """The lower bound of the value (incorporating uncertainty)"""
        return self.real - self.uncertainty if self.uncertainty is not None else self.real

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """Support for numpy ufuncs"""
        warnings.warn('Numpy ufunc support is largely untested. Use this with care. ')
        if method == '__call__':
            return ufunc(
                *[float(val) for val in inputs],
                **kwargs
            )
        raise NotImplementedError(f'The ufunc {ufunc} with method {method} is not currently supported. ')

    def __repr__(self):
        # return f'{self.__class__.__name__}({self.real}, {self.unit}, {self.prefix})'
        return f'{self.optimal_representation()}'

    def __str__(self):
        return f'{self.optimal_representation()}'

    def __float__(self):
        return float(self.real)

    def __int__(self):
        return int(self.real)

    # addition methods
    def __add__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> 'UnitFloat':
        """addition"""
        if isinstance(other, (UnitFloat, UnitInt)):  # if incoming is another UnitValue, scale incoming value to current
            if self.unit_equality(other) is False:
                raise UnitError(f'The units of the two {self.__class__.__name__} instances are mismatched: '
                                f'{self.unit} != {other.unit}')
            if isinstance(other, UnitFloat):
                other = other.specific_prefix(self.prefix)  # scale to specific prefix
            elif isinstance(other, UnitInt):
                other = other.real
        return UnitFloat(
            self.real + other,
            self.units,
            si_prefix=self.prefix,
            stored_prefix=self.prefix,
            scale_representation=self.scale_representation,
        )

    def __radd__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> 'UnitFloat':
        """reverse addition"""
        return self.__add__(other)

    def __iadd__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> 'UnitFloat':
        """addition/modification (+=)"""
        if isinstance(other, (UnitFloat, UnitInt)):  # if incoming is another UnitValue, scale incoming value to current
            if self.unit_equality(other) is False:
                raise UnitError(f'The units of the two {self.__class__.__name__} instances are mismatched: '
                                f'{self.unit} != {other.unit}')
            if isinstance(other, UnitFloat):
                other = other.specific_prefix(self.prefix)  # scale to specific prefix
            elif isinstance(other, UnitInt):
                other = other.real
        self.real += other
        return self

    # subtraction methods
    def __sub__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> 'UnitFloat':
        """subtraction"""
        return self.__add__(-other)

    def __rsub__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> 'UnitFloat':
        """reversed subtraction"""
        if isinstance(other, (UnitFloat, UnitInt)):  # if incoming is another UnitValue, scale incoming value to current
            if self.unit_equality(other) is False:
                raise UnitError(f'The units of the two {self.__class__.__name__} instances are mismatched: '
                                f'{self.unit} != {other.unit}')
            if isinstance(other, UnitFloat):
                other = other.specific_prefix(self.prefix)
            elif isinstance(other, UnitInt):
                other = other.real
        return UnitFloat(
            other - self.real,
            self.units,
            si_prefix=self.prefix,
            stored_prefix=self.prefix,
            scale_representation=self.scale_representation,
        )

    def __isub__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> 'UnitFloat':
        """assignment subtraction"""
        return self.__iadd__(-other)

    # multiplication methods
    def __mul__(self, other: Union['UnitFloat', 'UnitInt', 'Unit', float, int, str]) -> 'UnitFloat':
        """multiplication"""
        if isinstance(other, (UnitFloat, UnitInt)):
            newunits = adjust_unit(  # combine units
                self.units,
                other.units,
            )
            if isinstance(other, UnitFloat):
                other = other.specific_prefix('')
            elif isinstance(other, UnitInt):
                other = other.real
        elif isinstance(other, Unit):
            newunits = adjust_unit(
                self.units,
                other.units
            )
            other = 1.
        elif type(other) is str:  # assume string is a new unit
            newunits = adjust_unit(self.units, interpret_unit(other))  # determine new units
            other = 1.
        else:
            newunits = self.units
        return UnitFloat(
            self.specific_prefix('') * other,
            newunits,
            stored_prefix=self.prefix,
            scale_representation=self.scale_representation,
        )

    def __rmul__(self, other: Union['UnitFloat', 'UnitInt', 'Unit', float, int, str]) -> 'UnitFloat':
        """reversed multiplication"""
        return self.__mul__(other)

    def __imul__(self, other: Union['UnitFloat', 'UnitInt', 'Unit', float, int, str]) -> 'UnitFloat':
        """assignment multiplication (*=)"""
        if isinstance(other, (UnitFloat, UnitInt)):
            self._multiply_units(other.units)  # combine units
            if isinstance(other, UnitFloat):
                other = other.specific_prefix(self.prefix)  # match prefixes
            elif isinstance(other, UnitInt):
                other = other.real
        elif isinstance(other, Unit):
            self._multiply_units(other.units)
            other = 1.
        elif type(other) is str:  # assume string is a new unit
            self._multiply_units(interpret_unit(other))  # determine new units
            other = 1.
        self.real *= other
        return self

    # power methods
    def __pow__(self, power: int, modulo=None) -> 'UnitFloat':
        """raising to a power"""
        return UnitFloat(
            self.real ** power,
            {unit: self.units[unit] * power for unit in self.units},
            si_prefix=self.prefix,
            stored_prefix=self.prefix,
            scale_representation=self.scale_representation,
        )

    def __rpow__(self, other):
        """reverse power raising (not supported/nonsensical)"""
        return NotImplemented

    def __ipow__(self, power: int) -> 'UnitFloat':
        """assignment raising to a power (**=)"""
        self.units = {unit: self.units[unit] * power for unit in self.units}
        self.real = self.real ** power
        return self

    # division methods
    def __truediv__(self, other: Union['UnitFloat', 'UnitInt', 'Unit', float, int, str]) -> 'UnitFloat':
        """true division"""
        if isinstance(other, (UnitFloat, UnitInt)):
            newunits = adjust_unit(
                self.units,
                other.inverse(),
            )
            if isinstance(other, UnitFloat):
                # if another UnitFloat, special case for returning a prefixless number
                other = other.specific_prefix('')
            elif isinstance(other, UnitInt):
                other = other.real
        elif isinstance(other, Unit):
            newunits = adjust_unit(
                self.units,
                other.inverse()
            )
            other = 1
        elif type(other) == str:
            incomingunit = interpret_unit(other)
            newunits = adjust_unit(
                self.units,
                {unit: -incomingunit[unit] for unit in incomingunit}
            )
            other = 1.
        else:
            newunits = self.units
        return UnitFloat(
            self.specific_prefix('') / other,
            newunits,
            stored_prefix=self.prefix,
            scale_representation=self.scale_representation,
        )

    def __rtruediv__(self, other: Union['UnitFloat', 'UnitInt', 'Unit', float, int, str]) -> 'UnitFloat':
        """
        Reversed division.
        If this case is encountered, this method assumes that the numerator (other) has *no* SI prefix. This will
        scale the value stored in the `UnitFloat` instance to have no prefix prior to division, and may result in
        unexpected behaviour for users assuming that the numerator is scaled identically to the `UnitFloat` instance.
        To control this behaviour, create a `UnitFloat` instance with the appropriate prefix prior to division.
        """
        if isinstance(other, Unit):
            newunits = adjust_unit(
                self.units,
                other.inverse()
            )
            other = 1.
        elif type(other) == str:
            newunits = adjust_unit(
                interpret_unit(other),
                self.inverse(),
            )
            other = 1.
        else:
            newunits = self.inverse()
        return UnitFloat(
            other / self.specific_prefix(''),  # bring to no prefix
            newunits,
        )

    def __rdiv__(self, other: Union['UnitFloat', 'UnitInt', 'Unit', float, int, str]) -> 'UnitFloat':
        """reversed non-true division"""
        return self.__rtruediv__(other)

    def __itruediv__(self, other: Union['UnitFloat', 'UnitInt', 'Unit', float, int, str]) -> 'UnitFloat':
        """division assignment"""
        if isinstance(other, (UnitFloat, UnitInt)):
            self._divide_units(other.inverse())  # adjust units
            if isinstance(other, UnitFloat):
                other = other.specific_prefix(self.prefix)  # match prefix
            elif isinstance(other, UnitInt):
                other = other.real
        elif isinstance(other, Unit):
            self._divide_units(other.units)
            other = 1
        elif type(other) == str:
            self._divide_units(interpret_unit(other))
            other = 1.
        self.real /= other
        self._prefix = ''  # the result is a prefixless number
        return self

    def __idiv__(self, other: Union['UnitFloat', 'UnitInt', 'Unit', float, int, str]) -> 'UnitFloat':
        return self.__itruediv__(other)

    # div/mod methods
    def __floordiv__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> int:
        """integer division"""
        if isinstance(other, UnitFloat):
            other = other.specific_prefix(self.prefix)
        elif isinstance(other, UnitInt):
            other = other.real
        return int(self.real // other)

    def __rfloordiv__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> int:
        return int(other // self.real)

    def __mod__(self, other: Union['UnitFloat', 'UnitInt', float, int]) -> 'UnitFloat':
        """modulo"""
        if isinstance(other, UnitFloat):
            other = other.specific_prefix(self.prefix)
        elif isinstance(other, UnitInt):
            other = other.real
        return UnitFloat(
            self.real % other,
            self.unit,
            si_prefix=self.prefix,
            stored_prefix=self.prefix,
            scale_representation=self.scale_representation,
        )

    def __rmod__(self, other):
        return other % self.real

    def __divmod__(self, other):
        return (
            self.__floordiv__(other),
            self.__mod__(other),
        )

    # comparison methods
    def __gt__(self, other):  # greater than
        if isinstance(other, UnitFloat):
            other = other.specific_prefix(self.prefix)
        return self.real > other

    def __lt__(self, other):  # less than
        if isinstance(other, UnitFloat):
            other = other.specific_prefix(self.prefix)
        return self.real < other

    def __eq__(self, other):  # equal to
        if isinstance(other, UnitFloat):
            other = other.specific_prefix(self.prefix)
        return self.real == other

    def __le__(self, other):  # less or equal to
        if isinstance(other, UnitFloat):
            other = other.specific_prefix(self.prefix)
        return self.real <= other

    def __ge__(self, other):  # greater or equal to
        if isinstance(other, UnitFloat):
            other = other.specific_prefix(self.prefix)
        return self.real >= other

    def __ne__(self, other):  # not equal to
        if isinstance(other, UnitFloat):
            other = other.specific_prefix(self.prefix)
        return self.real != other

    # unary operators/functions
    def __neg__(self):
        """negative"""
        return UnitFloat(
            -self.real,
            self.units,
            si_prefix=self.prefix,
            stored_prefix=self.prefix,
            scale_representation=self.scale_representation,
        )

    def __pos__(self):
        """positive"""
        return UnitFloat(
            self.real,
            self.units,
            si_prefix=self.prefix,
            stored_prefix=self.prefix,
            scale_representation=self.scale_representation,
        )

    def __abs__(self):
        return UnitFloat(
            abs(self.real),
            self.units,
            si_prefix=self.prefix,
            stored_prefix=self.prefix,
            scale_representation=self.scale_representation,
        )

    def __round__(self, n=None):
        return round(self.real, n)

    # passthroughs for math
    def __floor__(self):
        return math.floor(self.real)

    def __ceil__(self):
        return math.ceil(self.real)

    def __trunc__(self):
        return math.trunc(self.real)

    def __copy__(self):
        return UnitFloat(
            self.real,
            self.units,
            si_prefix=self.prefix,
            stored_prefix=self.prefix,
            scale_representation=self.scale_representation,
        )

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    def __hex__(self):
        """hexidecimal represenation"""
        return self.real.hex()

    def hex(self):
        """Converts the value to hexidecimal"""
        return self.__hex__()

    def fromhex(self, s: str):
        """converts a hexidecimal string to a float value"""
        return float.fromhex(s)

    def as_integer_ratio(self):
        """returns the integer ratio of the float value"""
        return self.real.as_integer_ratio()

    def __getinitargs__(self):
        """init arguments for reinstantiation"""
        return (
            self.real,
            self.units,
            self.prefix,
            self.prefix,
            self.scale_representation,
        )

    def __reduce__(self):
        """pickle support"""
        return (
            UnitFloat,  # callable class object
            self.__getinitargs__(),  # init arguments
        )

    def specified_representation(self) -> str:
        """
        Returns the value represented in the specified prefix.

        :return: value with unit
        :rtype: str
        """
        return f'{self.real} {self.prefix}{self.unit}'

    def optimal_representation(self) -> str:
        """
        Determines the optimal representation of the value.

        :return: value, prefixed unit
        :rtype: str
        """
        def sign():
            return 1 if self.real > 0. else -1

        def uncertainty():
            if self.uncertainty is not None:
                return f'\u00b1{self.uncertainty / 10 ** p}'
            else:
                return ''

        value = abs(float(self.real))
        p = si_prefixes[self.prefix]  # retrieve power of current prefix

        # if the user doesn't want it scaled
        if self.scale_representation is False:
            return (
                f'{sign() * value:g}'
                f'{uncertainty()}'
                f' {prefix_from_power(p)}{self.unit}'
            )
        if 1000. > value >= 1. or value == 0.:  # if the value is within the standard range, do nothing
            pass
        elif 1. > value:  # if less than 1
            while 1. > value:
                if p - 3 not in si_prefixes.values():  # catch for undefined, very small prefixes
                    break
                p -= 3  # decrease power by 3
                value *= 10 ** 3  # multiply value by 10^3
        elif value >= 1000.:  # if greater than 1000
            while value >= 1000.:
                if p + 3 not in si_prefixes.values():  # catch for undefined, very large prefixes
                    break
                p += 3  # increase power by 3
                value /= 10 ** 3  # divide by 10^3

        return (
            f'{sign() * value:g}'  # base value
            f'{uncertainty()}'  # uncertainty (if any)
            f' {prefix_from_power(p)}{self.unit}'  # prefixed unit
        )

    def change_return_prefix(self, newprefix=''):
        """
        Changes the return prefix to the specified prefix.

        :param str newprefix: new SI prefix
        """
        # catch for legacy implementations
        warnings.warn('change_return_prefix has be depreciated. Use UnitFloat.prefix instead')
        self.prefix = newprefix

    def specific_prefix(self, newprefix) -> float:
        """
        Returns the value converted to the specific prefix

        :param newprefix: new SI prefix
        :return: value with the specific prefix
        :rtype: float
        """
        return scale_value_by_prefix(
            self.real,
            newprefix,
            self.prefix,
        )

    def as_constant(self) -> 'Constant':
        """Returns the value as a Constant instance"""
        return Constant(
            self.real,
            self.units,
            self.uncertainty,
        )


class Constant(UnitFloat):
    def __init__(self,
                 value,
                 unit='',
                 uncertainty=None,
                 scale_representation: bool = None,
                 ):
        """
        A class for storing a constant value with a unit. The value will be immutable except by accessing protected
        variables.

        :param float value: the value to store
        :param str unit: unit for the value
        :param float uncertainty: Uncertainty in the float value (this will be interpreted as a +/- value with the same
            prefix as the incoming value).
        :param bool scale_representation: Whether to scale the representation of the value. Set this to False to
            disable value scaling.
        """
        UnitFloat.__init__(
            self,
            value,
            unit,
            uncertainty=uncertainty,
            scale_representation=scale_representation,
        )

    @property
    def real(self) -> float:  # only define retrieval, not modification of real value
        return self._real

    @real.setter
    def real(self, value):
        raise AttributeError(f'The value of a {self.__class__.__name__} instance may not be modified. ')

    @real.deleter
    def real(self):
        raise AttributeError(f'The value of a {self.__class__.__name__} instance may not be modified. ')

    # disable augmented magic methods (prevent modification)
    def __imul__(self, other):
        return NotImplemented

    def __idiv__(self, other):
        return NotImplemented

    def __ipow__(self, other):
        return NotImplemented

    def __itruediv__(self, other):
        return NotImplemented

    def __isub__(self, other):
        return NotImplemented

    def __iadd__(self, other):
        return NotImplemented

    def __imod__(self, other):
        return NotImplemented
