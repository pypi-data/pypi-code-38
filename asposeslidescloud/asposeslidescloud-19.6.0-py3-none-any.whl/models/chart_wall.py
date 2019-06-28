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


class ChartWall(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'thickness': 'int',
        'picture_type': 'str'
    }

    attribute_map = {
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'thickness': 'Thickness',
        'picture_type': 'PictureType'
    }

    def __init__(self, fill_format=None, effect_format=None, line_format=None, thickness=None, picture_type=None):  # noqa: E501
        """ChartWall - a model defined in Swagger"""  # noqa: E501

        self._fill_format = None
        self._effect_format = None
        self._line_format = None
        self._thickness = None
        self._picture_type = None

        if fill_format is not None:
            self.fill_format = fill_format
        if effect_format is not None:
            self.effect_format = effect_format
        if line_format is not None:
            self.line_format = line_format
        self.thickness = thickness
        self.picture_type = picture_type

    @property
    def fill_format(self):
        """Gets the fill_format of this ChartWall.  # noqa: E501

        Get or sets the fill format.  # noqa: E501

        :return: The fill_format of this ChartWall.  # noqa: E501
        :rtype: FillFormat
        """
        return self._fill_format

    @fill_format.setter
    def fill_format(self, fill_format):
        """Sets the fill_format of this ChartWall.

        Get or sets the fill format.  # noqa: E501

        :param fill_format: The fill_format of this ChartWall.  # noqa: E501
        :type: FillFormat
        """
        self._fill_format = fill_format

    @property
    def effect_format(self):
        """Gets the effect_format of this ChartWall.  # noqa: E501

        Get or sets the effect format.  # noqa: E501

        :return: The effect_format of this ChartWall.  # noqa: E501
        :rtype: EffectFormat
        """
        return self._effect_format

    @effect_format.setter
    def effect_format(self, effect_format):
        """Sets the effect_format of this ChartWall.

        Get or sets the effect format.  # noqa: E501

        :param effect_format: The effect_format of this ChartWall.  # noqa: E501
        :type: EffectFormat
        """
        self._effect_format = effect_format

    @property
    def line_format(self):
        """Gets the line_format of this ChartWall.  # noqa: E501

        Get or sets the line format.  # noqa: E501

        :return: The line_format of this ChartWall.  # noqa: E501
        :rtype: LineFormat
        """
        return self._line_format

    @line_format.setter
    def line_format(self, line_format):
        """Sets the line_format of this ChartWall.

        Get or sets the line format.  # noqa: E501

        :param line_format: The line_format of this ChartWall.  # noqa: E501
        :type: LineFormat
        """
        self._line_format = line_format

    @property
    def thickness(self):
        """Gets the thickness of this ChartWall.  # noqa: E501

        Get or sets wall thickness as a percentage of the largest dimension of the plot volume.  # noqa: E501

        :return: The thickness of this ChartWall.  # noqa: E501
        :rtype: int
        """
        return self._thickness

    @thickness.setter
    def thickness(self, thickness):
        """Sets the thickness of this ChartWall.

        Get or sets wall thickness as a percentage of the largest dimension of the plot volume.  # noqa: E501

        :param thickness: The thickness of this ChartWall.  # noqa: E501
        :type: int
        """
        self._thickness = thickness

    @property
    def picture_type(self):
        """Gets the picture_type of this ChartWall.  # noqa: E501

        Get or sets mode of bar picture filling.  # noqa: E501

        :return: The picture_type of this ChartWall.  # noqa: E501
        :rtype: str
        """
        return self._picture_type

    @picture_type.setter
    def picture_type(self, picture_type):
        """Sets the picture_type of this ChartWall.

        Get or sets mode of bar picture filling.  # noqa: E501

        :param picture_type: The picture_type of this ChartWall.  # noqa: E501
        :type: str
        """
        if picture_type is not None:
            allowed_values = ["Stack", "StackScale", "Stretch", "NotDefined"]  # noqa: E501
            if picture_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `picture_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(picture_type, allowed_values)
                )
        self._picture_type = picture_type

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
        if not isinstance(other, ChartWall):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
