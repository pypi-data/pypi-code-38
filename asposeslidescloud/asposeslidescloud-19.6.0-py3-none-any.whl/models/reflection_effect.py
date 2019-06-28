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


class ReflectionEffect(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'direction': 'float',
        'fade_direction': 'float',
        'distance': 'float',
        'blur_radius': 'float',
        'scale_horizontal': 'float',
        'scale_vertical': 'float',
        'skew_horizontal': 'float',
        'skew_vertical': 'float',
        'start_pos_alpha': 'float',
        'end_pos_alpha': 'float',
        'start_reflection_opacity': 'float',
        'end_reflection_opacity': 'float',
        'rectangle_align': 'str',
        'rotate_shadow_with_shape': 'bool'
    }

    attribute_map = {
        'direction': 'Direction',
        'fade_direction': 'FadeDirection',
        'distance': 'Distance',
        'blur_radius': 'BlurRadius',
        'scale_horizontal': 'ScaleHorizontal',
        'scale_vertical': 'ScaleVertical',
        'skew_horizontal': 'SkewHorizontal',
        'skew_vertical': 'SkewVertical',
        'start_pos_alpha': 'StartPosAlpha',
        'end_pos_alpha': 'EndPosAlpha',
        'start_reflection_opacity': 'StartReflectionOpacity',
        'end_reflection_opacity': 'EndReflectionOpacity',
        'rectangle_align': 'RectangleAlign',
        'rotate_shadow_with_shape': 'RotateShadowWithShape'
    }

    def __init__(self, direction=None, fade_direction=None, distance=None, blur_radius=None, scale_horizontal=None, scale_vertical=None, skew_horizontal=None, skew_vertical=None, start_pos_alpha=None, end_pos_alpha=None, start_reflection_opacity=None, end_reflection_opacity=None, rectangle_align=None, rotate_shadow_with_shape=None):  # noqa: E501
        """ReflectionEffect - a model defined in Swagger"""  # noqa: E501

        self._direction = None
        self._fade_direction = None
        self._distance = None
        self._blur_radius = None
        self._scale_horizontal = None
        self._scale_vertical = None
        self._skew_horizontal = None
        self._skew_vertical = None
        self._start_pos_alpha = None
        self._end_pos_alpha = None
        self._start_reflection_opacity = None
        self._end_reflection_opacity = None
        self._rectangle_align = None
        self._rotate_shadow_with_shape = None

        self.direction = direction
        self.fade_direction = fade_direction
        self.distance = distance
        self.blur_radius = blur_radius
        self.scale_horizontal = scale_horizontal
        self.scale_vertical = scale_vertical
        self.skew_horizontal = skew_horizontal
        self.skew_vertical = skew_vertical
        self.start_pos_alpha = start_pos_alpha
        self.end_pos_alpha = end_pos_alpha
        self.start_reflection_opacity = start_reflection_opacity
        self.end_reflection_opacity = end_reflection_opacity
        self.rectangle_align = rectangle_align
        self.rotate_shadow_with_shape = rotate_shadow_with_shape

    @property
    def direction(self):
        """Gets the direction of this ReflectionEffect.  # noqa: E501

        direction  # noqa: E501

        :return: The direction of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._direction

    @direction.setter
    def direction(self, direction):
        """Sets the direction of this ReflectionEffect.

        direction  # noqa: E501

        :param direction: The direction of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._direction = direction

    @property
    def fade_direction(self):
        """Gets the fade_direction of this ReflectionEffect.  # noqa: E501

        fade direction  # noqa: E501

        :return: The fade_direction of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._fade_direction

    @fade_direction.setter
    def fade_direction(self, fade_direction):
        """Sets the fade_direction of this ReflectionEffect.

        fade direction  # noqa: E501

        :param fade_direction: The fade_direction of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._fade_direction = fade_direction

    @property
    def distance(self):
        """Gets the distance of this ReflectionEffect.  # noqa: E501

        distance  # noqa: E501

        :return: The distance of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._distance

    @distance.setter
    def distance(self, distance):
        """Sets the distance of this ReflectionEffect.

        distance  # noqa: E501

        :param distance: The distance of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._distance = distance

    @property
    def blur_radius(self):
        """Gets the blur_radius of this ReflectionEffect.  # noqa: E501

        blur radius  # noqa: E501

        :return: The blur_radius of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._blur_radius

    @blur_radius.setter
    def blur_radius(self, blur_radius):
        """Sets the blur_radius of this ReflectionEffect.

        blur radius  # noqa: E501

        :param blur_radius: The blur_radius of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._blur_radius = blur_radius

    @property
    def scale_horizontal(self):
        """Gets the scale_horizontal of this ReflectionEffect.  # noqa: E501

        scale horizontal  # noqa: E501

        :return: The scale_horizontal of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._scale_horizontal

    @scale_horizontal.setter
    def scale_horizontal(self, scale_horizontal):
        """Sets the scale_horizontal of this ReflectionEffect.

        scale horizontal  # noqa: E501

        :param scale_horizontal: The scale_horizontal of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._scale_horizontal = scale_horizontal

    @property
    def scale_vertical(self):
        """Gets the scale_vertical of this ReflectionEffect.  # noqa: E501

        scale vertical  # noqa: E501

        :return: The scale_vertical of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._scale_vertical

    @scale_vertical.setter
    def scale_vertical(self, scale_vertical):
        """Sets the scale_vertical of this ReflectionEffect.

        scale vertical  # noqa: E501

        :param scale_vertical: The scale_vertical of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._scale_vertical = scale_vertical

    @property
    def skew_horizontal(self):
        """Gets the skew_horizontal of this ReflectionEffect.  # noqa: E501

        skew horizontal  # noqa: E501

        :return: The skew_horizontal of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._skew_horizontal

    @skew_horizontal.setter
    def skew_horizontal(self, skew_horizontal):
        """Sets the skew_horizontal of this ReflectionEffect.

        skew horizontal  # noqa: E501

        :param skew_horizontal: The skew_horizontal of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._skew_horizontal = skew_horizontal

    @property
    def skew_vertical(self):
        """Gets the skew_vertical of this ReflectionEffect.  # noqa: E501

        skew vertical  # noqa: E501

        :return: The skew_vertical of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._skew_vertical

    @skew_vertical.setter
    def skew_vertical(self, skew_vertical):
        """Sets the skew_vertical of this ReflectionEffect.

        skew vertical  # noqa: E501

        :param skew_vertical: The skew_vertical of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._skew_vertical = skew_vertical

    @property
    def start_pos_alpha(self):
        """Gets the start_pos_alpha of this ReflectionEffect.  # noqa: E501

        start pos alpha  # noqa: E501

        :return: The start_pos_alpha of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._start_pos_alpha

    @start_pos_alpha.setter
    def start_pos_alpha(self, start_pos_alpha):
        """Sets the start_pos_alpha of this ReflectionEffect.

        start pos alpha  # noqa: E501

        :param start_pos_alpha: The start_pos_alpha of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._start_pos_alpha = start_pos_alpha

    @property
    def end_pos_alpha(self):
        """Gets the end_pos_alpha of this ReflectionEffect.  # noqa: E501

        end pos alpha  # noqa: E501

        :return: The end_pos_alpha of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._end_pos_alpha

    @end_pos_alpha.setter
    def end_pos_alpha(self, end_pos_alpha):
        """Sets the end_pos_alpha of this ReflectionEffect.

        end pos alpha  # noqa: E501

        :param end_pos_alpha: The end_pos_alpha of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._end_pos_alpha = end_pos_alpha

    @property
    def start_reflection_opacity(self):
        """Gets the start_reflection_opacity of this ReflectionEffect.  # noqa: E501

        start reflection opacity  # noqa: E501

        :return: The start_reflection_opacity of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._start_reflection_opacity

    @start_reflection_opacity.setter
    def start_reflection_opacity(self, start_reflection_opacity):
        """Sets the start_reflection_opacity of this ReflectionEffect.

        start reflection opacity  # noqa: E501

        :param start_reflection_opacity: The start_reflection_opacity of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._start_reflection_opacity = start_reflection_opacity

    @property
    def end_reflection_opacity(self):
        """Gets the end_reflection_opacity of this ReflectionEffect.  # noqa: E501

        end reflection opacity  # noqa: E501

        :return: The end_reflection_opacity of this ReflectionEffect.  # noqa: E501
        :rtype: float
        """
        return self._end_reflection_opacity

    @end_reflection_opacity.setter
    def end_reflection_opacity(self, end_reflection_opacity):
        """Sets the end_reflection_opacity of this ReflectionEffect.

        end reflection opacity  # noqa: E501

        :param end_reflection_opacity: The end_reflection_opacity of this ReflectionEffect.  # noqa: E501
        :type: float
        """
        self._end_reflection_opacity = end_reflection_opacity

    @property
    def rectangle_align(self):
        """Gets the rectangle_align of this ReflectionEffect.  # noqa: E501

        rectangle alignment  # noqa: E501

        :return: The rectangle_align of this ReflectionEffect.  # noqa: E501
        :rtype: str
        """
        return self._rectangle_align

    @rectangle_align.setter
    def rectangle_align(self, rectangle_align):
        """Sets the rectangle_align of this ReflectionEffect.

        rectangle alignment  # noqa: E501

        :param rectangle_align: The rectangle_align of this ReflectionEffect.  # noqa: E501
        :type: str
        """
        if rectangle_align is not None:
            allowed_values = ["TopLeft", "Top", "TopRight", "Left", "Center", "Right", "BottomLeft", "Bottom", "BottomRight", "NotDefined"]  # noqa: E501
            if rectangle_align not in allowed_values:
                raise ValueError(
                    "Invalid value for `rectangle_align` ({0}), must be one of {1}"  # noqa: E501
                    .format(rectangle_align, allowed_values)
                )
        self._rectangle_align = rectangle_align

    @property
    def rotate_shadow_with_shape(self):
        """Gets the rotate_shadow_with_shape of this ReflectionEffect.  # noqa: E501

        true if the reflection should rotate with the shape when the shape is rotated  # noqa: E501

        :return: The rotate_shadow_with_shape of this ReflectionEffect.  # noqa: E501
        :rtype: bool
        """
        return self._rotate_shadow_with_shape

    @rotate_shadow_with_shape.setter
    def rotate_shadow_with_shape(self, rotate_shadow_with_shape):
        """Sets the rotate_shadow_with_shape of this ReflectionEffect.

        true if the reflection should rotate with the shape when the shape is rotated  # noqa: E501

        :param rotate_shadow_with_shape: The rotate_shadow_with_shape of this ReflectionEffect.  # noqa: E501
        :type: bool
        """
        self._rotate_shadow_with_shape = rotate_shadow_with_shape

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
        if not isinstance(other, ReflectionEffect):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
