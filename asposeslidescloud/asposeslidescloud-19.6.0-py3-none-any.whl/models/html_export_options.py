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

class HtmlExportOptions(ExportOptions):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'format': 'str',
        'save_as_zip': 'bool',
        'sub_directory_name': 'str',
        'show_hidden_slides': 'bool',
        'jpeg_quality': 'int',
        'pictures_compression': 'str',
        'delete_pictures_cropped_areas': 'bool',
        'notes_position': 'str',
        'comments_position': 'str',
        'comments_area_width': 'int',
        'comments_area_color': 'str',
        'show_comments_by_no_author': 'bool'
    }

    attribute_map = {
        'format': 'Format',
        'save_as_zip': 'SaveAsZip',
        'sub_directory_name': 'SubDirectoryName',
        'show_hidden_slides': 'ShowHiddenSlides',
        'jpeg_quality': 'JpegQuality',
        'pictures_compression': 'PicturesCompression',
        'delete_pictures_cropped_areas': 'DeletePicturesCroppedAreas',
        'notes_position': 'NotesPosition',
        'comments_position': 'CommentsPosition',
        'comments_area_width': 'CommentsAreaWidth',
        'comments_area_color': 'CommentsAreaColor',
        'show_comments_by_no_author': 'ShowCommentsByNoAuthor'
    }

    def __init__(self, format='html', save_as_zip=None, sub_directory_name=None, show_hidden_slides=None, jpeg_quality=None, pictures_compression=None, delete_pictures_cropped_areas=None, notes_position=None, comments_position=None, comments_area_width=None, comments_area_color=None, show_comments_by_no_author=None):  # noqa: E501
        """HtmlExportOptions - a model defined in Swagger"""  # noqa: E501
        super(HtmlExportOptions, self).__init__(format)

        self._save_as_zip = None
        self._sub_directory_name = None
        self._show_hidden_slides = None
        self._jpeg_quality = None
        self._pictures_compression = None
        self._delete_pictures_cropped_areas = None
        self._notes_position = None
        self._comments_position = None
        self._comments_area_width = None
        self._comments_area_color = None
        self._show_comments_by_no_author = None

        self.save_as_zip = save_as_zip
        if sub_directory_name is not None:
            self.sub_directory_name = sub_directory_name
        self.show_hidden_slides = show_hidden_slides
        self.jpeg_quality = jpeg_quality
        if pictures_compression is not None:
            self.pictures_compression = pictures_compression
        self.delete_pictures_cropped_areas = delete_pictures_cropped_areas
        self.notes_position = notes_position
        self.comments_position = comments_position
        self.comments_area_width = comments_area_width
        if comments_area_color is not None:
            self.comments_area_color = comments_area_color
        self.show_comments_by_no_author = show_comments_by_no_author

    @property
    def save_as_zip(self):
        """Gets the save_as_zip of this HtmlExportOptions.  # noqa: E501

        Get or sets flag for save presentation as zip file  # noqa: E501

        :return: The save_as_zip of this HtmlExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._save_as_zip

    @save_as_zip.setter
    def save_as_zip(self, save_as_zip):
        """Sets the save_as_zip of this HtmlExportOptions.

        Get or sets flag for save presentation as zip file  # noqa: E501

        :param save_as_zip: The save_as_zip of this HtmlExportOptions.  # noqa: E501
        :type: bool
        """
        self._save_as_zip = save_as_zip

    @property
    def sub_directory_name(self):
        """Gets the sub_directory_name of this HtmlExportOptions.  # noqa: E501

        Get or set name of subdirectory in zip-file for store external files  # noqa: E501

        :return: The sub_directory_name of this HtmlExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._sub_directory_name

    @sub_directory_name.setter
    def sub_directory_name(self, sub_directory_name):
        """Sets the sub_directory_name of this HtmlExportOptions.

        Get or set name of subdirectory in zip-file for store external files  # noqa: E501

        :param sub_directory_name: The sub_directory_name of this HtmlExportOptions.  # noqa: E501
        :type: str
        """
        self._sub_directory_name = sub_directory_name

    @property
    def show_hidden_slides(self):
        """Gets the show_hidden_slides of this HtmlExportOptions.  # noqa: E501

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :return: The show_hidden_slides of this HtmlExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_hidden_slides

    @show_hidden_slides.setter
    def show_hidden_slides(self, show_hidden_slides):
        """Sets the show_hidden_slides of this HtmlExportOptions.

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :param show_hidden_slides: The show_hidden_slides of this HtmlExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_hidden_slides = show_hidden_slides

    @property
    def jpeg_quality(self):
        """Gets the jpeg_quality of this HtmlExportOptions.  # noqa: E501

        Returns or sets a value determining the quality of the JPEG images inside PDF document.  # noqa: E501

        :return: The jpeg_quality of this HtmlExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._jpeg_quality

    @jpeg_quality.setter
    def jpeg_quality(self, jpeg_quality):
        """Sets the jpeg_quality of this HtmlExportOptions.

        Returns or sets a value determining the quality of the JPEG images inside PDF document.  # noqa: E501

        :param jpeg_quality: The jpeg_quality of this HtmlExportOptions.  # noqa: E501
        :type: int
        """
        self._jpeg_quality = jpeg_quality

    @property
    def pictures_compression(self):
        """Gets the pictures_compression of this HtmlExportOptions.  # noqa: E501

        Represents the pictures compression level  # noqa: E501

        :return: The pictures_compression of this HtmlExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._pictures_compression

    @pictures_compression.setter
    def pictures_compression(self, pictures_compression):
        """Sets the pictures_compression of this HtmlExportOptions.

        Represents the pictures compression level  # noqa: E501

        :param pictures_compression: The pictures_compression of this HtmlExportOptions.  # noqa: E501
        :type: str
        """
        if pictures_compression is not None:
            allowed_values = ["Dpi330", "Dpi220", "Dpi150", "Dpi96", "Dpi72", "DocumentResolution"]  # noqa: E501
            if pictures_compression not in allowed_values:
                raise ValueError(
                    "Invalid value for `pictures_compression` ({0}), must be one of {1}"  # noqa: E501
                    .format(pictures_compression, allowed_values)
                )
        self._pictures_compression = pictures_compression

    @property
    def delete_pictures_cropped_areas(self):
        """Gets the delete_pictures_cropped_areas of this HtmlExportOptions.  # noqa: E501

        A boolean flag indicates if the cropped parts remain as part of the document. If true the cropped  parts will removed, if false they will be serialized in the document (which can possible lead to a  larger file)  # noqa: E501

        :return: The delete_pictures_cropped_areas of this HtmlExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._delete_pictures_cropped_areas

    @delete_pictures_cropped_areas.setter
    def delete_pictures_cropped_areas(self, delete_pictures_cropped_areas):
        """Sets the delete_pictures_cropped_areas of this HtmlExportOptions.

        A boolean flag indicates if the cropped parts remain as part of the document. If true the cropped  parts will removed, if false they will be serialized in the document (which can possible lead to a  larger file)  # noqa: E501

        :param delete_pictures_cropped_areas: The delete_pictures_cropped_areas of this HtmlExportOptions.  # noqa: E501
        :type: bool
        """
        self._delete_pictures_cropped_areas = delete_pictures_cropped_areas

    @property
    def notes_position(self):
        """Gets the notes_position of this HtmlExportOptions.  # noqa: E501

        Gets or sets the position of the notes on the page.  # noqa: E501

        :return: The notes_position of this HtmlExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._notes_position

    @notes_position.setter
    def notes_position(self, notes_position):
        """Sets the notes_position of this HtmlExportOptions.

        Gets or sets the position of the notes on the page.  # noqa: E501

        :param notes_position: The notes_position of this HtmlExportOptions.  # noqa: E501
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
        """Gets the comments_position of this HtmlExportOptions.  # noqa: E501

        Gets or sets the position of the comments on the page.  # noqa: E501

        :return: The comments_position of this HtmlExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._comments_position

    @comments_position.setter
    def comments_position(self, comments_position):
        """Sets the comments_position of this HtmlExportOptions.

        Gets or sets the position of the comments on the page.  # noqa: E501

        :param comments_position: The comments_position of this HtmlExportOptions.  # noqa: E501
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
        """Gets the comments_area_width of this HtmlExportOptions.  # noqa: E501

        Gets or sets the width of the comment output area in pixels (Applies only if comments are displayed on the right).  # noqa: E501

        :return: The comments_area_width of this HtmlExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._comments_area_width

    @comments_area_width.setter
    def comments_area_width(self, comments_area_width):
        """Sets the comments_area_width of this HtmlExportOptions.

        Gets or sets the width of the comment output area in pixels (Applies only if comments are displayed on the right).  # noqa: E501

        :param comments_area_width: The comments_area_width of this HtmlExportOptions.  # noqa: E501
        :type: int
        """
        self._comments_area_width = comments_area_width

    @property
    def comments_area_color(self):
        """Gets the comments_area_color of this HtmlExportOptions.  # noqa: E501

        Gets or sets the color of comments area (Applies only if comments are displayed on the right).  # noqa: E501

        :return: The comments_area_color of this HtmlExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._comments_area_color

    @comments_area_color.setter
    def comments_area_color(self, comments_area_color):
        """Sets the comments_area_color of this HtmlExportOptions.

        Gets or sets the color of comments area (Applies only if comments are displayed on the right).  # noqa: E501

        :param comments_area_color: The comments_area_color of this HtmlExportOptions.  # noqa: E501
        :type: str
        """
        self._comments_area_color = comments_area_color

    @property
    def show_comments_by_no_author(self):
        """Gets the show_comments_by_no_author of this HtmlExportOptions.  # noqa: E501

        True if comments that have no author are displayed. (Applies only if comments are displayed).  # noqa: E501

        :return: The show_comments_by_no_author of this HtmlExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_comments_by_no_author

    @show_comments_by_no_author.setter
    def show_comments_by_no_author(self, show_comments_by_no_author):
        """Sets the show_comments_by_no_author of this HtmlExportOptions.

        True if comments that have no author are displayed. (Applies only if comments are displayed).  # noqa: E501

        :param show_comments_by_no_author: The show_comments_by_no_author of this HtmlExportOptions.  # noqa: E501
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
        if not isinstance(other, HtmlExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
