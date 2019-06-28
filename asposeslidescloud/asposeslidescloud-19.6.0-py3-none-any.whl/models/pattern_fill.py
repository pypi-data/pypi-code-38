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

class PatternFill(FillFormat):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'back_color': 'str',
        'fore_color': 'str',
        'style': 'str'
    }

    attribute_map = {
        'type': 'Type',
        'back_color': 'BackColor',
        'fore_color': 'ForeColor',
        'style': 'Style'
    }

    def __init__(self, type='Pattern', back_color=None, fore_color=None, style=None):  # noqa: E501
        """PatternFill - a model defined in Swagger"""  # noqa: E501
        super(PatternFill, self).__init__(type)

        self._back_color = None
        self._fore_color = None
        self._style = None

        if back_color is not None:
            self.back_color = back_color
        if fore_color is not None:
            self.fore_color = fore_color
        self.style = style

    @property
    def back_color(self):
        """Gets the back_color of this PatternFill.  # noqa: E501

        Gets or sets the back color of the pattern fill.  # noqa: E501

        :return: The back_color of this PatternFill.  # noqa: E501
        :rtype: str
        """
        return self._back_color

    @back_color.setter
    def back_color(self, back_color):
        """Sets the back_color of this PatternFill.

        Gets or sets the back color of the pattern fill.  # noqa: E501

        :param back_color: The back_color of this PatternFill.  # noqa: E501
        :type: str
        """
        self._back_color = back_color

    @property
    def fore_color(self):
        """Gets the fore_color of this PatternFill.  # noqa: E501

        Gets or sets the fore color of the pattern fill.  # noqa: E501

        :return: The fore_color of this PatternFill.  # noqa: E501
        :rtype: str
        """
        return self._fore_color

    @fore_color.setter
    def fore_color(self, fore_color):
        """Sets the fore_color of this PatternFill.

        Gets or sets the fore color of the pattern fill.  # noqa: E501

        :param fore_color: The fore_color of this PatternFill.  # noqa: E501
        :type: str
        """
        self._fore_color = fore_color

    @property
    def style(self):
        """Gets the style of this PatternFill.  # noqa: E501

        Gets or sets the style of pattern fill.  # noqa: E501

        :return: The style of this PatternFill.  # noqa: E501
        :rtype: str
        """
        return self._style

    @style.setter
    def style(self, style):
        """Sets the style of this PatternFill.

        Gets or sets the style of pattern fill.  # noqa: E501

        :param style: The style of this PatternFill.  # noqa: E501
        :type: str
        """
        if style is not None:
            allowed_values = ["Unknown", "Percent05", "Percent10", "Percent20", "Percent25", "Percent30", "Percent40", "Percent50", "Percent60", "Percent70", "Percent75", "Percent80", "Percent90", "DarkHorizontal", "DarkVertical", "DarkDownwardDiagonal", "DarkUpwardDiagonal", "SmallCheckerBoard", "Trellis", "LightHorizontal", "LightVertical", "LightDownwardDiagonal", "LightUpwardDiagonal", "SmallGrid", "DottedDiamond", "WideDownwardDiagonal", "WideUpwardDiagonal", "DashedUpwardDiagonal", "DashedDownwardDiagonal", "NarrowVertical", "NarrowHorizontal", "DashedVertical", "DashedHorizontal", "LargeConfetti", "LargeGrid", "HorizontalBrick", "LargeCheckerBoard", "SmallConfetti", "Zigzag", "SolidDiamond", "DiagonalBrick", "OutlinedDiamond", "Plaid", "Sphere", "Weave", "DottedGrid", "Divot", "Shingle", "Wave", "Horizontal", "Vertical", "Cross", "DownwardDiagonal", "UpwardDiagonal", "DiagonalCross", "NotDefined"]  # noqa: E501
            if style not in allowed_values:
                raise ValueError(
                    "Invalid value for `style` ({0}), must be one of {1}"  # noqa: E501
                    .format(style, allowed_values)
                )
        self._style = style

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
        if not isinstance(other, PatternFill):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
