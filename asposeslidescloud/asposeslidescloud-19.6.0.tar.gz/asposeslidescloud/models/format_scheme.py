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

from asposeslidescloud.models.resource_base import ResourceBase

class FormatScheme(ResourceBase):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'self_uri': 'ResourceUri',
        'alternate_links': 'list[ResourceUri]',
        'background_styles': 'list[ResourceUri]',
        'effect_styles': 'list[ResourceUri]',
        'fill_styles': 'list[ResourceUri]',
        'line_styles': 'list[ResourceUri]'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'background_styles': 'BackgroundStyles',
        'effect_styles': 'EffectStyles',
        'fill_styles': 'FillStyles',
        'line_styles': 'LineStyles'
    }

    def __init__(self, self_uri=None, alternate_links=None, background_styles=None, effect_styles=None, fill_styles=None, line_styles=None):  # noqa: E501
        """FormatScheme - a model defined in Swagger"""  # noqa: E501
        super(FormatScheme, self).__init__(self_uri, alternate_links)

        self._background_styles = None
        self._effect_styles = None
        self._fill_styles = None
        self._line_styles = None

        if background_styles is not None:
            self.background_styles = background_styles
        if effect_styles is not None:
            self.effect_styles = effect_styles
        if fill_styles is not None:
            self.fill_styles = fill_styles
        if line_styles is not None:
            self.line_styles = line_styles

    @property
    def background_styles(self):
        """Gets the background_styles of this FormatScheme.  # noqa: E501


        :return: The background_styles of this FormatScheme.  # noqa: E501
        :rtype: list[ResourceUri]
        """
        return self._background_styles

    @background_styles.setter
    def background_styles(self, background_styles):
        """Sets the background_styles of this FormatScheme.


        :param background_styles: The background_styles of this FormatScheme.  # noqa: E501
        :type: list[ResourceUri]
        """
        self._background_styles = background_styles

    @property
    def effect_styles(self):
        """Gets the effect_styles of this FormatScheme.  # noqa: E501


        :return: The effect_styles of this FormatScheme.  # noqa: E501
        :rtype: list[ResourceUri]
        """
        return self._effect_styles

    @effect_styles.setter
    def effect_styles(self, effect_styles):
        """Sets the effect_styles of this FormatScheme.


        :param effect_styles: The effect_styles of this FormatScheme.  # noqa: E501
        :type: list[ResourceUri]
        """
        self._effect_styles = effect_styles

    @property
    def fill_styles(self):
        """Gets the fill_styles of this FormatScheme.  # noqa: E501


        :return: The fill_styles of this FormatScheme.  # noqa: E501
        :rtype: list[ResourceUri]
        """
        return self._fill_styles

    @fill_styles.setter
    def fill_styles(self, fill_styles):
        """Sets the fill_styles of this FormatScheme.


        :param fill_styles: The fill_styles of this FormatScheme.  # noqa: E501
        :type: list[ResourceUri]
        """
        self._fill_styles = fill_styles

    @property
    def line_styles(self):
        """Gets the line_styles of this FormatScheme.  # noqa: E501


        :return: The line_styles of this FormatScheme.  # noqa: E501
        :rtype: list[ResourceUri]
        """
        return self._line_styles

    @line_styles.setter
    def line_styles(self, line_styles):
        """Sets the line_styles of this FormatScheme.


        :param line_styles: The line_styles of this FormatScheme.  # noqa: E501
        :type: list[ResourceUri]
        """
        self._line_styles = line_styles

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
        if not isinstance(other, FormatScheme):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
