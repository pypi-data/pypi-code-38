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

class ColorScheme(ResourceBase):


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
        'accent1': 'str',
        'accent2': 'str',
        'accent3': 'str',
        'accent4': 'str',
        'accent5': 'str',
        'accent6': 'str',
        'dark1': 'str',
        'dark2': 'str',
        'followed_hyperlink': 'str',
        'hyperlink': 'str',
        'light1': 'str',
        'light2': 'str'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'accent1': 'Accent1',
        'accent2': 'Accent2',
        'accent3': 'Accent3',
        'accent4': 'Accent4',
        'accent5': 'Accent5',
        'accent6': 'Accent6',
        'dark1': 'Dark1',
        'dark2': 'Dark2',
        'followed_hyperlink': 'FollowedHyperlink',
        'hyperlink': 'Hyperlink',
        'light1': 'Light1',
        'light2': 'Light2'
    }

    def __init__(self, self_uri=None, alternate_links=None, accent1=None, accent2=None, accent3=None, accent4=None, accent5=None, accent6=None, dark1=None, dark2=None, followed_hyperlink=None, hyperlink=None, light1=None, light2=None):  # noqa: E501
        """ColorScheme - a model defined in Swagger"""  # noqa: E501
        super(ColorScheme, self).__init__(self_uri, alternate_links)

        self._accent1 = None
        self._accent2 = None
        self._accent3 = None
        self._accent4 = None
        self._accent5 = None
        self._accent6 = None
        self._dark1 = None
        self._dark2 = None
        self._followed_hyperlink = None
        self._hyperlink = None
        self._light1 = None
        self._light2 = None

        if accent1 is not None:
            self.accent1 = accent1
        if accent2 is not None:
            self.accent2 = accent2
        if accent3 is not None:
            self.accent3 = accent3
        if accent4 is not None:
            self.accent4 = accent4
        if accent5 is not None:
            self.accent5 = accent5
        if accent6 is not None:
            self.accent6 = accent6
        if dark1 is not None:
            self.dark1 = dark1
        if dark2 is not None:
            self.dark2 = dark2
        if followed_hyperlink is not None:
            self.followed_hyperlink = followed_hyperlink
        if hyperlink is not None:
            self.hyperlink = hyperlink
        if light1 is not None:
            self.light1 = light1
        if light2 is not None:
            self.light2 = light2

    @property
    def accent1(self):
        """Gets the accent1 of this ColorScheme.  # noqa: E501


        :return: The accent1 of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._accent1

    @accent1.setter
    def accent1(self, accent1):
        """Sets the accent1 of this ColorScheme.


        :param accent1: The accent1 of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._accent1 = accent1

    @property
    def accent2(self):
        """Gets the accent2 of this ColorScheme.  # noqa: E501


        :return: The accent2 of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._accent2

    @accent2.setter
    def accent2(self, accent2):
        """Sets the accent2 of this ColorScheme.


        :param accent2: The accent2 of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._accent2 = accent2

    @property
    def accent3(self):
        """Gets the accent3 of this ColorScheme.  # noqa: E501


        :return: The accent3 of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._accent3

    @accent3.setter
    def accent3(self, accent3):
        """Sets the accent3 of this ColorScheme.


        :param accent3: The accent3 of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._accent3 = accent3

    @property
    def accent4(self):
        """Gets the accent4 of this ColorScheme.  # noqa: E501


        :return: The accent4 of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._accent4

    @accent4.setter
    def accent4(self, accent4):
        """Sets the accent4 of this ColorScheme.


        :param accent4: The accent4 of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._accent4 = accent4

    @property
    def accent5(self):
        """Gets the accent5 of this ColorScheme.  # noqa: E501


        :return: The accent5 of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._accent5

    @accent5.setter
    def accent5(self, accent5):
        """Sets the accent5 of this ColorScheme.


        :param accent5: The accent5 of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._accent5 = accent5

    @property
    def accent6(self):
        """Gets the accent6 of this ColorScheme.  # noqa: E501


        :return: The accent6 of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._accent6

    @accent6.setter
    def accent6(self, accent6):
        """Sets the accent6 of this ColorScheme.


        :param accent6: The accent6 of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._accent6 = accent6

    @property
    def dark1(self):
        """Gets the dark1 of this ColorScheme.  # noqa: E501


        :return: The dark1 of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._dark1

    @dark1.setter
    def dark1(self, dark1):
        """Sets the dark1 of this ColorScheme.


        :param dark1: The dark1 of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._dark1 = dark1

    @property
    def dark2(self):
        """Gets the dark2 of this ColorScheme.  # noqa: E501


        :return: The dark2 of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._dark2

    @dark2.setter
    def dark2(self, dark2):
        """Sets the dark2 of this ColorScheme.


        :param dark2: The dark2 of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._dark2 = dark2

    @property
    def followed_hyperlink(self):
        """Gets the followed_hyperlink of this ColorScheme.  # noqa: E501


        :return: The followed_hyperlink of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._followed_hyperlink

    @followed_hyperlink.setter
    def followed_hyperlink(self, followed_hyperlink):
        """Sets the followed_hyperlink of this ColorScheme.


        :param followed_hyperlink: The followed_hyperlink of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._followed_hyperlink = followed_hyperlink

    @property
    def hyperlink(self):
        """Gets the hyperlink of this ColorScheme.  # noqa: E501


        :return: The hyperlink of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._hyperlink

    @hyperlink.setter
    def hyperlink(self, hyperlink):
        """Sets the hyperlink of this ColorScheme.


        :param hyperlink: The hyperlink of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._hyperlink = hyperlink

    @property
    def light1(self):
        """Gets the light1 of this ColorScheme.  # noqa: E501


        :return: The light1 of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._light1

    @light1.setter
    def light1(self, light1):
        """Sets the light1 of this ColorScheme.


        :param light1: The light1 of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._light1 = light1

    @property
    def light2(self):
        """Gets the light2 of this ColorScheme.  # noqa: E501


        :return: The light2 of this ColorScheme.  # noqa: E501
        :rtype: str
        """
        return self._light2

    @light2.setter
    def light2(self, light2):
        """Sets the light2 of this ColorScheme.


        :param light2: The light2 of this ColorScheme.  # noqa: E501
        :type: str
        """
        self._light2 = light2

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
        if not isinstance(other, ColorScheme):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
