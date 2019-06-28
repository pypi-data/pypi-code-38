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


class FontSet(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'complex_script': 'str',
        'east_asian': 'str',
        'latin': 'str'
    }

    attribute_map = {
        'complex_script': 'ComplexScript',
        'east_asian': 'EastAsian',
        'latin': 'Latin'
    }

    def __init__(self, complex_script=None, east_asian=None, latin=None):  # noqa: E501
        """FontSet - a model defined in Swagger"""  # noqa: E501

        self._complex_script = None
        self._east_asian = None
        self._latin = None

        if complex_script is not None:
            self.complex_script = complex_script
        if east_asian is not None:
            self.east_asian = east_asian
        if latin is not None:
            self.latin = latin

    @property
    def complex_script(self):
        """Gets the complex_script of this FontSet.  # noqa: E501


        :return: The complex_script of this FontSet.  # noqa: E501
        :rtype: str
        """
        return self._complex_script

    @complex_script.setter
    def complex_script(self, complex_script):
        """Sets the complex_script of this FontSet.


        :param complex_script: The complex_script of this FontSet.  # noqa: E501
        :type: str
        """
        self._complex_script = complex_script

    @property
    def east_asian(self):
        """Gets the east_asian of this FontSet.  # noqa: E501


        :return: The east_asian of this FontSet.  # noqa: E501
        :rtype: str
        """
        return self._east_asian

    @east_asian.setter
    def east_asian(self, east_asian):
        """Sets the east_asian of this FontSet.


        :param east_asian: The east_asian of this FontSet.  # noqa: E501
        :type: str
        """
        self._east_asian = east_asian

    @property
    def latin(self):
        """Gets the latin of this FontSet.  # noqa: E501


        :return: The latin of this FontSet.  # noqa: E501
        :rtype: str
        """
        return self._latin

    @latin.setter
    def latin(self, latin):
        """Sets the latin of this FontSet.


        :param latin: The latin of this FontSet.  # noqa: E501
        :type: str
        """
        self._latin = latin

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
        if not isinstance(other, FontSet):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
