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

class MasterSlide(ResourceBase):


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
        'name': 'str',
        'layout_slides': 'list[ResourceUriElement]',
        'depending_slides': 'list[ResourceUriElement]'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'name': 'Name',
        'layout_slides': 'LayoutSlides',
        'depending_slides': 'DependingSlides'
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, layout_slides=None, depending_slides=None):  # noqa: E501
        """MasterSlide - a model defined in Swagger"""  # noqa: E501
        super(MasterSlide, self).__init__(self_uri, alternate_links)

        self._name = None
        self._layout_slides = None
        self._depending_slides = None

        if name is not None:
            self.name = name
        if layout_slides is not None:
            self.layout_slides = layout_slides
        if depending_slides is not None:
            self.depending_slides = depending_slides

    @property
    def name(self):
        """Gets the name of this MasterSlide.  # noqa: E501


        :return: The name of this MasterSlide.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this MasterSlide.


        :param name: The name of this MasterSlide.  # noqa: E501
        :type: str
        """
        self._name = name

    @property
    def layout_slides(self):
        """Gets the layout_slides of this MasterSlide.  # noqa: E501


        :return: The layout_slides of this MasterSlide.  # noqa: E501
        :rtype: list[ResourceUriElement]
        """
        return self._layout_slides

    @layout_slides.setter
    def layout_slides(self, layout_slides):
        """Sets the layout_slides of this MasterSlide.


        :param layout_slides: The layout_slides of this MasterSlide.  # noqa: E501
        :type: list[ResourceUriElement]
        """
        self._layout_slides = layout_slides

    @property
    def depending_slides(self):
        """Gets the depending_slides of this MasterSlide.  # noqa: E501


        :return: The depending_slides of this MasterSlide.  # noqa: E501
        :rtype: list[ResourceUriElement]
        """
        return self._depending_slides

    @depending_slides.setter
    def depending_slides(self, depending_slides):
        """Sets the depending_slides of this MasterSlide.


        :param depending_slides: The depending_slides of this MasterSlide.  # noqa: E501
        :type: list[ResourceUriElement]
        """
        self._depending_slides = depending_slides

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
        if not isinstance(other, MasterSlide):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
