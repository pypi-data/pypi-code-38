# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="RadialGradientBrush.py">
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

from groupdocs_signature_cloud.models import Brush

class RadialGradientBrush(Brush):
    """
    Represents radial gradient brush
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'inner_color': 'Color',
        'outer_color': 'Color'
    }

    attribute_map = {
        'inner_color': 'InnerColor',
        'outer_color': 'OuterColor'
    }

    def __init__(self, inner_color=None, outer_color=None, **kwargs):  # noqa: E501
        """Initializes new instance of RadialGradientBrush"""  # noqa: E501

        self._inner_color = None
        self._outer_color = None

        if inner_color is not None:
            self.inner_color = inner_color
        if outer_color is not None:
            self.outer_color = outer_color

        base = super(RadialGradientBrush, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def inner_color(self):
        """
        Gets the inner_color.  # noqa: E501

        Gets or sets inner gradient color  # noqa: E501

        :return: The inner_color.  # noqa: E501
        :rtype: Color
        """
        return self._inner_color

    @inner_color.setter
    def inner_color(self, inner_color):
        """
        Sets the inner_color.

        Gets or sets inner gradient color  # noqa: E501

        :param inner_color: The inner_color.  # noqa: E501
        :type: Color
        """
        self._inner_color = inner_color
    
    @property
    def outer_color(self):
        """
        Gets the outer_color.  # noqa: E501

        Gets or sets outer gradient color  # noqa: E501

        :return: The outer_color.  # noqa: E501
        :rtype: Color
        """
        return self._outer_color

    @outer_color.setter
    def outer_color(self, outer_color):
        """
        Sets the outer_color.

        Gets or sets outer gradient color  # noqa: E501

        :param outer_color: The outer_color.  # noqa: E501
        :type: Color
        """
        self._outer_color = outer_color

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
        if not isinstance(other, RadialGradientBrush):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
