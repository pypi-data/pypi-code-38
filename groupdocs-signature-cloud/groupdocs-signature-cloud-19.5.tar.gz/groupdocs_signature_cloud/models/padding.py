# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="Padding.py">
#   Copyright (c) 2003-2019 Aspose Pty Ltd
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

class Padding(object):
    """
    Represents padding or margin information associated with element
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'all': 'int',
        'left': 'int',
        'top': 'int',
        'right': 'int',
        'bottom': 'int'
    }

    attribute_map = {
        'all': 'All',
        'left': 'Left',
        'top': 'Top',
        'right': 'Right',
        'bottom': 'Bottom'
    }

    def __init__(self, all=None, left=None, top=None, right=None, bottom=None, **kwargs):  # noqa: E501
        """Initializes new instance of Padding"""  # noqa: E501

        self._all = None
        self._left = None
        self._top = None
        self._right = None
        self._bottom = None

        if all is not None:
            self.all = all
        if left is not None:
            self.left = left
        if top is not None:
            self.top = top
        if right is not None:
            self.right = right
        if bottom is not None:
            self.bottom = bottom
    
    @property
    def all(self):
        """
        Gets the all.  # noqa: E501

        Gets or sets the padding value for all the edges  # noqa: E501

        :return: The all.  # noqa: E501
        :rtype: int
        """
        return self._all

    @all.setter
    def all(self, all):
        """
        Sets the all.

        Gets or sets the padding value for all the edges  # noqa: E501

        :param all: The all.  # noqa: E501
        :type: int
        """
        if all is None:
            raise ValueError("Invalid value for `all`, must not be `None`")  # noqa: E501
        self._all = all
    
    @property
    def left(self):
        """
        Gets the left.  # noqa: E501

        Gets or sets the padding value for the left edge  # noqa: E501

        :return: The left.  # noqa: E501
        :rtype: int
        """
        return self._left

    @left.setter
    def left(self, left):
        """
        Sets the left.

        Gets or sets the padding value for the left edge  # noqa: E501

        :param left: The left.  # noqa: E501
        :type: int
        """
        if left is None:
            raise ValueError("Invalid value for `left`, must not be `None`")  # noqa: E501
        self._left = left
    
    @property
    def top(self):
        """
        Gets the top.  # noqa: E501

        Gets or sets the padding value for the top edge  # noqa: E501

        :return: The top.  # noqa: E501
        :rtype: int
        """
        return self._top

    @top.setter
    def top(self, top):
        """
        Sets the top.

        Gets or sets the padding value for the top edge  # noqa: E501

        :param top: The top.  # noqa: E501
        :type: int
        """
        if top is None:
            raise ValueError("Invalid value for `top`, must not be `None`")  # noqa: E501
        self._top = top
    
    @property
    def right(self):
        """
        Gets the right.  # noqa: E501

        Gets or sets the padding value for the right edge  # noqa: E501

        :return: The right.  # noqa: E501
        :rtype: int
        """
        return self._right

    @right.setter
    def right(self, right):
        """
        Sets the right.

        Gets or sets the padding value for the right edge  # noqa: E501

        :param right: The right.  # noqa: E501
        :type: int
        """
        if right is None:
            raise ValueError("Invalid value for `right`, must not be `None`")  # noqa: E501
        self._right = right
    
    @property
    def bottom(self):
        """
        Gets the bottom.  # noqa: E501

        Gets or sets the padding value for the bottom edge  # noqa: E501

        :return: The bottom.  # noqa: E501
        :rtype: int
        """
        return self._bottom

    @bottom.setter
    def bottom(self, bottom):
        """
        Sets the bottom.

        Gets or sets the padding value for the bottom edge  # noqa: E501

        :param bottom: The bottom.  # noqa: E501
        :type: int
        """
        if bottom is None:
            raise ValueError("Invalid value for `bottom`, must not be `None`")  # noqa: E501
        self._bottom = bottom

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
        if not isinstance(other, Padding):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
