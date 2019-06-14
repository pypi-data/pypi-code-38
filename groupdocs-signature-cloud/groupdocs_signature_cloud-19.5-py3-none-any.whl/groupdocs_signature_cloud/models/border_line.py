# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="BorderLine.py">
#   Copyright (c) 2003-2019 Aspose Pty Ltd
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

class BorderLine(object):
    """
    Instance to keep Border line properties
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'style': 'str',
        'transparency': 'float',
        'weight': 'float',
        'color': 'Color'
    }

    attribute_map = {
        'style': 'Style',
        'transparency': 'Transparency',
        'weight': 'Weight',
        'color': 'Color'
    }

    def __init__(self, style=None, transparency=None, weight=None, color=None, **kwargs):  # noqa: E501
        """Initializes new instance of BorderLine"""  # noqa: E501

        self._style = None
        self._transparency = None
        self._weight = None
        self._color = None

        if style is not None:
            self.style = style
        if transparency is not None:
            self.transparency = transparency
        if weight is not None:
            self.weight = weight
        if color is not None:
            self.color = color
    
    @property
    def style(self):
        """
        Gets the style.  # noqa: E501

        Gets or sets the signature border style  # noqa: E501

        :return: The style.  # noqa: E501
        :rtype: str
        """
        return self._style

    @style.setter
    def style(self, style):
        """
        Sets the style.

        Gets or sets the signature border style  # noqa: E501

        :param style: The style.  # noqa: E501
        :type: str
        """
        if style is None:
            raise ValueError("Invalid value for `style`, must not be `None`")  # noqa: E501
        allowed_values = ["Default", "Solid", "ShortDash", "ShortDot", "ShortDashDot", "ShortDashDotDot", "Dot", "Dash", "LongDash", "DashDot", "LongDashDot", "LongDashDotDot"]  # noqa: E501
        if not style.isdigit():	
            if style not in allowed_values:
                raise ValueError(
                    "Invalid value for `style` ({0}), must be one of {1}"  # noqa: E501
                    .format(style, allowed_values))
            self._style = style
        else:
            self._style = allowed_values[int(style) if six.PY3 else long(style)]
    
    @property
    def transparency(self):
        """
        Gets the transparency.  # noqa: E501

        Gets or sets the signature border transparency (value from 0.0 (opaque) through 1.0 (clear))  # noqa: E501

        :return: The transparency.  # noqa: E501
        :rtype: float
        """
        return self._transparency

    @transparency.setter
    def transparency(self, transparency):
        """
        Sets the transparency.

        Gets or sets the signature border transparency (value from 0.0 (opaque) through 1.0 (clear))  # noqa: E501

        :param transparency: The transparency.  # noqa: E501
        :type: float
        """
        if transparency is None:
            raise ValueError("Invalid value for `transparency`, must not be `None`")  # noqa: E501
        self._transparency = transparency
    
    @property
    def weight(self):
        """
        Gets the weight.  # noqa: E501

        Gets or sets the weight of the signature border  # noqa: E501

        :return: The weight.  # noqa: E501
        :rtype: float
        """
        return self._weight

    @weight.setter
    def weight(self, weight):
        """
        Sets the weight.

        Gets or sets the weight of the signature border  # noqa: E501

        :param weight: The weight.  # noqa: E501
        :type: float
        """
        if weight is None:
            raise ValueError("Invalid value for `weight`, must not be `None`")  # noqa: E501
        self._weight = weight
    
    @property
    def color(self):
        """
        Gets the color.  # noqa: E501

        Gets or sets the border color of signature  # noqa: E501

        :return: The color.  # noqa: E501
        :rtype: Color
        """
        return self._color

    @color.setter
    def color(self, color):
        """
        Sets the color.

        Gets or sets the border color of signature  # noqa: E501

        :param color: The color.  # noqa: E501
        :type: Color
        """
        self._color = color

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
        if not isinstance(other, BorderLine):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
