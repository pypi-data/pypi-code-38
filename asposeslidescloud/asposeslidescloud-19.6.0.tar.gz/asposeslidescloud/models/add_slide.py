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

class AddSlide(Task):


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
        'position': 'int',
        'layout_alias': 'str'
    }

    attribute_map = {
        'type': 'Type',
        'clone_from_file': 'CloneFromFile',
        'clone_from_position': 'CloneFromPosition',
        'position': 'Position',
        'layout_alias': 'LayoutAlias'
    }

    def __init__(self, type='AddSlide', clone_from_file=None, clone_from_position=None, position=None, layout_alias=None):  # noqa: E501
        """AddSlide - a model defined in Swagger"""  # noqa: E501
        super(AddSlide, self).__init__(type)

        self._clone_from_file = None
        self._clone_from_position = None
        self._position = None
        self._layout_alias = None

        if clone_from_file is not None:
            self.clone_from_file = clone_from_file
        self.clone_from_position = clone_from_position
        self.position = position
        if layout_alias is not None:
            self.layout_alias = layout_alias

    @property
    def clone_from_file(self):
        """Gets the clone_from_file of this AddSlide.  # noqa: E501

        File to clone a slide from.  # noqa: E501

        :return: The clone_from_file of this AddSlide.  # noqa: E501
        :rtype: InputFile
        """
        return self._clone_from_file

    @clone_from_file.setter
    def clone_from_file(self, clone_from_file):
        """Sets the clone_from_file of this AddSlide.

        File to clone a slide from.  # noqa: E501

        :param clone_from_file: The clone_from_file of this AddSlide.  # noqa: E501
        :type: InputFile
        """
        self._clone_from_file = clone_from_file

    @property
    def clone_from_position(self):
        """Gets the clone_from_position of this AddSlide.  # noqa: E501

        Position of the slide to clone.  # noqa: E501

        :return: The clone_from_position of this AddSlide.  # noqa: E501
        :rtype: int
        """
        return self._clone_from_position

    @clone_from_position.setter
    def clone_from_position(self, clone_from_position):
        """Sets the clone_from_position of this AddSlide.

        Position of the slide to clone.  # noqa: E501

        :param clone_from_position: The clone_from_position of this AddSlide.  # noqa: E501
        :type: int
        """
        self._clone_from_position = clone_from_position

    @property
    def position(self):
        """Gets the position of this AddSlide.  # noqa: E501

        Position at which to insert the slide.  # noqa: E501

        :return: The position of this AddSlide.  # noqa: E501
        :rtype: int
        """
        return self._position

    @position.setter
    def position(self, position):
        """Sets the position of this AddSlide.

        Position at which to insert the slide.  # noqa: E501

        :param position: The position of this AddSlide.  # noqa: E501
        :type: int
        """
        self._position = position

    @property
    def layout_alias(self):
        """Gets the layout_alias of this AddSlide.  # noqa: E501

        Alias of layout (href, index or type). If value is null a blank slide is added.  # noqa: E501

        :return: The layout_alias of this AddSlide.  # noqa: E501
        :rtype: str
        """
        return self._layout_alias

    @layout_alias.setter
    def layout_alias(self, layout_alias):
        """Sets the layout_alias of this AddSlide.

        Alias of layout (href, index or type). If value is null a blank slide is added.  # noqa: E501

        :param layout_alias: The layout_alias of this AddSlide.  # noqa: E501
        :type: str
        """
        self._layout_alias = layout_alias

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
        if not isinstance(other, AddSlide):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
