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

class SvgExportOptions(ExportOptions):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'format': 'str',
        'vectorize_text': 'bool',
        'metafile_rasterization_dpi': 'int',
        'disable3_d_text': 'bool',
        'disable_gradient_split': 'bool',
        'disable_line_end_cropping': 'bool',
        'jpeg_quality': 'int',
        'pictures_compression': 'str',
        'delete_pictures_cropped_areas': 'bool',
        'external_fonts_handling': 'str'
    }

    attribute_map = {
        'format': 'Format',
        'vectorize_text': 'VectorizeText',
        'metafile_rasterization_dpi': 'MetafileRasterizationDpi',
        'disable3_d_text': 'Disable3DText',
        'disable_gradient_split': 'DisableGradientSplit',
        'disable_line_end_cropping': 'DisableLineEndCropping',
        'jpeg_quality': 'JpegQuality',
        'pictures_compression': 'PicturesCompression',
        'delete_pictures_cropped_areas': 'DeletePicturesCroppedAreas',
        'external_fonts_handling': 'ExternalFontsHandling'
    }

    def __init__(self, format='svg', vectorize_text=None, metafile_rasterization_dpi=None, disable3_d_text=None, disable_gradient_split=None, disable_line_end_cropping=None, jpeg_quality=None, pictures_compression=None, delete_pictures_cropped_areas=None, external_fonts_handling=None):  # noqa: E501
        """SvgExportOptions - a model defined in Swagger"""  # noqa: E501
        super(SvgExportOptions, self).__init__(format)

        self._vectorize_text = None
        self._metafile_rasterization_dpi = None
        self._disable3_d_text = None
        self._disable_gradient_split = None
        self._disable_line_end_cropping = None
        self._jpeg_quality = None
        self._pictures_compression = None
        self._delete_pictures_cropped_areas = None
        self._external_fonts_handling = None

        self.vectorize_text = vectorize_text
        self.metafile_rasterization_dpi = metafile_rasterization_dpi
        self.disable3_d_text = disable3_d_text
        self.disable_gradient_split = disable_gradient_split
        self.disable_line_end_cropping = disable_line_end_cropping
        self.jpeg_quality = jpeg_quality
        self.pictures_compression = pictures_compression
        self.delete_pictures_cropped_areas = delete_pictures_cropped_areas
        self.external_fonts_handling = external_fonts_handling

    @property
    def vectorize_text(self):
        """Gets the vectorize_text of this SvgExportOptions.  # noqa: E501

        Determines whether the text on a slide will be saved as graphics.  # noqa: E501

        :return: The vectorize_text of this SvgExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._vectorize_text

    @vectorize_text.setter
    def vectorize_text(self, vectorize_text):
        """Sets the vectorize_text of this SvgExportOptions.

        Determines whether the text on a slide will be saved as graphics.  # noqa: E501

        :param vectorize_text: The vectorize_text of this SvgExportOptions.  # noqa: E501
        :type: bool
        """
        self._vectorize_text = vectorize_text

    @property
    def metafile_rasterization_dpi(self):
        """Gets the metafile_rasterization_dpi of this SvgExportOptions.  # noqa: E501

        Returns or sets the lower resolution limit for metafile rasterization.  # noqa: E501

        :return: The metafile_rasterization_dpi of this SvgExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._metafile_rasterization_dpi

    @metafile_rasterization_dpi.setter
    def metafile_rasterization_dpi(self, metafile_rasterization_dpi):
        """Sets the metafile_rasterization_dpi of this SvgExportOptions.

        Returns or sets the lower resolution limit for metafile rasterization.  # noqa: E501

        :param metafile_rasterization_dpi: The metafile_rasterization_dpi of this SvgExportOptions.  # noqa: E501
        :type: int
        """
        self._metafile_rasterization_dpi = metafile_rasterization_dpi

    @property
    def disable3_d_text(self):
        """Gets the disable3_d_text of this SvgExportOptions.  # noqa: E501

        Determines whether the 3D text is disabled in SVG.  # noqa: E501

        :return: The disable3_d_text of this SvgExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._disable3_d_text

    @disable3_d_text.setter
    def disable3_d_text(self, disable3_d_text):
        """Sets the disable3_d_text of this SvgExportOptions.

        Determines whether the 3D text is disabled in SVG.  # noqa: E501

        :param disable3_d_text: The disable3_d_text of this SvgExportOptions.  # noqa: E501
        :type: bool
        """
        self._disable3_d_text = disable3_d_text

    @property
    def disable_gradient_split(self):
        """Gets the disable_gradient_split of this SvgExportOptions.  # noqa: E501

        Disables splitting FromCornerX and FromCenter gradients.  # noqa: E501

        :return: The disable_gradient_split of this SvgExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._disable_gradient_split

    @disable_gradient_split.setter
    def disable_gradient_split(self, disable_gradient_split):
        """Sets the disable_gradient_split of this SvgExportOptions.

        Disables splitting FromCornerX and FromCenter gradients.  # noqa: E501

        :param disable_gradient_split: The disable_gradient_split of this SvgExportOptions.  # noqa: E501
        :type: bool
        """
        self._disable_gradient_split = disable_gradient_split

    @property
    def disable_line_end_cropping(self):
        """Gets the disable_line_end_cropping of this SvgExportOptions.  # noqa: E501

        SVG 1.1 lacks ability to define insets for markers. Aspose.Slides SVG writing engine has workaround for that problem: it crops end of line with arrow, so, line doesn't overlap markers. This option switches off such behavior.  # noqa: E501

        :return: The disable_line_end_cropping of this SvgExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._disable_line_end_cropping

    @disable_line_end_cropping.setter
    def disable_line_end_cropping(self, disable_line_end_cropping):
        """Sets the disable_line_end_cropping of this SvgExportOptions.

        SVG 1.1 lacks ability to define insets for markers. Aspose.Slides SVG writing engine has workaround for that problem: it crops end of line with arrow, so, line doesn't overlap markers. This option switches off such behavior.  # noqa: E501

        :param disable_line_end_cropping: The disable_line_end_cropping of this SvgExportOptions.  # noqa: E501
        :type: bool
        """
        self._disable_line_end_cropping = disable_line_end_cropping

    @property
    def jpeg_quality(self):
        """Gets the jpeg_quality of this SvgExportOptions.  # noqa: E501

        Determines JPEG encoding quality.  # noqa: E501

        :return: The jpeg_quality of this SvgExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._jpeg_quality

    @jpeg_quality.setter
    def jpeg_quality(self, jpeg_quality):
        """Sets the jpeg_quality of this SvgExportOptions.

        Determines JPEG encoding quality.  # noqa: E501

        :param jpeg_quality: The jpeg_quality of this SvgExportOptions.  # noqa: E501
        :type: int
        """
        self._jpeg_quality = jpeg_quality

    @property
    def pictures_compression(self):
        """Gets the pictures_compression of this SvgExportOptions.  # noqa: E501

        Represents the pictures compression level  # noqa: E501

        :return: The pictures_compression of this SvgExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._pictures_compression

    @pictures_compression.setter
    def pictures_compression(self, pictures_compression):
        """Sets the pictures_compression of this SvgExportOptions.

        Represents the pictures compression level  # noqa: E501

        :param pictures_compression: The pictures_compression of this SvgExportOptions.  # noqa: E501
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
        """Gets the delete_pictures_cropped_areas of this SvgExportOptions.  # noqa: E501

        A boolean flag indicates if the cropped parts remain as part of the document. If true the cropped  parts will removed, if false they will be serialized in the document (which can possible lead to a  larger file)  # noqa: E501

        :return: The delete_pictures_cropped_areas of this SvgExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._delete_pictures_cropped_areas

    @delete_pictures_cropped_areas.setter
    def delete_pictures_cropped_areas(self, delete_pictures_cropped_areas):
        """Sets the delete_pictures_cropped_areas of this SvgExportOptions.

        A boolean flag indicates if the cropped parts remain as part of the document. If true the cropped  parts will removed, if false they will be serialized in the document (which can possible lead to a  larger file)  # noqa: E501

        :param delete_pictures_cropped_areas: The delete_pictures_cropped_areas of this SvgExportOptions.  # noqa: E501
        :type: bool
        """
        self._delete_pictures_cropped_areas = delete_pictures_cropped_areas

    @property
    def external_fonts_handling(self):
        """Gets the external_fonts_handling of this SvgExportOptions.  # noqa: E501

        Determines a way of handling externally loaded fonts.  # noqa: E501

        :return: The external_fonts_handling of this SvgExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._external_fonts_handling

    @external_fonts_handling.setter
    def external_fonts_handling(self, external_fonts_handling):
        """Sets the external_fonts_handling of this SvgExportOptions.

        Determines a way of handling externally loaded fonts.  # noqa: E501

        :param external_fonts_handling: The external_fonts_handling of this SvgExportOptions.  # noqa: E501
        :type: str
        """
        if external_fonts_handling is not None:
            allowed_values = ["AddLinksToFontFiles", "Embed", "Vectorize"]  # noqa: E501
            if external_fonts_handling not in allowed_values:
                raise ValueError(
                    "Invalid value for `external_fonts_handling` ({0}), must be one of {1}"  # noqa: E501
                    .format(external_fonts_handling, allowed_values)
                )
        self._external_fonts_handling = external_fonts_handling

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
        if not isinstance(other, SvgExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
