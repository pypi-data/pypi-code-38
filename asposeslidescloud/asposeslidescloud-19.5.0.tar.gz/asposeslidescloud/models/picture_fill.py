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

from asposeslidescloud.models.fill_format import FillFormat

class PictureFill(FillFormat):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'crop_bottom': 'float',
        'crop_left': 'float',
        'crop_right': 'float',
        'crop_top': 'float',
        'dpi': 'int',
        'image': 'ResourceUriElement',
        'base64_data': 'str',
        'svg_data': 'str',
        'picture_fill_mode': 'str'
    }

    attribute_map = {
        'type': 'Type',
        'crop_bottom': 'CropBottom',
        'crop_left': 'CropLeft',
        'crop_right': 'CropRight',
        'crop_top': 'CropTop',
        'dpi': 'Dpi',
        'image': 'Image',
        'base64_data': 'Base64Data',
        'svg_data': 'SvgData',
        'picture_fill_mode': 'PictureFillMode'
    }

    def __init__(self, type='Picture', crop_bottom=None, crop_left=None, crop_right=None, crop_top=None, dpi=None, image=None, base64_data=None, svg_data=None, picture_fill_mode=None):  # noqa: E501
        """PictureFill - a model defined in Swagger"""  # noqa: E501
        super(PictureFill, self).__init__(type)

        self._crop_bottom = None
        self._crop_left = None
        self._crop_right = None
        self._crop_top = None
        self._dpi = None
        self._image = None
        self._base64_data = None
        self._svg_data = None
        self._picture_fill_mode = None

        self.crop_bottom = crop_bottom
        self.crop_left = crop_left
        self.crop_right = crop_right
        self.crop_top = crop_top
        self.dpi = dpi
        if image is not None:
            self.image = image
        if base64_data is not None:
            self.base64_data = base64_data
        if svg_data is not None:
            self.svg_data = svg_data
        self.picture_fill_mode = picture_fill_mode

    @property
    def crop_bottom(self):
        """Gets the crop_bottom of this PictureFill.  # noqa: E501


        :return: The crop_bottom of this PictureFill.  # noqa: E501
        :rtype: float
        """
        return self._crop_bottom

    @crop_bottom.setter
    def crop_bottom(self, crop_bottom):
        """Sets the crop_bottom of this PictureFill.


        :param crop_bottom: The crop_bottom of this PictureFill.  # noqa: E501
        :type: float
        """
        self._crop_bottom = crop_bottom

    @property
    def crop_left(self):
        """Gets the crop_left of this PictureFill.  # noqa: E501


        :return: The crop_left of this PictureFill.  # noqa: E501
        :rtype: float
        """
        return self._crop_left

    @crop_left.setter
    def crop_left(self, crop_left):
        """Sets the crop_left of this PictureFill.


        :param crop_left: The crop_left of this PictureFill.  # noqa: E501
        :type: float
        """
        self._crop_left = crop_left

    @property
    def crop_right(self):
        """Gets the crop_right of this PictureFill.  # noqa: E501


        :return: The crop_right of this PictureFill.  # noqa: E501
        :rtype: float
        """
        return self._crop_right

    @crop_right.setter
    def crop_right(self, crop_right):
        """Sets the crop_right of this PictureFill.


        :param crop_right: The crop_right of this PictureFill.  # noqa: E501
        :type: float
        """
        self._crop_right = crop_right

    @property
    def crop_top(self):
        """Gets the crop_top of this PictureFill.  # noqa: E501


        :return: The crop_top of this PictureFill.  # noqa: E501
        :rtype: float
        """
        return self._crop_top

    @crop_top.setter
    def crop_top(self, crop_top):
        """Sets the crop_top of this PictureFill.


        :param crop_top: The crop_top of this PictureFill.  # noqa: E501
        :type: float
        """
        self._crop_top = crop_top

    @property
    def dpi(self):
        """Gets the dpi of this PictureFill.  # noqa: E501


        :return: The dpi of this PictureFill.  # noqa: E501
        :rtype: int
        """
        return self._dpi

    @dpi.setter
    def dpi(self, dpi):
        """Sets the dpi of this PictureFill.


        :param dpi: The dpi of this PictureFill.  # noqa: E501
        :type: int
        """
        self._dpi = dpi

    @property
    def image(self):
        """Gets the image of this PictureFill.  # noqa: E501


        :return: The image of this PictureFill.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._image

    @image.setter
    def image(self, image):
        """Sets the image of this PictureFill.


        :param image: The image of this PictureFill.  # noqa: E501
        :type: ResourceUriElement
        """
        self._image = image

    @property
    def base64_data(self):
        """Gets the base64_data of this PictureFill.  # noqa: E501


        :return: The base64_data of this PictureFill.  # noqa: E501
        :rtype: str
        """
        return self._base64_data

    @base64_data.setter
    def base64_data(self, base64_data):
        """Sets the base64_data of this PictureFill.


        :param base64_data: The base64_data of this PictureFill.  # noqa: E501
        :type: str
        """
        self._base64_data = base64_data

    @property
    def svg_data(self):
        """Gets the svg_data of this PictureFill.  # noqa: E501


        :return: The svg_data of this PictureFill.  # noqa: E501
        :rtype: str
        """
        return self._svg_data

    @svg_data.setter
    def svg_data(self, svg_data):
        """Sets the svg_data of this PictureFill.


        :param svg_data: The svg_data of this PictureFill.  # noqa: E501
        :type: str
        """
        self._svg_data = svg_data

    @property
    def picture_fill_mode(self):
        """Gets the picture_fill_mode of this PictureFill.  # noqa: E501


        :return: The picture_fill_mode of this PictureFill.  # noqa: E501
        :rtype: str
        """
        return self._picture_fill_mode

    @picture_fill_mode.setter
    def picture_fill_mode(self, picture_fill_mode):
        """Sets the picture_fill_mode of this PictureFill.


        :param picture_fill_mode: The picture_fill_mode of this PictureFill.  # noqa: E501
        :type: str
        """
        if picture_fill_mode is not None:
            allowed_values = ["Tile", "Stretch"]  # noqa: E501
            if picture_fill_mode not in allowed_values:
                raise ValueError(
                    "Invalid value for `picture_fill_mode` ({0}), must be one of {1}"  # noqa: E501
                    .format(picture_fill_mode, allowed_values)
                )
        self._picture_fill_mode = picture_fill_mode

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
        if not isinstance(other, PictureFill):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
