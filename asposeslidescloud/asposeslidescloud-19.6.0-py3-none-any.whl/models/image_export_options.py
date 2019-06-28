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

from asposeslidescloud.models.export_options import ExportOptions

class ImageExportOptions(ExportOptions):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'format': 'str',
        'notes_position': 'str',
        'comments_position': 'str',
        'comments_area_width': 'int',
        'comments_area_color': 'str'
    }

    attribute_map = {
        'format': 'Format',
        'notes_position': 'NotesPosition',
        'comments_position': 'CommentsPosition',
        'comments_area_width': 'CommentsAreaWidth',
        'comments_area_color': 'CommentsAreaColor'
    }

    def __init__(self, format='image', notes_position=None, comments_position=None, comments_area_width=None, comments_area_color=None):  # noqa: E501
        """ImageExportOptions - a model defined in Swagger"""  # noqa: E501
        super(ImageExportOptions, self).__init__(format)

        self._notes_position = None
        self._comments_position = None
        self._comments_area_width = None
        self._comments_area_color = None

        self.notes_position = notes_position
        self.comments_position = comments_position
        self.comments_area_width = comments_area_width
        if comments_area_color is not None:
            self.comments_area_color = comments_area_color

    @property
    def notes_position(self):
        """Gets the notes_position of this ImageExportOptions.  # noqa: E501

        Gets or sets the position of the notes on the page.  # noqa: E501

        :return: The notes_position of this ImageExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._notes_position

    @notes_position.setter
    def notes_position(self, notes_position):
        """Sets the notes_position of this ImageExportOptions.

        Gets or sets the position of the notes on the page.  # noqa: E501

        :param notes_position: The notes_position of this ImageExportOptions.  # noqa: E501
        :type: str
        """
        if notes_position is not None:
            allowed_values = ["None", "BottomFull", "BottomTruncated"]  # noqa: E501
            if notes_position not in allowed_values:
                raise ValueError(
                    "Invalid value for `notes_position` ({0}), must be one of {1}"  # noqa: E501
                    .format(notes_position, allowed_values)
                )
        self._notes_position = notes_position

    @property
    def comments_position(self):
        """Gets the comments_position of this ImageExportOptions.  # noqa: E501

        Gets or sets the position of the comments on the page.  # noqa: E501

        :return: The comments_position of this ImageExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._comments_position

    @comments_position.setter
    def comments_position(self, comments_position):
        """Sets the comments_position of this ImageExportOptions.

        Gets or sets the position of the comments on the page.  # noqa: E501

        :param comments_position: The comments_position of this ImageExportOptions.  # noqa: E501
        :type: str
        """
        if comments_position is not None:
            allowed_values = ["None", "Bottom", "Right"]  # noqa: E501
            if comments_position not in allowed_values:
                raise ValueError(
                    "Invalid value for `comments_position` ({0}), must be one of {1}"  # noqa: E501
                    .format(comments_position, allowed_values)
                )
        self._comments_position = comments_position

    @property
    def comments_area_width(self):
        """Gets the comments_area_width of this ImageExportOptions.  # noqa: E501

        Gets or sets the width of the comment output area in pixels (Applies only if comments are displayed on the right).  # noqa: E501

        :return: The comments_area_width of this ImageExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._comments_area_width

    @comments_area_width.setter
    def comments_area_width(self, comments_area_width):
        """Sets the comments_area_width of this ImageExportOptions.

        Gets or sets the width of the comment output area in pixels (Applies only if comments are displayed on the right).  # noqa: E501

        :param comments_area_width: The comments_area_width of this ImageExportOptions.  # noqa: E501
        :type: int
        """
        self._comments_area_width = comments_area_width

    @property
    def comments_area_color(self):
        """Gets the comments_area_color of this ImageExportOptions.  # noqa: E501

        Gets or sets the color of comments area (Applies only if comments are displayed on the right).  # noqa: E501

        :return: The comments_area_color of this ImageExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._comments_area_color

    @comments_area_color.setter
    def comments_area_color(self, comments_area_color):
        """Sets the comments_area_color of this ImageExportOptions.

        Gets or sets the color of comments area (Applies only if comments are displayed on the right).  # noqa: E501

        :param comments_area_color: The comments_area_color of this ImageExportOptions.  # noqa: E501
        :type: str
        """
        self._comments_area_color = comments_area_color

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
        if not isinstance(other, ImageExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
