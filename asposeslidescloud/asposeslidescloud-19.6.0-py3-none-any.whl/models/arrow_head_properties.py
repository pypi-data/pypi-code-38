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


class ArrowHeadProperties(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'length': 'str',
        'style': 'str',
        'width': 'str'
    }

    attribute_map = {
        'length': 'Length',
        'style': 'Style',
        'width': 'Width'
    }

    def __init__(self, length=None, style=None, width=None):  # noqa: E501
        """ArrowHeadProperties - a model defined in Swagger"""  # noqa: E501

        self._length = None
        self._style = None
        self._width = None

        self.length = length
        self.style = style
        self.width = width

    @property
    def length(self):
        """Gets the length of this ArrowHeadProperties.  # noqa: E501

        Length.  # noqa: E501

        :return: The length of this ArrowHeadProperties.  # noqa: E501
        :rtype: str
        """
        return self._length

    @length.setter
    def length(self, length):
        """Sets the length of this ArrowHeadProperties.

        Length.  # noqa: E501

        :param length: The length of this ArrowHeadProperties.  # noqa: E501
        :type: str
        """
        if length is not None:
            allowed_values = ["Short", "Medium", "Long", "NotDefined"]  # noqa: E501
            if length not in allowed_values:
                raise ValueError(
                    "Invalid value for `length` ({0}), must be one of {1}"  # noqa: E501
                    .format(length, allowed_values)
                )
        self._length = length

    @property
    def style(self):
        """Gets the style of this ArrowHeadProperties.  # noqa: E501

        Style.  # noqa: E501

        :return: The style of this ArrowHeadProperties.  # noqa: E501
        :rtype: str
        """
        return self._style

    @style.setter
    def style(self, style):
        """Sets the style of this ArrowHeadProperties.

        Style.  # noqa: E501

        :param style: The style of this ArrowHeadProperties.  # noqa: E501
        :type: str
        """
        if style is not None:
            allowed_values = ["None", "Triangle", "Stealth", "Diamond", "Oval", "Open", "NotDefined"]  # noqa: E501
            if style not in allowed_values:
                raise ValueError(
                    "Invalid value for `style` ({0}), must be one of {1}"  # noqa: E501
                    .format(style, allowed_values)
                )
        self._style = style

    @property
    def width(self):
        """Gets the width of this ArrowHeadProperties.  # noqa: E501

        Width.  # noqa: E501

        :return: The width of this ArrowHeadProperties.  # noqa: E501
        :rtype: str
        """
        return self._width

    @width.setter
    def width(self, width):
        """Sets the width of this ArrowHeadProperties.

        Width.  # noqa: E501

        :param width: The width of this ArrowHeadProperties.  # noqa: E501
        :type: str
        """
        if width is not None:
            allowed_values = ["Narrow", "Medium", "Wide", "NotDefined"]  # noqa: E501
            if width not in allowed_values:
                raise ValueError(
                    "Invalid value for `width` ({0}), must be one of {1}"  # noqa: E501
                    .format(width, allowed_values)
                )
        self._width = width

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
        if not isinstance(other, ArrowHeadProperties):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
