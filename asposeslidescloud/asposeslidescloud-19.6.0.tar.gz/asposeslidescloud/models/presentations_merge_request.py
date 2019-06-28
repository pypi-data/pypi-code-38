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


class PresentationsMergeRequest(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'presentation_paths': 'list[str]',
        'presentation_passwords': 'list[str]'
    }

    attribute_map = {
        'presentation_paths': 'PresentationPaths',
        'presentation_passwords': 'PresentationPasswords'
    }

    def __init__(self, presentation_paths=None, presentation_passwords=None):  # noqa: E501
        """PresentationsMergeRequest - a model defined in Swagger"""  # noqa: E501

        self._presentation_paths = None
        self._presentation_passwords = None

        if presentation_paths is not None:
            self.presentation_paths = presentation_paths
        if presentation_passwords is not None:
            self.presentation_passwords = presentation_passwords

    @property
    def presentation_paths(self):
        """Gets the presentation_paths of this PresentationsMergeRequest.  # noqa: E501

        Gets or sets the presentation paths.  # noqa: E501

        :return: The presentation_paths of this PresentationsMergeRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._presentation_paths

    @presentation_paths.setter
    def presentation_paths(self, presentation_paths):
        """Sets the presentation_paths of this PresentationsMergeRequest.

        Gets or sets the presentation paths.  # noqa: E501

        :param presentation_paths: The presentation_paths of this PresentationsMergeRequest.  # noqa: E501
        :type: list[str]
        """
        self._presentation_paths = presentation_paths

    @property
    def presentation_passwords(self):
        """Gets the presentation_passwords of this PresentationsMergeRequest.  # noqa: E501

        Gets or sets the presentation passwords.  # noqa: E501

        :return: The presentation_passwords of this PresentationsMergeRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._presentation_passwords

    @presentation_passwords.setter
    def presentation_passwords(self, presentation_passwords):
        """Sets the presentation_passwords of this PresentationsMergeRequest.

        Gets or sets the presentation passwords.  # noqa: E501

        :param presentation_passwords: The presentation_passwords of this PresentationsMergeRequest.  # noqa: E501
        :type: list[str]
        """
        self._presentation_passwords = presentation_passwords

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
        if not isinstance(other, PresentationsMergeRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
