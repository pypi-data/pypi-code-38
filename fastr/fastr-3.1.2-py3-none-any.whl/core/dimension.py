# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from abc import ABCMeta, abstractproperty, abstractmethod

import sympy

from .. import exceptions


class Dimension(object):
    """
    A class representing a dimension. It contains the name and size of the
    dimension.
    """
    __slots__ = ('_name', '_size')

    def __init__(self, name, size):
        """
        The constructor for the dimension.

        :param str name: Name of the dimension
        :param size: Size fo the dimension
        :type size: int or sympy.Symbol
        """
        if isinstance(name, str):
            try:
                name = str(name)
            except UnicodeEncodeError:
                raise exceptions.FastrTypeError("Dimensions cannot contain unicode characters!")

        if not isinstance(name, str):
            raise exceptions.FastrTypeError("Dimension.name should be a str, "
                                            "found [{}] {}".format(type(name).__name__,
                                                                   size))

        self._name = name
        self._size = None
        self.size = size

    def __repr__(self):
        """
        String representation of a Dimension
        """
        return "<Dimension {d.name} ({d.size})>".format(d=self)

    def __eq__(self, other):
        """
        Dimension is the same if the name and size are the same
        """
        return self.name == other.name and self.size == other.size

    def __ne__(self, other):
        """
        The not equal test is simply the inverse of the equal test
        """
        return not self == other

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if not isinstance(value, (int, sympy.Symbol)):
            raise exceptions.FastrTypeError("Dimension.size should be an int or"
                                            " sympy.Symbol, found [{}] {}".format(type(value).__name__,
                                                                                  value))

        if isinstance(value, int) and value < 0:
            raise exceptions.FastrValueError("Dimension.size should be positive")

        self._size = value

    def update_size(self, value):
        if self._size == value:
            # No effect
            return

        if not isinstance(value, int):
            raise exceptions.FastrTypeError("Dimension.size can only be updated by an int "
                                            " found [{}] {}".format(type(value).__name__,
                                                                    value))

        if value < 0:
            raise exceptions.FastrValueError("Dimension.size should be positive")

        if isinstance(self._size, sympy.Symbol):
            self._size = value
        else:
            self._size = max(self._size, value)

    def copy(self):
        """
        Get a copy object of a Dimension
        """
        return Dimension(self.name, self.size)


class HasDimensions(object, metaclass=ABCMeta):
    """
    A Mixin class for any object that has a notion of dimensions and size. It
    uses the dimension property to expose the dimension name and size.
    """

    @abstractproperty
    def dimensions(self):
        """
        The dimensions has to be implemented by any subclass. It has to provide
        a tuple of Dimensions.

        :return: dimensions
        :rtype: tuple
        """

    @property
    def dimnames(self):
        """
        A tuple containing the dimension names of this object. All items of the
        tuple are of type str.
        """
        return tuple(x.name for x in self.dimensions)

    @property
    def size(self):
        """
        A tuple containing the size of this object. All items of the
        tuple are of type int or sympy.Symbol.
        """
        return tuple(x.size for x in self.dimensions)

    @property
    def ndims(self):
        """
        The number of dimensions in this object
        """
        return len(self.dimensions)


class ForwardsDimensions(HasDimensions):
    """
    Class of objects that have dimensions not because they contain data with
    dimensions but forward them (optionally with changes via combine_dimensions)
    """
    @abstractproperty
    def source(self):
        """
        The source object from which the dimensions are forwarded

        :return: the object from which the dimensions are forwarded
        :rtype: HasDimensions
        """

    @abstractmethod
    def combine_dimensions(self, dimensions):
        """
        Method to combine/manipulate the dimensions

        :param dimensions: the input dimensions from the source
        :return: dimensions manipulated for this object
        :rtype: tuple of dimensions
        """

    @property
    def dimensions(self):
        """
        The dimensions of the object based on the forwarding
        """
        return self.combine_dimensions(self.source.dimensions)
