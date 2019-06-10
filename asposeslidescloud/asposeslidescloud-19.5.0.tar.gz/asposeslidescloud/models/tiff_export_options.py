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

class TiffExportOptions(ExportOptions):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'format': 'str',
        'compression': 'str',
        'width': 'int',
        'height': 'int',
        'dpi_x': 'int',
        'dpi_y': 'int',
        'show_hidden_slides': 'bool',
        'pixel_format': 'str',
        'notes_position': 'str',
        'comments_position': 'str',
        'comments_area_width': 'int',
        'comments_area_color': 'str',
        'show_comments_by_no_author': 'bool'
    }

    attribute_map = {
        'format': 'Format',
        'compression': 'Compression',
        'width': 'Width',
        'height': 'Height',
        'dpi_x': 'DpiX',
        'dpi_y': 'DpiY',
        'show_hidden_slides': 'ShowHiddenSlides',
        'pixel_format': 'PixelFormat',
        'notes_position': 'NotesPosition',
        'comments_position': 'CommentsPosition',
        'comments_area_width': 'CommentsAreaWidth',
        'comments_area_color': 'CommentsAreaColor',
        'show_comments_by_no_author': 'ShowCommentsByNoAuthor'
    }

    def __init__(self, format='tiff', compression=None, width=None, height=None, dpi_x=None, dpi_y=None, show_hidden_slides=None, pixel_format=None, notes_position=None, comments_position=None, comments_area_width=None, comments_area_color=None, show_comments_by_no_author=None):  # noqa: E501
        """TiffExportOptions - a model defined in Swagger"""  # noqa: E501
        super(TiffExportOptions, self).__init__(format)

        self._compression = None
        self._width = None
        self._height = None
        self._dpi_x = None
        self._dpi_y = None
        self._show_hidden_slides = None
        self._pixel_format = None
        self._notes_position = None
        self._comments_position = None
        self._comments_area_width = None
        self._comments_area_color = None
        self._show_comments_by_no_author = None

        self.compression = compression
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if dpi_x is not None:
            self.dpi_x = dpi_x
        if dpi_y is not None:
            self.dpi_y = dpi_y
        self.show_hidden_slides = show_hidden_slides
        self.pixel_format = pixel_format
        self.notes_position = notes_position
        self.comments_position = comments_position
        self.comments_area_width = comments_area_width
        if comments_area_color is not None:
            self.comments_area_color = comments_area_color
        self.show_comments_by_no_author = show_comments_by_no_author

    @property
    def compression(self):
        """Gets the compression of this TiffExportOptions.  # noqa: E501


        :return: The compression of this TiffExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._compression

    @compression.setter
    def compression(self, compression):
        """Sets the compression of this TiffExportOptions.


        :param compression: The compression of this TiffExportOptions.  # noqa: E501
        :type: str
        """
        if compression is not None:
            allowed_values = ["Default", "None", "CCITT3", "CCITT4", "LZW", "RLE"]  # noqa: E501
            if compression not in allowed_values:
                raise ValueError(
                    "Invalid value for `compression` ({0}), must be one of {1}"  # noqa: E501
                    .format(compression, allowed_values)
                )
        self._compression = compression

    @property
    def width(self):
        """Gets the width of this TiffExportOptions.  # noqa: E501


        :return: The width of this TiffExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._width

    @width.setter
    def width(self, width):
        """Sets the width of this TiffExportOptions.


        :param width: The width of this TiffExportOptions.  # noqa: E501
        :type: int
        """
        self._width = width

    @property
    def height(self):
        """Gets the height of this TiffExportOptions.  # noqa: E501


        :return: The height of this TiffExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._height

    @height.setter
    def height(self, height):
        """Sets the height of this TiffExportOptions.


        :param height: The height of this TiffExportOptions.  # noqa: E501
        :type: int
        """
        self._height = height

    @property
    def dpi_x(self):
        """Gets the dpi_x of this TiffExportOptions.  # noqa: E501


        :return: The dpi_x of this TiffExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._dpi_x

    @dpi_x.setter
    def dpi_x(self, dpi_x):
        """Sets the dpi_x of this TiffExportOptions.


        :param dpi_x: The dpi_x of this TiffExportOptions.  # noqa: E501
        :type: int
        """
        self._dpi_x = dpi_x

    @property
    def dpi_y(self):
        """Gets the dpi_y of this TiffExportOptions.  # noqa: E501


        :return: The dpi_y of this TiffExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._dpi_y

    @dpi_y.setter
    def dpi_y(self, dpi_y):
        """Sets the dpi_y of this TiffExportOptions.


        :param dpi_y: The dpi_y of this TiffExportOptions.  # noqa: E501
        :type: int
        """
        self._dpi_y = dpi_y

    @property
    def show_hidden_slides(self):
        """Gets the show_hidden_slides of this TiffExportOptions.  # noqa: E501

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :return: The show_hidden_slides of this TiffExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_hidden_slides

    @show_hidden_slides.setter
    def show_hidden_slides(self, show_hidden_slides):
        """Sets the show_hidden_slides of this TiffExportOptions.

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :param show_hidden_slides: The show_hidden_slides of this TiffExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_hidden_slides = show_hidden_slides

    @property
    def pixel_format(self):
        """Gets the pixel_format of this TiffExportOptions.  # noqa: E501

        Specifies the pixel format for the generated images. Read/write ImagePixelFormat.  # noqa: E501

        :return: The pixel_format of this TiffExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._pixel_format

    @pixel_format.setter
    def pixel_format(self, pixel_format):
        """Sets the pixel_format of this TiffExportOptions.

        Specifies the pixel format for the generated images. Read/write ImagePixelFormat.  # noqa: E501

        :param pixel_format: The pixel_format of this TiffExportOptions.  # noqa: E501
        :type: str
        """
        if pixel_format is not None:
            allowed_values = ["Format1bppIndexed", "Format4bppIndexed", "Format8bppIndexed", "Format24bppRgb", "Format32bppArgb"]  # noqa: E501
            if pixel_format not in allowed_values:
                raise ValueError(
                    "Invalid value for `pixel_format` ({0}), must be one of {1}"  # noqa: E501
                    .format(pixel_format, allowed_values)
                )
        self._pixel_format = pixel_format

    @property
    def notes_position(self):
        """Gets the notes_position of this TiffExportOptions.  # noqa: E501

        Gets or sets the position of the notes on the page.  # noqa: E501

        :return: The notes_position of this TiffExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._notes_position

    @notes_position.setter
    def notes_position(self, notes_position):
        """Sets the notes_position of this TiffExportOptions.

        Gets or sets the position of the notes on the page.  # noqa: E501

        :param notes_position: The notes_position of this TiffExportOptions.  # noqa: E501
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
        """Gets the comments_position of this TiffExportOptions.  # noqa: E501

        Gets or sets the position of the comments on the page.  # noqa: E501

        :return: The comments_position of this TiffExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._comments_position

    @comments_position.setter
    def comments_position(self, comments_position):
        """Sets the comments_position of this TiffExportOptions.

        Gets or sets the position of the comments on the page.  # noqa: E501

        :param comments_position: The comments_position of this TiffExportOptions.  # noqa: E501
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
        """Gets the comments_area_width of this TiffExportOptions.  # noqa: E501

        Gets or sets the width of the comment output area in pixels (Applies only if comments are displayed on the right).  # noqa: E501

        :return: The comments_area_width of this TiffExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._comments_area_width

    @comments_area_width.setter
    def comments_area_width(self, comments_area_width):
        """Sets the comments_area_width of this TiffExportOptions.

        Gets or sets the width of the comment output area in pixels (Applies only if comments are displayed on the right).  # noqa: E501

        :param comments_area_width: The comments_area_width of this TiffExportOptions.  # noqa: E501
        :type: int
        """
        self._comments_area_width = comments_area_width

    @property
    def comments_area_color(self):
        """Gets the comments_area_color of this TiffExportOptions.  # noqa: E501

        Gets or sets the color of comments area (Applies only if comments are displayed on the right).  # noqa: E501

        :return: The comments_area_color of this TiffExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._comments_area_color

    @comments_area_color.setter
    def comments_area_color(self, comments_area_color):
        """Sets the comments_area_color of this TiffExportOptions.

        Gets or sets the color of comments area (Applies only if comments are displayed on the right).  # noqa: E501

        :param comments_area_color: The comments_area_color of this TiffExportOptions.  # noqa: E501
        :type: str
        """
        self._comments_area_color = comments_area_color

    @property
    def show_comments_by_no_author(self):
        """Gets the show_comments_by_no_author of this TiffExportOptions.  # noqa: E501

        True if comments that have no author are displayed. (Applies only if comments are displayed).  # noqa: E501

        :return: The show_comments_by_no_author of this TiffExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_comments_by_no_author

    @show_comments_by_no_author.setter
    def show_comments_by_no_author(self, show_comments_by_no_author):
        """Sets the show_comments_by_no_author of this TiffExportOptions.

        True if comments that have no author are displayed. (Applies only if comments are displayed).  # noqa: E501

        :param show_comments_by_no_author: The show_comments_by_no_author of this TiffExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_comments_by_no_author = show_comments_by_no_author

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
        if not isinstance(other, TiffExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
