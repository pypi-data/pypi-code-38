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

class PdfExportOptions(ExportOptions):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'format': 'str',
        'text_compression': 'str',
        'embed_full_fonts': 'bool',
        'compliance': 'str',
        'sufficient_resolution': 'float',
        'jpeg_quality': 'int',
        'draw_slides_frame': 'bool',
        'show_hidden_slides': 'bool',
        'save_metafiles_as_png': 'bool',
        'password': 'str',
        'embed_true_type_fonts_for_ascii': 'bool',
        'additional_common_font_families': 'list[str]',
        'notes_position': 'str',
        'comments_position': 'str',
        'comments_area_width': 'int',
        'comments_area_color': 'str',
        'show_comments_by_no_author': 'bool',
        'image_transparent_color': 'str',
        'apply_image_transparent': 'bool'
    }

    attribute_map = {
        'format': 'Format',
        'text_compression': 'TextCompression',
        'embed_full_fonts': 'EmbedFullFonts',
        'compliance': 'Compliance',
        'sufficient_resolution': 'SufficientResolution',
        'jpeg_quality': 'JpegQuality',
        'draw_slides_frame': 'DrawSlidesFrame',
        'show_hidden_slides': 'ShowHiddenSlides',
        'save_metafiles_as_png': 'SaveMetafilesAsPng',
        'password': 'Password',
        'embed_true_type_fonts_for_ascii': 'EmbedTrueTypeFontsForASCII',
        'additional_common_font_families': 'AdditionalCommonFontFamilies',
        'notes_position': 'NotesPosition',
        'comments_position': 'CommentsPosition',
        'comments_area_width': 'CommentsAreaWidth',
        'comments_area_color': 'CommentsAreaColor',
        'show_comments_by_no_author': 'ShowCommentsByNoAuthor',
        'image_transparent_color': 'ImageTransparentColor',
        'apply_image_transparent': 'ApplyImageTransparent'
    }

    def __init__(self, format='pdf', text_compression=None, embed_full_fonts=None, compliance=None, sufficient_resolution=None, jpeg_quality=None, draw_slides_frame=None, show_hidden_slides=None, save_metafiles_as_png=None, password=None, embed_true_type_fonts_for_ascii=None, additional_common_font_families=None, notes_position=None, comments_position=None, comments_area_width=None, comments_area_color=None, show_comments_by_no_author=None, image_transparent_color=None, apply_image_transparent=None):  # noqa: E501
        """PdfExportOptions - a model defined in Swagger"""  # noqa: E501
        super(PdfExportOptions, self).__init__(format)

        self._text_compression = None
        self._embed_full_fonts = None
        self._compliance = None
        self._sufficient_resolution = None
        self._jpeg_quality = None
        self._draw_slides_frame = None
        self._show_hidden_slides = None
        self._save_metafiles_as_png = None
        self._password = None
        self._embed_true_type_fonts_for_ascii = None
        self._additional_common_font_families = None
        self._notes_position = None
        self._comments_position = None
        self._comments_area_width = None
        self._comments_area_color = None
        self._show_comments_by_no_author = None
        self._image_transparent_color = None
        self._apply_image_transparent = None

        self.text_compression = text_compression
        self.embed_full_fonts = embed_full_fonts
        self.compliance = compliance
        self.sufficient_resolution = sufficient_resolution
        self.jpeg_quality = jpeg_quality
        self.draw_slides_frame = draw_slides_frame
        self.show_hidden_slides = show_hidden_slides
        self.save_metafiles_as_png = save_metafiles_as_png
        if password is not None:
            self.password = password
        self.embed_true_type_fonts_for_ascii = embed_true_type_fonts_for_ascii
        if additional_common_font_families is not None:
            self.additional_common_font_families = additional_common_font_families
        self.notes_position = notes_position
        self.comments_position = comments_position
        self.comments_area_width = comments_area_width
        if comments_area_color is not None:
            self.comments_area_color = comments_area_color
        self.show_comments_by_no_author = show_comments_by_no_author
        if image_transparent_color is not None:
            self.image_transparent_color = image_transparent_color
        self.apply_image_transparent = apply_image_transparent

    @property
    def text_compression(self):
        """Gets the text_compression of this PdfExportOptions.  # noqa: E501

        Specifies compression type to be used for all textual content in the document.  # noqa: E501

        :return: The text_compression of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._text_compression

    @text_compression.setter
    def text_compression(self, text_compression):
        """Sets the text_compression of this PdfExportOptions.

        Specifies compression type to be used for all textual content in the document.  # noqa: E501

        :param text_compression: The text_compression of this PdfExportOptions.  # noqa: E501
        :type: str
        """
        if text_compression is not None:
            allowed_values = ["None", "Flate"]  # noqa: E501
            if text_compression not in allowed_values:
                raise ValueError(
                    "Invalid value for `text_compression` ({0}), must be one of {1}"  # noqa: E501
                    .format(text_compression, allowed_values)
                )
        self._text_compression = text_compression

    @property
    def embed_full_fonts(self):
        """Gets the embed_full_fonts of this PdfExportOptions.  # noqa: E501

        Determines if all characters of font should be embedded or only used subset.  # noqa: E501

        :return: The embed_full_fonts of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._embed_full_fonts

    @embed_full_fonts.setter
    def embed_full_fonts(self, embed_full_fonts):
        """Sets the embed_full_fonts of this PdfExportOptions.

        Determines if all characters of font should be embedded or only used subset.  # noqa: E501

        :param embed_full_fonts: The embed_full_fonts of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._embed_full_fonts = embed_full_fonts

    @property
    def compliance(self):
        """Gets the compliance of this PdfExportOptions.  # noqa: E501

        Desired conformance level for generated PDF document.  # noqa: E501

        :return: The compliance of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._compliance

    @compliance.setter
    def compliance(self, compliance):
        """Sets the compliance of this PdfExportOptions.

        Desired conformance level for generated PDF document.  # noqa: E501

        :param compliance: The compliance of this PdfExportOptions.  # noqa: E501
        :type: str
        """
        if compliance is not None:
            allowed_values = ["Pdf15", "PdfA1b"]  # noqa: E501
            if compliance not in allowed_values:
                raise ValueError(
                    "Invalid value for `compliance` ({0}), must be one of {1}"  # noqa: E501
                    .format(compliance, allowed_values)
                )
        self._compliance = compliance

    @property
    def sufficient_resolution(self):
        """Gets the sufficient_resolution of this PdfExportOptions.  # noqa: E501

        Returns or sets a value determining resolution of images inside PDF document.  Property affects on file size, time of export and image quality. The default value is 96.  # noqa: E501

        :return: The sufficient_resolution of this PdfExportOptions.  # noqa: E501
        :rtype: float
        """
        return self._sufficient_resolution

    @sufficient_resolution.setter
    def sufficient_resolution(self, sufficient_resolution):
        """Sets the sufficient_resolution of this PdfExportOptions.

        Returns or sets a value determining resolution of images inside PDF document.  Property affects on file size, time of export and image quality. The default value is 96.  # noqa: E501

        :param sufficient_resolution: The sufficient_resolution of this PdfExportOptions.  # noqa: E501
        :type: float
        """
        self._sufficient_resolution = sufficient_resolution

    @property
    def jpeg_quality(self):
        """Gets the jpeg_quality of this PdfExportOptions.  # noqa: E501

        Returns or sets a value determining the quality of the JPEG images inside PDF document.  # noqa: E501

        :return: The jpeg_quality of this PdfExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._jpeg_quality

    @jpeg_quality.setter
    def jpeg_quality(self, jpeg_quality):
        """Sets the jpeg_quality of this PdfExportOptions.

        Returns or sets a value determining the quality of the JPEG images inside PDF document.  # noqa: E501

        :param jpeg_quality: The jpeg_quality of this PdfExportOptions.  # noqa: E501
        :type: int
        """
        self._jpeg_quality = jpeg_quality

    @property
    def draw_slides_frame(self):
        """Gets the draw_slides_frame of this PdfExportOptions.  # noqa: E501

        True to draw black frame around each slide.  # noqa: E501

        :return: The draw_slides_frame of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._draw_slides_frame

    @draw_slides_frame.setter
    def draw_slides_frame(self, draw_slides_frame):
        """Sets the draw_slides_frame of this PdfExportOptions.

        True to draw black frame around each slide.  # noqa: E501

        :param draw_slides_frame: The draw_slides_frame of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._draw_slides_frame = draw_slides_frame

    @property
    def show_hidden_slides(self):
        """Gets the show_hidden_slides of this PdfExportOptions.  # noqa: E501

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :return: The show_hidden_slides of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_hidden_slides

    @show_hidden_slides.setter
    def show_hidden_slides(self, show_hidden_slides):
        """Sets the show_hidden_slides of this PdfExportOptions.

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :param show_hidden_slides: The show_hidden_slides of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_hidden_slides = show_hidden_slides

    @property
    def save_metafiles_as_png(self):
        """Gets the save_metafiles_as_png of this PdfExportOptions.  # noqa: E501

        True to convert all metafiles used in a presentation to the PNG images.  # noqa: E501

        :return: The save_metafiles_as_png of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._save_metafiles_as_png

    @save_metafiles_as_png.setter
    def save_metafiles_as_png(self, save_metafiles_as_png):
        """Sets the save_metafiles_as_png of this PdfExportOptions.

        True to convert all metafiles used in a presentation to the PNG images.  # noqa: E501

        :param save_metafiles_as_png: The save_metafiles_as_png of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._save_metafiles_as_png = save_metafiles_as_png

    @property
    def password(self):
        """Gets the password of this PdfExportOptions.  # noqa: E501

        Setting user password to protect the PDF document.   # noqa: E501

        :return: The password of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this PdfExportOptions.

        Setting user password to protect the PDF document.   # noqa: E501

        :param password: The password of this PdfExportOptions.  # noqa: E501
        :type: str
        """
        self._password = password

    @property
    def embed_true_type_fonts_for_ascii(self):
        """Gets the embed_true_type_fonts_for_ascii of this PdfExportOptions.  # noqa: E501

        Determines if Aspose.Slides will embed common fonts for ASCII (33..127 code range) text. Fonts for character codes greater than 127 are always embedded. Common fonts list includes PDF's base 14 fonts and additional user specified fonts.  # noqa: E501

        :return: The embed_true_type_fonts_for_ascii of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._embed_true_type_fonts_for_ascii

    @embed_true_type_fonts_for_ascii.setter
    def embed_true_type_fonts_for_ascii(self, embed_true_type_fonts_for_ascii):
        """Sets the embed_true_type_fonts_for_ascii of this PdfExportOptions.

        Determines if Aspose.Slides will embed common fonts for ASCII (33..127 code range) text. Fonts for character codes greater than 127 are always embedded. Common fonts list includes PDF's base 14 fonts and additional user specified fonts.  # noqa: E501

        :param embed_true_type_fonts_for_ascii: The embed_true_type_fonts_for_ascii of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._embed_true_type_fonts_for_ascii = embed_true_type_fonts_for_ascii

    @property
    def additional_common_font_families(self):
        """Gets the additional_common_font_families of this PdfExportOptions.  # noqa: E501

        Returns or sets an array of user-defined names of font families which Aspose.Slides should consider common.  # noqa: E501

        :return: The additional_common_font_families of this PdfExportOptions.  # noqa: E501
        :rtype: list[str]
        """
        return self._additional_common_font_families

    @additional_common_font_families.setter
    def additional_common_font_families(self, additional_common_font_families):
        """Sets the additional_common_font_families of this PdfExportOptions.

        Returns or sets an array of user-defined names of font families which Aspose.Slides should consider common.  # noqa: E501

        :param additional_common_font_families: The additional_common_font_families of this PdfExportOptions.  # noqa: E501
        :type: list[str]
        """
        self._additional_common_font_families = additional_common_font_families

    @property
    def notes_position(self):
        """Gets the notes_position of this PdfExportOptions.  # noqa: E501

        Gets or sets the position of the notes on the page.  # noqa: E501

        :return: The notes_position of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._notes_position

    @notes_position.setter
    def notes_position(self, notes_position):
        """Sets the notes_position of this PdfExportOptions.

        Gets or sets the position of the notes on the page.  # noqa: E501

        :param notes_position: The notes_position of this PdfExportOptions.  # noqa: E501
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
        """Gets the comments_position of this PdfExportOptions.  # noqa: E501

        Gets or sets the position of the comments on the page.  # noqa: E501

        :return: The comments_position of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._comments_position

    @comments_position.setter
    def comments_position(self, comments_position):
        """Sets the comments_position of this PdfExportOptions.

        Gets or sets the position of the comments on the page.  # noqa: E501

        :param comments_position: The comments_position of this PdfExportOptions.  # noqa: E501
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
        """Gets the comments_area_width of this PdfExportOptions.  # noqa: E501

        Gets or sets the width of the comment output area in pixels (Applies only if comments are displayed on the right).  # noqa: E501

        :return: The comments_area_width of this PdfExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._comments_area_width

    @comments_area_width.setter
    def comments_area_width(self, comments_area_width):
        """Sets the comments_area_width of this PdfExportOptions.

        Gets or sets the width of the comment output area in pixels (Applies only if comments are displayed on the right).  # noqa: E501

        :param comments_area_width: The comments_area_width of this PdfExportOptions.  # noqa: E501
        :type: int
        """
        self._comments_area_width = comments_area_width

    @property
    def comments_area_color(self):
        """Gets the comments_area_color of this PdfExportOptions.  # noqa: E501

        Gets or sets the color of comments area (Applies only if comments are displayed on the right).  # noqa: E501

        :return: The comments_area_color of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._comments_area_color

    @comments_area_color.setter
    def comments_area_color(self, comments_area_color):
        """Sets the comments_area_color of this PdfExportOptions.

        Gets or sets the color of comments area (Applies only if comments are displayed on the right).  # noqa: E501

        :param comments_area_color: The comments_area_color of this PdfExportOptions.  # noqa: E501
        :type: str
        """
        self._comments_area_color = comments_area_color

    @property
    def show_comments_by_no_author(self):
        """Gets the show_comments_by_no_author of this PdfExportOptions.  # noqa: E501

        True if comments that have no author are displayed. (Applies only if comments are displayed).  # noqa: E501

        :return: The show_comments_by_no_author of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_comments_by_no_author

    @show_comments_by_no_author.setter
    def show_comments_by_no_author(self, show_comments_by_no_author):
        """Sets the show_comments_by_no_author of this PdfExportOptions.

        True if comments that have no author are displayed. (Applies only if comments are displayed).  # noqa: E501

        :param show_comments_by_no_author: The show_comments_by_no_author of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_comments_by_no_author = show_comments_by_no_author

    @property
    def image_transparent_color(self):
        """Gets the image_transparent_color of this PdfExportOptions.  # noqa: E501

        Image transparent color.  # noqa: E501

        :return: The image_transparent_color of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._image_transparent_color

    @image_transparent_color.setter
    def image_transparent_color(self, image_transparent_color):
        """Sets the image_transparent_color of this PdfExportOptions.

        Image transparent color.  # noqa: E501

        :param image_transparent_color: The image_transparent_color of this PdfExportOptions.  # noqa: E501
        :type: str
        """
        self._image_transparent_color = image_transparent_color

    @property
    def apply_image_transparent(self):
        """Gets the apply_image_transparent of this PdfExportOptions.  # noqa: E501

        True to apply specified ImageTransparentColor  to an image.  # noqa: E501

        :return: The apply_image_transparent of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._apply_image_transparent

    @apply_image_transparent.setter
    def apply_image_transparent(self, apply_image_transparent):
        """Sets the apply_image_transparent of this PdfExportOptions.

        True to apply specified ImageTransparentColor  to an image.  # noqa: E501

        :param apply_image_transparent: The apply_image_transparent of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._apply_image_transparent = apply_image_transparent

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
        if not isinstance(other, PdfExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
