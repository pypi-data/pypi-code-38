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

from asposeslidescloud.models.task import Task

class AddMasterSlide(Task):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'clone_from_file': 'InputFile',
        'clone_from_position': 'int',
        'apply_to_all': 'bool'
    }

    attribute_map = {
        'type': 'Type',
        'clone_from_file': 'CloneFromFile',
        'clone_from_position': 'CloneFromPosition',
        'apply_to_all': 'ApplyToAll'
    }

    def __init__(self, type='AddMasterSlide', clone_from_file=None, clone_from_position=None, apply_to_all=None):  # noqa: E501
        """AddMasterSlide - a model defined in Swagger"""  # noqa: E501
        super(AddMasterSlide, self).__init__(type)

        self._clone_from_file = None
        self._clone_from_position = None
        self._apply_to_all = None

        if clone_from_file is not None:
            self.clone_from_file = clone_from_file
        self.clone_from_position = clone_from_position
        self.apply_to_all = apply_to_all

    @property
    def clone_from_file(self):
        """Gets the clone_from_file of this AddMasterSlide.  # noqa: E501

        Source presentation clone from.  # noqa: E501

        :return: The clone_from_file of this AddMasterSlide.  # noqa: E501
        :rtype: InputFile
        """
        return self._clone_from_file

    @clone_from_file.setter
    def clone_from_file(self, clone_from_file):
        """Sets the clone_from_file of this AddMasterSlide.

        Source presentation clone from.  # noqa: E501

        :param clone_from_file: The clone_from_file of this AddMasterSlide.  # noqa: E501
        :type: InputFile
        """
        self._clone_from_file = clone_from_file

    @property
    def clone_from_position(self):
        """Gets the clone_from_position of this AddMasterSlide.  # noqa: E501

        Index of slide to clone.  # noqa: E501

        :return: The clone_from_position of this AddMasterSlide.  # noqa: E501
        :rtype: int
        """
        return self._clone_from_position

    @clone_from_position.setter
    def clone_from_position(self, clone_from_position):
        """Sets the clone_from_position of this AddMasterSlide.

        Index of slide to clone.  # noqa: E501

        :param clone_from_position: The clone_from_position of this AddMasterSlide.  # noqa: E501
        :type: int
        """
        self._clone_from_position = clone_from_position

    @property
    def apply_to_all(self):
        """Gets the apply_to_all of this AddMasterSlide.  # noqa: E501

        True if cloned master slide is applied to all slides.  # noqa: E501

        :return: The apply_to_all of this AddMasterSlide.  # noqa: E501
        :rtype: bool
        """
        return self._apply_to_all

    @apply_to_all.setter
    def apply_to_all(self, apply_to_all):
        """Sets the apply_to_all of this AddMasterSlide.

        True if cloned master slide is applied to all slides.  # noqa: E501

        :param apply_to_all: The apply_to_all of this AddMasterSlide.  # noqa: E501
        :type: bool
        """
        self._apply_to_all = apply_to_all

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
        if not isinstance(other, AddMasterSlide):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
