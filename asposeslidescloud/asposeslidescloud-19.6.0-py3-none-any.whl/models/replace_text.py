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

class ReplaceText(Task):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'old_text': 'str',
        'new_text': 'str',
        'ignore_case': 'bool',
        'slide_position': 'int'
    }

    attribute_map = {
        'type': 'Type',
        'old_text': 'OldText',
        'new_text': 'NewText',
        'ignore_case': 'IgnoreCase',
        'slide_position': 'SlidePosition'
    }

    def __init__(self, type='ReplaceText', old_text=None, new_text=None, ignore_case=None, slide_position=None):  # noqa: E501
        """ReplaceText - a model defined in Swagger"""  # noqa: E501
        super(ReplaceText, self).__init__(type)

        self._old_text = None
        self._new_text = None
        self._ignore_case = None
        self._slide_position = None

        if old_text is not None:
            self.old_text = old_text
        if new_text is not None:
            self.new_text = new_text
        self.ignore_case = ignore_case
        self.slide_position = slide_position

    @property
    def old_text(self):
        """Gets the old_text of this ReplaceText.  # noqa: E501

        Text to be replaced.  # noqa: E501

        :return: The old_text of this ReplaceText.  # noqa: E501
        :rtype: str
        """
        return self._old_text

    @old_text.setter
    def old_text(self, old_text):
        """Sets the old_text of this ReplaceText.

        Text to be replaced.  # noqa: E501

        :param old_text: The old_text of this ReplaceText.  # noqa: E501
        :type: str
        """
        self._old_text = old_text

    @property
    def new_text(self):
        """Gets the new_text of this ReplaceText.  # noqa: E501

        Text to replace with.  # noqa: E501

        :return: The new_text of this ReplaceText.  # noqa: E501
        :rtype: str
        """
        return self._new_text

    @new_text.setter
    def new_text(self, new_text):
        """Sets the new_text of this ReplaceText.

        Text to replace with.  # noqa: E501

        :param new_text: The new_text of this ReplaceText.  # noqa: E501
        :type: str
        """
        self._new_text = new_text

    @property
    def ignore_case(self):
        """Gets the ignore_case of this ReplaceText.  # noqa: E501

        True to ignore case in replace pattern search.  # noqa: E501

        :return: The ignore_case of this ReplaceText.  # noqa: E501
        :rtype: bool
        """
        return self._ignore_case

    @ignore_case.setter
    def ignore_case(self, ignore_case):
        """Sets the ignore_case of this ReplaceText.

        True to ignore case in replace pattern search.  # noqa: E501

        :param ignore_case: The ignore_case of this ReplaceText.  # noqa: E501
        :type: bool
        """
        self._ignore_case = ignore_case

    @property
    def slide_position(self):
        """Gets the slide_position of this ReplaceText.  # noqa: E501

        One-based position of the slide to perform the replace in. 0 to make the replace throughout the presentation.  # noqa: E501

        :return: The slide_position of this ReplaceText.  # noqa: E501
        :rtype: int
        """
        return self._slide_position

    @slide_position.setter
    def slide_position(self, slide_position):
        """Sets the slide_position of this ReplaceText.

        One-based position of the slide to perform the replace in. 0 to make the replace throughout the presentation.  # noqa: E501

        :param slide_position: The slide_position of this ReplaceText.  # noqa: E501
        :type: int
        """
        self._slide_position = slide_position

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
        if not isinstance(other, ReplaceText):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
