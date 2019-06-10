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


class ResourceBase(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'self_uri': 'ResourceUri',
        'alternate_links': 'list[ResourceUri]'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks'
    }

    def __init__(self, self_uri=None, alternate_links=None):  # noqa: E501
        """ResourceBase - a model defined in Swagger"""  # noqa: E501

        self._self_uri = None
        self._alternate_links = None

        if self_uri is not None:
            self.self_uri = self_uri
        if alternate_links is not None:
            self.alternate_links = alternate_links

    @property
    def self_uri(self):
        """Gets the self_uri of this ResourceBase.  # noqa: E501

        Gets or sets the link to this resource.  # noqa: E501

        :return: The self_uri of this ResourceBase.  # noqa: E501
        :rtype: ResourceUri
        """
        return self._self_uri

    @self_uri.setter
    def self_uri(self, self_uri):
        """Sets the self_uri of this ResourceBase.

        Gets or sets the link to this resource.  # noqa: E501

        :param self_uri: The self_uri of this ResourceBase.  # noqa: E501
        :type: ResourceUri
        """
        self._self_uri = self_uri

    @property
    def alternate_links(self):
        """Gets the alternate_links of this ResourceBase.  # noqa: E501


        :return: The alternate_links of this ResourceBase.  # noqa: E501
        :rtype: list[ResourceUri]
        """
        return self._alternate_links

    @alternate_links.setter
    def alternate_links(self, alternate_links):
        """Sets the alternate_links of this ResourceBase.


        :param alternate_links: The alternate_links of this ResourceBase.  # noqa: E501
        :type: list[ResourceUri]
        """
        self._alternate_links = alternate_links

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
        if not isinstance(other, ResourceBase):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
