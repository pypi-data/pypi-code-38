# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose">
#   Copyright (c) 2018 Aspose.Slides for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

import pprint
import re  # noqa: F401

import six

from asposeslidescloud.models.fill_format import FillFormat

class GradientFill(FillFormat):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'direction': 'str',
        'shape': 'str',
        'stops': 'list[GradientFillStop]',
        'linear_angle': 'float',
        'is_scaled': 'bool',
        'tile_flip': 'str'
    }

    attribute_map = {
        'type': 'Type',
        'direction': 'Direction',
        'shape': 'Shape',
        'stops': 'Stops',
        'linear_angle': 'LinearAngle',
        'is_scaled': 'IsScaled',
        'tile_flip': 'TileFlip'
    }

    def __init__(self, type='Gradient', direction=None, shape=None, stops=None, linear_angle=None, is_scaled=None, tile_flip=None):  # noqa: E501
        """GradientFill - a model defined in Swagger"""  # noqa: E501
        super(GradientFill, self).__init__(type)

        self._direction = None
        self._shape = None
        self._stops = None
        self._linear_angle = None
        self._is_scaled = None
        self._tile_flip = None

        self.direction = direction
        self.shape = shape
        if stops is not None:
            self.stops = stops
        self.linear_angle = linear_angle
        self.is_scaled = is_scaled
        self.tile_flip = tile_flip

    @property
    def direction(self):
        """Gets the direction of this GradientFill.  # noqa: E501

        Gradient style.  # noqa: E501

        :return: The direction of this GradientFill.  # noqa: E501
        :rtype: str
        """
        return self._direction

    @direction.setter
    def direction(self, direction):
        """Sets the direction of this GradientFill.

        Gradient style.  # noqa: E501

        :param direction: The direction of this GradientFill.  # noqa: E501
        :type: str
        """
        if direction is not None:
            allowed_values = ["FromCorner1", "FromCorner2", "FromCorner3", "FromCorner4", "FromCenter", "NotDefined"]  # noqa: E501
            if direction not in allowed_values:
                raise ValueError(
                    "Invalid value for `direction` ({0}), must be one of {1}"  # noqa: E501
                    .format(direction, allowed_values)
                )
        self._direction = direction

    @property
    def shape(self):
        """Gets the shape of this GradientFill.  # noqa: E501

        Gradient shape.  # noqa: E501

        :return: The shape of this GradientFill.  # noqa: E501
        :rtype: str
        """
        return self._shape

    @shape.setter
    def shape(self, shape):
        """Sets the shape of this GradientFill.

        Gradient shape.  # noqa: E501

        :param shape: The shape of this GradientFill.  # noqa: E501
        :type: str
        """
        if shape is not None:
            allowed_values = ["Linear", "Rectangle", "Radial", "Path", "NotDefined"]  # noqa: E501
            if shape not in allowed_values:
                raise ValueError(
                    "Invalid value for `shape` ({0}), must be one of {1}"  # noqa: E501
                    .format(shape, allowed_values)
                )
        self._shape = shape

    @property
    def stops(self):
        """Gets the stops of this GradientFill.  # noqa: E501

        Gradient stops.  # noqa: E501

        :return: The stops of this GradientFill.  # noqa: E501
        :rtype: list[GradientFillStop]
        """
        return self._stops

    @stops.setter
    def stops(self, stops):
        """Sets the stops of this GradientFill.

        Gradient stops.  # noqa: E501

        :param stops: The stops of this GradientFill.  # noqa: E501
        :type: list[GradientFillStop]
        """
        self._stops = stops

    @property
    def linear_angle(self):
        """Gets the linear_angle of this GradientFill.  # noqa: E501

        Gradient angle.  # noqa: E501

        :return: The linear_angle of this GradientFill.  # noqa: E501
        :rtype: float
        """
        return self._linear_angle

    @linear_angle.setter
    def linear_angle(self, linear_angle):
        """Sets the linear_angle of this GradientFill.

        Gradient angle.  # noqa: E501

        :param linear_angle: The linear_angle of this GradientFill.  # noqa: E501
        :type: float
        """
        self._linear_angle = linear_angle

    @property
    def is_scaled(self):
        """Gets the is_scaled of this GradientFill.  # noqa: E501

        True if the gradient is scaled.  # noqa: E501

        :return: The is_scaled of this GradientFill.  # noqa: E501
        :rtype: bool
        """
        return self._is_scaled

    @is_scaled.setter
    def is_scaled(self, is_scaled):
        """Sets the is_scaled of this GradientFill.

        True if the gradient is scaled.  # noqa: E501

        :param is_scaled: The is_scaled of this GradientFill.  # noqa: E501
        :type: bool
        """
        self._is_scaled = is_scaled

    @property
    def tile_flip(self):
        """Gets the tile_flip of this GradientFill.  # noqa: E501

        Gradient flipping mode.  # noqa: E501

        :return: The tile_flip of this GradientFill.  # noqa: E501
        :rtype: str
        """
        return self._tile_flip

    @tile_flip.setter
    def tile_flip(self, tile_flip):
        """Sets the tile_flip of this GradientFill.

        Gradient flipping mode.  # noqa: E501

        :param tile_flip: The tile_flip of this GradientFill.  # noqa: E501
        :type: str
        """
        if tile_flip is not None:
            allowed_values = ["NoFlip", "FlipX", "FlipY", "FlipBoth", "NotDefined"]  # noqa: E501
            if tile_flip not in allowed_values:
                raise ValueError(
                    "Invalid value for `tile_flip` ({0}), must be one of {1}"  # noqa: E501
                    .format(tile_flip, allowed_values)
                )
        self._tile_flip = tile_flip

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, GradientFill):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
