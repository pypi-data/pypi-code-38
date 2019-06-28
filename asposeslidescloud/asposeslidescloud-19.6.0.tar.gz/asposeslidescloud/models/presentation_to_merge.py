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


class PresentationToMerge(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'path': 'str',
        'password': 'str',
        'slides': 'list[int]'
    }

    attribute_map = {
        'path': 'Path',
        'password': 'Password',
        'slides': 'Slides'
    }

    def __init__(self, path=None, password=None, slides=None):  # noqa: E501
        """PresentationToMerge - a model defined in Swagger"""  # noqa: E501

        self._path = None
        self._password = None
        self._slides = None

        if path is not None:
            self.path = path
        if password is not None:
            self.password = password
        if slides is not None:
            self.slides = slides

    @property
    def path(self):
        """Gets the path of this PresentationToMerge.  # noqa: E501

        Get or sets the presentation path  # noqa: E501

        :return: The path of this PresentationToMerge.  # noqa: E501
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this PresentationToMerge.

        Get or sets the presentation path  # noqa: E501

        :param path: The path of this PresentationToMerge.  # noqa: E501
        :type: str
        """
        self._path = path

    @property
    def password(self):
        """Gets the password of this PresentationToMerge.  # noqa: E501

        Get or sets the presentation password  # noqa: E501

        :return: The password of this PresentationToMerge.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this PresentationToMerge.

        Get or sets the presentation password  # noqa: E501

        :param password: The password of this PresentationToMerge.  # noqa: E501
        :type: str
        """
        self._password = password

    @property
    def slides(self):
        """Gets the slides of this PresentationToMerge.  # noqa: E501

        Get or sets the indexes of slides to merge  # noqa: E501

        :return: The slides of this PresentationToMerge.  # noqa: E501
        :rtype: list[int]
        """
        return self._slides

    @slides.setter
    def slides(self, slides):
        """Sets the slides of this PresentationToMerge.

        Get or sets the indexes of slides to merge  # noqa: E501

        :param slides: The slides of this PresentationToMerge.  # noqa: E501
        :type: list[int]
        """
        self._slides = slides

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
        if not isinstance(other, PresentationToMerge):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
