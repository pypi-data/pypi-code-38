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


class PresetShadowEffect(object):


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
        'preset': 'str',
        'shadow_color': 'str'
    }

    attribute_map = {
        'direction': 'Direction',
        'distance': 'Distance',
        'preset': 'Preset',
        'shadow_color': 'ShadowColor'
    }

    def __init__(self, direction=None, distance=None, preset=None, shadow_color=None):  # noqa: E501
        """PresetShadowEffect - a model defined in Swagger"""  # noqa: E501

        self._direction = None
        self._distance = None
        self._preset = None
        self._shadow_color = None

        self.direction = direction
        self.distance = distance
        self.preset = preset
        if shadow_color is not None:
            self.shadow_color = shadow_color

    @property
    def direction(self):
        """Gets the direction of this PresetShadowEffect.  # noqa: E501

        direction  # noqa: E501

        :return: The direction of this PresetShadowEffect.  # noqa: E501
        :rtype: float
        """
        return self._direction

    @direction.setter
    def direction(self, direction):
        """Sets the direction of this PresetShadowEffect.

        direction  # noqa: E501

        :param direction: The direction of this PresetShadowEffect.  # noqa: E501
        :type: float
        """
        self._direction = direction

    @property
    def distance(self):
        """Gets the distance of this PresetShadowEffect.  # noqa: E501

        distance  # noqa: E501

        :return: The distance of this PresetShadowEffect.  # noqa: E501
        :rtype: float
        """
        return self._distance

    @distance.setter
    def distance(self, distance):
        """Sets the distance of this PresetShadowEffect.

        distance  # noqa: E501

        :param distance: The distance of this PresetShadowEffect.  # noqa: E501
        :type: float
        """
        self._distance = distance

    @property
    def preset(self):
        """Gets the preset of this PresetShadowEffect.  # noqa: E501

        preset  # noqa: E501

        :return: The preset of this PresetShadowEffect.  # noqa: E501
        :rtype: str
        """
        return self._preset

    @preset.setter
    def preset(self, preset):
        """Sets the preset of this PresetShadowEffect.

        preset  # noqa: E501

        :param preset: The preset of this PresetShadowEffect.  # noqa: E501
        :type: str
        """
        if preset is not None:
            allowed_values = ["TopLeftDropShadow", "TopLeftLargeDropShadow", "BackLeftLongPerspectiveShadow", "BackRightLongPerspectiveShadow", "TopLeftDoubleDropShadow", "BottomRightSmallDropShadow", "FrontLeftLongPerspectiveShadow", "FrontRightLongPerspectiveShadow", "OuterBoxShadow3D", "InnerBoxShadow3D", "BackCenterPerspectiveShadow", "TopRightDropShadow", "FrontBottomShadow", "BackLeftPerspectiveShadow", "BackRightPerspectiveShadow", "BottomLeftDropShadow", "BottomRightDropShadow", "FrontLeftPerspectiveShadow", "FrontRightPerspectiveShadow", "TopLeftSmallDropShadow"]  # noqa: E501
            if preset not in allowed_values:
                raise ValueError(
                    "Invalid value for `preset` ({0}), must be one of {1}"  # noqa: E501
                    .format(preset, allowed_values)
                )
        self._preset = preset

    @property
    def shadow_color(self):
        """Gets the shadow_color of this PresetShadowEffect.  # noqa: E501

        shadow color  # noqa: E501

        :return: The shadow_color of this PresetShadowEffect.  # noqa: E501
        :rtype: str
        """
        return self._shadow_color

    @shadow_color.setter
    def shadow_color(self, shadow_color):
        """Sets the shadow_color of this PresetShadowEffect.

        shadow color  # noqa: E501

        :param shadow_color: The shadow_color of this PresetShadowEffect.  # noqa: E501
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
        if not isinstance(other, PresetShadowEffect):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
