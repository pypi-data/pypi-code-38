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


class InnerShadowEffect(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'direction': 'float',
        'distance': 'float',
        'blur_radius': 'float',
        'shadow_color': 'str'
    }

    attribute_map = {
        'direction': 'Direction',
        'distance': 'Distance',
        'blur_radius': 'BlurRadius',
        'shadow_color': 'ShadowColor'
    }

    def __init__(self, direction=None, distance=None, blur_radius=None, shadow_color=None):  # noqa: E501
        """InnerShadowEffect - a model defined in Swagger"""  # noqa: E501

        self._direction = None
        self._distance = None
        self._blur_radius = None
        self._shadow_color = None

        self.direction = direction
        self.distance = distance
        self.blur_radius = blur_radius
        if shadow_color is not None:
            self.shadow_color = shadow_color

    @property
    def direction(self):
        """Gets the direction of this InnerShadowEffect.  # noqa: E501

        direction  # noqa: E501

        :return: The direction of this InnerShadowEffect.  # noqa: E501
        :rtype: float
        """
        return self._direction

    @direction.setter
    def direction(self, direction):
        """Sets the direction of this InnerShadowEffect.

        direction  # noqa: E501

        :param direction: The direction of this InnerShadowEffect.  # noqa: E501
        :type: float
        """
        self._direction = direction

    @property
    def distance(self):
        """Gets the distance of this InnerShadowEffect.  # noqa: E501

        distance  # noqa: E501

        :return: The distance of this InnerShadowEffect.  # noqa: E501
        :rtype: float
        """
        return self._distance

    @distance.setter
    def distance(self, distance):
        """Sets the distance of this InnerShadowEffect.

        distance  # noqa: E501

        :param distance: The distance of this InnerShadowEffect.  # noqa: E501
        :type: float
        """
        self._distance = distance

    @property
    def blur_radius(self):
        """Gets the blur_radius of this InnerShadowEffect.  # noqa: E501

        blur radius  # noqa: E501

        :return: The blur_radius of this InnerShadowEffect.  # noqa: E501
        :rtype: float
        """
        return self._blur_radius

    @blur_radius.setter
    def blur_radius(self, blur_radius):
        """Sets the blur_radius of this InnerShadowEffect.

        blur radius  # noqa: E501

        :param blur_radius: The blur_radius of this InnerShadowEffect.  # noqa: E501
        :type: float
        """
        self._blur_radius = blur_radius

    @property
    def shadow_color(self):
        """Gets the shadow_color of this InnerShadowEffect.  # noqa: E501

        shadow color  # noqa: E501

        :return: The shadow_color of this InnerShadowEffect.  # noqa: E501
        :rtype: str
        """
        return self._shadow_color

    @shadow_color.setter
    def shadow_color(self, shadow_color):
        """Sets the shadow_color of this InnerShadowEffect.

        shadow color  # noqa: E501

        :param shadow_color: The shadow_color of this InnerShadowEffect.  # noqa: E501
        :type: str
        """
        self._shadow_color = shadow_color

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
        if not isinstance(other, InnerShadowEffect):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
