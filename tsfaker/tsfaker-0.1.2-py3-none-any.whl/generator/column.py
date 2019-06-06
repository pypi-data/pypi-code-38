"""
Column generators, as defined in Table-Schema specification
https://frictionlessdata.io/specs/table-schema/#types-and-formats
"""

import string

import numpy as np
import rstr
from dsfaker.generators.date import RandomDatetime
from dsfaker.generators.distributions import Randint, Uniform

DEFAULT_MAXIMUM_NUMBER = 10 ** 10


class AbstractColumnGenerator:
    """
    Abstract column generator.

    This class avoid a direct coupling with dsfaker library
    """

    def __init__(self, nrows: int):
        self.nrows = nrows

    def get_1d_array(self) -> np.array:
        """
        Abstract generator of a numpy array of shape (nrows, ) - 1 dimension
        """
        raise NotImplementedError("_get_batch not implemented")

    def get_2d_array(self) -> np.array:
        """
        Generate a numpy array column of shape (nrows, 1) - 2 dimension
        """
        return np.reshape(self.get_1d_array(), (self.nrows, 1))


class Bounded(AbstractColumnGenerator):
    def __init__(self, *args, minimum=None, maximum=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.minimum = minimum or self.DEFAULT_MINIMUM
        self.maximum = maximum or self.DEFAULT_MAXIMUM


class Collection(AbstractColumnGenerator):
    def __init__(self, *args, min_length=None, max_length=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_length = min_length or self.DEFAULT_MIN_LENGTH
        self.max_length = max_length or self.DEFAULT_MAX_LENGTH


class String(Collection):
    """
    Integer column generator
    """
    DEFAULT_MIN_LENGTH = 0
    DEFAULT_MAX_LENGTH = 20
    DEFAULT_CHARACTERS = string.ascii_letters  # string.printable

    def _get_single(self):
        return rstr.rstr(self.DEFAULT_CHARACTERS, start_range=self.min_length, end_range=self.max_length)

    def get_1d_array(self):
        if self.nrows == 0:
            return np.empty((0, 1), np.unicode_)
        values = [self._get_single() for _ in range(self.nrows)]
        return np.asarray(values)


class Integer(Bounded):
    """
    Integer column generator
    """
    DEFAULT_MINIMUM = -DEFAULT_MAXIMUM_NUMBER
    DEFAULT_MAXIMUM = DEFAULT_MAXIMUM_NUMBER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_1d_array(self):
        return Randint(self.minimum, self.maximum).get_batch(self.nrows)


class Number(Bounded):
    """
    Number (float) column generator
    """
    DEFAULT_MINIMUM = -DEFAULT_MAXIMUM_NUMBER
    DEFAULT_MAXIMUM = DEFAULT_MAXIMUM_NUMBER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_1d_array(self):
        return Uniform(self.minimum, self.maximum).get_batch(self.nrows)


class Datetime(Bounded):
    """
    Datetime column generator
    """
    DEFAULT_MINIMUM = np.datetime64("1900-01-01")
    DEFAULT_MAXIMUM = np.datetime64("2030-01-01")
    unit = 's'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_1d_array(self) -> np.array:
        generator = RandomDatetime(Uniform(0, 1), start=self.minimum, end=self.maximum, unit='s')
        column = generator.get_batch(self.nrows)
        return np.datetime_as_string(column, unit=self.unit)


class Date(Datetime):
    """
    Datetime column generator
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit = 'D'


class Yearmonth(Datetime):
    """
    Year column generator
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit = 'M'


class Year(Datetime):
    """
    Year column generator
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit = 'Y'
