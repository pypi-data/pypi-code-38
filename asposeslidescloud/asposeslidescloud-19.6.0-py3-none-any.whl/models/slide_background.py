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

class SlideBackground(ResourceBase):


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
        'type': 'str',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'type': 'Type',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat'
    }

    def __init__(self, self_uri=None, alternate_links=None, type=None, fill_format=None, effect_format=None):  # noqa: E501
        """SlideBackground - a model defined in Swagger"""  # noqa: E501
        super(SlideBackground, self).__init__(self_uri, alternate_links)

        self._type = None
        self._fill_format = None
        self._effect_format = None

        self.type = type
        if fill_format is not None:
            self.fill_format = fill_format
        if effect_format is not None:
            self.effect_format = effect_format

    @property
    def type(self):
        """Gets the type of this SlideBackground.  # noqa: E501


        :return: The type of this SlideBackground.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this SlideBackground.


        :param type: The type of this SlideBackground.  # noqa: E501
        :type: str
        """
        if type is not None:
            allowed_values = ["NoFill", "Solid", "Gradient", "Pattern", "Picture", "NotDefined"]  # noqa: E501
            if type not in allowed_values:
                raise ValueError(
                    "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                    .format(type, allowed_values)
                )
        self._type = type

    @property
    def fill_format(self):
        """Gets the fill_format of this SlideBackground.  # noqa: E501


        :return: The fill_format of this SlideBackground.  # noqa: E501
        :rtype: FillFormat
        """
        return self._fill_format

    @fill_format.setter
    def fill_format(self, fill_format):
        """Sets the fill_format of this SlideBackground.


        :param fill_format: The fill_format of this SlideBackground.  # noqa: E501
        :type: FillFormat
        """
        self._fill_format = fill_format

    @property
    def effect_format(self):
        """Gets the effect_format of this SlideBackground.  # noqa: E501


        :return: The effect_format of this SlideBackground.  # noqa: E501
        :rtype: EffectFormat
        """
        return self._effect_format

    @effect_format.setter
    def effect_format(self, effect_format):
        """Sets the effect_format of this SlideBackground.


        :param effect_format: The effect_format of this SlideBackground.  # noqa: E501
        :type: EffectFormat
        """
        self._effect_format = effect_format

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
        if not isinstance(other, SlideBackground):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
