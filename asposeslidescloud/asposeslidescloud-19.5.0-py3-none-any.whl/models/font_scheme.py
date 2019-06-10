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

class FontScheme(ResourceBase):


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
        'major': 'FontSet',
        'minor': 'FontSet',
        'name': 'str'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'major': 'Major',
        'minor': 'Minor',
        'name': 'Name'
    }

    def __init__(self, self_uri=None, alternate_links=None, major=None, minor=None, name=None):  # noqa: E501
        """FontScheme - a model defined in Swagger"""  # noqa: E501
        super(FontScheme, self).__init__(self_uri, alternate_links)

        self._major = None
        self._minor = None
        self._name = None

        if major is not None:
            self.major = major
        if minor is not None:
            self.minor = minor
        if name is not None:
            self.name = name

    @property
    def major(self):
        """Gets the major of this FontScheme.  # noqa: E501

        Gets or sets fonts collection for a \"heading\" part of the slide.  # noqa: E501

        :return: The major of this FontScheme.  # noqa: E501
        :rtype: FontSet
        """
        return self._major

    @major.setter
    def major(self, major):
        """Sets the major of this FontScheme.

        Gets or sets fonts collection for a \"heading\" part of the slide.  # noqa: E501

        :param major: The major of this FontScheme.  # noqa: E501
        :type: FontSet
        """
        self._major = major

    @property
    def minor(self):
        """Gets the minor of this FontScheme.  # noqa: E501

        Gets or sets  the fonts collection for a \"body\" part of the slide.  # noqa: E501

        :return: The minor of this FontScheme.  # noqa: E501
        :rtype: FontSet
        """
        return self._minor

    @minor.setter
    def minor(self, minor):
        """Sets the minor of this FontScheme.

        Gets or sets  the fonts collection for a \"body\" part of the slide.  # noqa: E501

        :param minor: The minor of this FontScheme.  # noqa: E501
        :type: FontSet
        """
        self._minor = minor

    @property
    def name(self):
        """Gets the name of this FontScheme.  # noqa: E501

        Gets or sets the name.  # noqa: E501

        :return: The name of this FontScheme.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this FontScheme.

        Gets or sets the name.  # noqa: E501

        :param name: The name of this FontScheme.  # noqa: E501
        :type: str
        """
        self._name = name

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
        if not isinstance(other, FontScheme):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
