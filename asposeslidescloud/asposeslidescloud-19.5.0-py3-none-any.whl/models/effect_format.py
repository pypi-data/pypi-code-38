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


class EffectFormat(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'blur': 'BlurEffect',
        'glow': 'GlowEffect',
        'inner_shadow': 'InnerShadowEffect',
        'outer_shadow': 'OuterShadowEffect',
        'preset_shadow': 'PresetShadowEffect',
        'soft_edge': 'SoftEdgeEffect',
        'reflection': 'ReflectionEffect',
        'fill_overlay': 'FillOverlayEffect'
    }

    attribute_map = {
        'blur': 'Blur',
        'glow': 'Glow',
        'inner_shadow': 'InnerShadow',
        'outer_shadow': 'OuterShadow',
        'preset_shadow': 'PresetShadow',
        'soft_edge': 'SoftEdge',
        'reflection': 'Reflection',
        'fill_overlay': 'FillOverlay'
    }

    def __init__(self, blur=None, glow=None, inner_shadow=None, outer_shadow=None, preset_shadow=None, soft_edge=None, reflection=None, fill_overlay=None):  # noqa: E501
        """EffectFormat - a model defined in Swagger"""  # noqa: E501

        self._blur = None
        self._glow = None
        self._inner_shadow = None
        self._outer_shadow = None
        self._preset_shadow = None
        self._soft_edge = None
        self._reflection = None
        self._fill_overlay = None

        if blur is not None:
            self.blur = blur
        if glow is not None:
            self.glow = glow
        if inner_shadow is not None:
            self.inner_shadow = inner_shadow
        if outer_shadow is not None:
            self.outer_shadow = outer_shadow
        if preset_shadow is not None:
            self.preset_shadow = preset_shadow
        if soft_edge is not None:
            self.soft_edge = soft_edge
        if reflection is not None:
            self.reflection = reflection
        if fill_overlay is not None:
            self.fill_overlay = fill_overlay

    @property
    def blur(self):
        """Gets the blur of this EffectFormat.  # noqa: E501

        blur effect  # noqa: E501

        :return: The blur of this EffectFormat.  # noqa: E501
        :rtype: BlurEffect
        """
        return self._blur

    @blur.setter
    def blur(self, blur):
        """Sets the blur of this EffectFormat.

        blur effect  # noqa: E501

        :param blur: The blur of this EffectFormat.  # noqa: E501
        :type: BlurEffect
        """
        self._blur = blur

    @property
    def glow(self):
        """Gets the glow of this EffectFormat.  # noqa: E501

        glow effect  # noqa: E501

        :return: The glow of this EffectFormat.  # noqa: E501
        :rtype: GlowEffect
        """
        return self._glow

    @glow.setter
    def glow(self, glow):
        """Sets the glow of this EffectFormat.

        glow effect  # noqa: E501

        :param glow: The glow of this EffectFormat.  # noqa: E501
        :type: GlowEffect
        """
        self._glow = glow

    @property
    def inner_shadow(self):
        """Gets the inner_shadow of this EffectFormat.  # noqa: E501

        inner shadow effect  # noqa: E501

        :return: The inner_shadow of this EffectFormat.  # noqa: E501
        :rtype: InnerShadowEffect
        """
        return self._inner_shadow

    @inner_shadow.setter
    def inner_shadow(self, inner_shadow):
        """Sets the inner_shadow of this EffectFormat.

        inner shadow effect  # noqa: E501

        :param inner_shadow: The inner_shadow of this EffectFormat.  # noqa: E501
        :type: InnerShadowEffect
        """
        self._inner_shadow = inner_shadow

    @property
    def outer_shadow(self):
        """Gets the outer_shadow of this EffectFormat.  # noqa: E501

        outer shadow effect  # noqa: E501

        :return: The outer_shadow of this EffectFormat.  # noqa: E501
        :rtype: OuterShadowEffect
        """
        return self._outer_shadow

    @outer_shadow.setter
    def outer_shadow(self, outer_shadow):
        """Sets the outer_shadow of this EffectFormat.

        outer shadow effect  # noqa: E501

        :param outer_shadow: The outer_shadow of this EffectFormat.  # noqa: E501
        :type: OuterShadowEffect
        """
        self._outer_shadow = outer_shadow

    @property
    def preset_shadow(self):
        """Gets the preset_shadow of this EffectFormat.  # noqa: E501

        preset shadow effect  # noqa: E501

        :return: The preset_shadow of this EffectFormat.  # noqa: E501
        :rtype: PresetShadowEffect
        """
        return self._preset_shadow

    @preset_shadow.setter
    def preset_shadow(self, preset_shadow):
        """Sets the preset_shadow of this EffectFormat.

        preset shadow effect  # noqa: E501

        :param preset_shadow: The preset_shadow of this EffectFormat.  # noqa: E501
        :type: PresetShadowEffect
        """
        self._preset_shadow = preset_shadow

    @property
    def soft_edge(self):
        """Gets the soft_edge of this EffectFormat.  # noqa: E501

        soft edge effect  # noqa: E501

        :return: The soft_edge of this EffectFormat.  # noqa: E501
        :rtype: SoftEdgeEffect
        """
        return self._soft_edge

    @soft_edge.setter
    def soft_edge(self, soft_edge):
        """Sets the soft_edge of this EffectFormat.

        soft edge effect  # noqa: E501

        :param soft_edge: The soft_edge of this EffectFormat.  # noqa: E501
        :type: SoftEdgeEffect
        """
        self._soft_edge = soft_edge

    @property
    def reflection(self):
        """Gets the reflection of this EffectFormat.  # noqa: E501

        reflection effect  # noqa: E501

        :return: The reflection of this EffectFormat.  # noqa: E501
        :rtype: ReflectionEffect
        """
        return self._reflection

    @reflection.setter
    def reflection(self, reflection):
        """Sets the reflection of this EffectFormat.

        reflection effect  # noqa: E501

        :param reflection: The reflection of this EffectFormat.  # noqa: E501
        :type: ReflectionEffect
        """
        self._reflection = reflection

    @property
    def fill_overlay(self):
        """Gets the fill_overlay of this EffectFormat.  # noqa: E501

        fill overlay effect  # noqa: E501

        :return: The fill_overlay of this EffectFormat.  # noqa: E501
        :rtype: FillOverlayEffect
        """
        return self._fill_overlay

    @fill_overlay.setter
    def fill_overlay(self, fill_overlay):
        """Sets the fill_overlay of this EffectFormat.

        fill overlay effect  # noqa: E501

        :param fill_overlay: The fill_overlay of this EffectFormat.  # noqa: E501
        :type: FillOverlayEffect
        """
        self._fill_overlay = fill_overlay

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
        if not isinstance(other, EffectFormat):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
