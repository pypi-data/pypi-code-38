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


class Axes(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'horizontal_axis': 'Axis',
        'vertical_axis': 'Axis',
        'secondary_horizontal_axis': 'Axis',
        'secondary_vertical_axis': 'Axis'
    }

    attribute_map = {
        'horizontal_axis': 'HorizontalAxis',
        'vertical_axis': 'VerticalAxis',
        'secondary_horizontal_axis': 'SecondaryHorizontalAxis',
        'secondary_vertical_axis': 'SecondaryVerticalAxis'
    }

    def __init__(self, horizontal_axis=None, vertical_axis=None, secondary_horizontal_axis=None, secondary_vertical_axis=None):  # noqa: E501
        """Axes - a model defined in Swagger"""  # noqa: E501

        self._horizontal_axis = None
        self._vertical_axis = None
        self._secondary_horizontal_axis = None
        self._secondary_vertical_axis = None

        if horizontal_axis is not None:
            self.horizontal_axis = horizontal_axis
        if vertical_axis is not None:
            self.vertical_axis = vertical_axis
        if secondary_horizontal_axis is not None:
            self.secondary_horizontal_axis = secondary_horizontal_axis
        if secondary_vertical_axis is not None:
            self.secondary_vertical_axis = secondary_vertical_axis

    @property
    def horizontal_axis(self):
        """Gets the horizontal_axis of this Axes.  # noqa: E501

        Gets or sets the horizontal axis.  # noqa: E501

        :return: The horizontal_axis of this Axes.  # noqa: E501
        :rtype: Axis
        """
        return self._horizontal_axis

    @horizontal_axis.setter
    def horizontal_axis(self, horizontal_axis):
        """Sets the horizontal_axis of this Axes.

        Gets or sets the horizontal axis.  # noqa: E501

        :param horizontal_axis: The horizontal_axis of this Axes.  # noqa: E501
        :type: Axis
        """
        self._horizontal_axis = horizontal_axis

    @property
    def vertical_axis(self):
        """Gets the vertical_axis of this Axes.  # noqa: E501

        Gets or sets the vertical axis.  # noqa: E501

        :return: The vertical_axis of this Axes.  # noqa: E501
        :rtype: Axis
        """
        return self._vertical_axis

    @vertical_axis.setter
    def vertical_axis(self, vertical_axis):
        """Sets the vertical_axis of this Axes.

        Gets or sets the vertical axis.  # noqa: E501

        :param vertical_axis: The vertical_axis of this Axes.  # noqa: E501
        :type: Axis
        """
        self._vertical_axis = vertical_axis

    @property
    def secondary_horizontal_axis(self):
        """Gets the secondary_horizontal_axis of this Axes.  # noqa: E501

        Gets or sets the secondary horizontal axis.  # noqa: E501

        :return: The secondary_horizontal_axis of this Axes.  # noqa: E501
        :rtype: Axis
        """
        return self._secondary_horizontal_axis

    @secondary_horizontal_axis.setter
    def secondary_horizontal_axis(self, secondary_horizontal_axis):
        """Sets the secondary_horizontal_axis of this Axes.

        Gets or sets the secondary horizontal axis.  # noqa: E501

        :param secondary_horizontal_axis: The secondary_horizontal_axis of this Axes.  # noqa: E501
        :type: Axis
        """
        self._secondary_horizontal_axis = secondary_horizontal_axis

    @property
    def secondary_vertical_axis(self):
        """Gets the secondary_vertical_axis of this Axes.  # noqa: E501

        Gets or sets the secondary vertical axis.  # noqa: E501

        :return: The secondary_vertical_axis of this Axes.  # noqa: E501
        :rtype: Axis
        """
        return self._secondary_vertical_axis

    @secondary_vertical_axis.setter
    def secondary_vertical_axis(self, secondary_vertical_axis):
        """Sets the secondary_vertical_axis of this Axes.

        Gets or sets the secondary vertical axis.  # noqa: E501

        :param secondary_vertical_axis: The secondary_vertical_axis of this Axes.  # noqa: E501
        :type: Axis
        """
        self._secondary_vertical_axis = secondary_vertical_axis

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
        if not isinstance(other, Axes):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
