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

class XpsExportOptions(ExportOptions):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'format': 'str',
        'show_hidden_slides': 'bool',
        'save_metafiles_as_png': 'bool',
        'draw_slides_frame': 'bool'
    }

    attribute_map = {
        'format': 'Format',
        'show_hidden_slides': 'ShowHiddenSlides',
        'save_metafiles_as_png': 'SaveMetafilesAsPng',
        'draw_slides_frame': 'DrawSlidesFrame'
    }

    def __init__(self, format='xps', show_hidden_slides=None, save_metafiles_as_png=None, draw_slides_frame=None):  # noqa: E501
        """XpsExportOptions - a model defined in Swagger"""  # noqa: E501
        super(XpsExportOptions, self).__init__(format)

        self._show_hidden_slides = None
        self._save_metafiles_as_png = None
        self._draw_slides_frame = None

        self.show_hidden_slides = show_hidden_slides
        self.save_metafiles_as_png = save_metafiles_as_png
        self.draw_slides_frame = draw_slides_frame

    @property
    def show_hidden_slides(self):
        """Gets the show_hidden_slides of this XpsExportOptions.  # noqa: E501

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :return: The show_hidden_slides of this XpsExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_hidden_slides

    @show_hidden_slides.setter
    def show_hidden_slides(self, show_hidden_slides):
        """Sets the show_hidden_slides of this XpsExportOptions.

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :param show_hidden_slides: The show_hidden_slides of this XpsExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_hidden_slides = show_hidden_slides

    @property
    def save_metafiles_as_png(self):
        """Gets the save_metafiles_as_png of this XpsExportOptions.  # noqa: E501

        True to convert all metafiles used in a presentation to the PNG images.  # noqa: E501

        :return: The save_metafiles_as_png of this XpsExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._save_metafiles_as_png

    @save_metafiles_as_png.setter
    def save_metafiles_as_png(self, save_metafiles_as_png):
        """Sets the save_metafiles_as_png of this XpsExportOptions.

        True to convert all metafiles used in a presentation to the PNG images.  # noqa: E501

        :param save_metafiles_as_png: The save_metafiles_as_png of this XpsExportOptions.  # noqa: E501
        :type: bool
        """
        self._save_metafiles_as_png = save_metafiles_as_png

    @property
    def draw_slides_frame(self):
        """Gets the draw_slides_frame of this XpsExportOptions.  # noqa: E501

        True to draw black frame around each slide.  # noqa: E501

        :return: The draw_slides_frame of this XpsExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._draw_slides_frame

    @draw_slides_frame.setter
    def draw_slides_frame(self, draw_slides_frame):
        """Sets the draw_slides_frame of this XpsExportOptions.

        True to draw black frame around each slide.  # noqa: E501

        :param draw_slides_frame: The draw_slides_frame of this XpsExportOptions.  # noqa: E501
        :type: bool
        """
        self._draw_slides_frame = draw_slides_frame

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
        if not isinstance(other, XpsExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
