# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="LinearGradientBrush.py">
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

class LinearGradientBrush(Brush):
    """
    Represents linear gradient brush
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'start_color': 'Color',
        'end_color': 'Color',
        'angle': 'float'
    }

    attribute_map = {
        'start_color': 'StartColor',
        'end_color': 'EndColor',
        'angle': 'Angle'
    }

    def __init__(self, start_color=None, end_color=None, angle=None, **kwargs):  # noqa: E501
        """Initializes new instance of LinearGradientBrush"""  # noqa: E501

        self._start_color = None
        self._end_color = None
        self._angle = None

        if start_color is not None:
            self.start_color = start_color
        if end_color is not None:
            self.end_color = end_color
        if angle is not None:
            self.angle = angle

        base = super(LinearGradientBrush, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def start_color(self):
        """
        Gets the start_color.  # noqa: E501

        Gets or sets start gradient color  # noqa: E501

        :return: The start_color.  # noqa: E501
        :rtype: Color
        """
        return self._start_color

    @start_color.setter
    def start_color(self, start_color):
        """
        Sets the start_color.

        Gets or sets start gradient color  # noqa: E501

        :param start_color: The start_color.  # noqa: E501
        :type: Color
        """
        self._start_color = start_color
    
    @property
    def end_color(self):
        """
        Gets the end_color.  # noqa: E501

        Gets or sets finish gradient color  # noqa: E501

        :return: The end_color.  # noqa: E501
        :rtype: Color
        """
        return self._end_color

    @end_color.setter
    def end_color(self, end_color):
        """
        Sets the end_color.

        Gets or sets finish gradient color  # noqa: E501

        :param end_color: The end_color.  # noqa: E501
        :type: Color
        """
        self._end_color = end_color
    
    @property
    def angle(self):
        """
        Gets the angle.  # noqa: E501

        Gets or sets gradient angle  # noqa: E501

        :return: The angle.  # noqa: E501
        :rtype: float
        """
        return self._angle

    @angle.setter
    def angle(self, angle):
        """
        Sets the angle.

        Gets or sets gradient angle  # noqa: E501

        :param angle: The angle.  # noqa: E501
        :type: float
        """
        if angle is None:
            raise ValueError("Invalid value for `angle`, must not be `None`")  # noqa: E501
        self._angle = angle

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
        if not isinstance(other, LinearGradientBrush):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
