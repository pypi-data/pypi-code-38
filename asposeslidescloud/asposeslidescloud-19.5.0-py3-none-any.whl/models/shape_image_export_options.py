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


class ShapeImageExportOptions(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'scale_x': 'float',
        'scale_y': 'float',
        'thumbnail_bounds': 'str',
        'format': 'str'
    }

    attribute_map = {
        'scale_x': 'ScaleX',
        'scale_y': 'ScaleY',
        'thumbnail_bounds': 'ThumbnailBounds',
        'format': 'Format'
    }

    def __init__(self, scale_x=None, scale_y=None, thumbnail_bounds=None, format=None):  # noqa: E501
        """ShapeImageExportOptions - a model defined in Swagger"""  # noqa: E501

        self._scale_x = None
        self._scale_y = None
        self._thumbnail_bounds = None
        self._format = None

        self.scale_x = scale_x
        self.scale_y = scale_y
        self.thumbnail_bounds = thumbnail_bounds
        if format is not None:
            self.format = format

    @property
    def scale_x(self):
        """Gets the scale_x of this ShapeImageExportOptions.  # noqa: E501

        Get or sets scaling ratio by X axis.  # noqa: E501

        :return: The scale_x of this ShapeImageExportOptions.  # noqa: E501
        :rtype: float
        """
        return self._scale_x

    @scale_x.setter
    def scale_x(self, scale_x):
        """Sets the scale_x of this ShapeImageExportOptions.

        Get or sets scaling ratio by X axis.  # noqa: E501

        :param scale_x: The scale_x of this ShapeImageExportOptions.  # noqa: E501
        :type: float
        """
        self._scale_x = scale_x

    @property
    def scale_y(self):
        """Gets the scale_y of this ShapeImageExportOptions.  # noqa: E501

        Get or sets scaling ratio by Y axis.  # noqa: E501

        :return: The scale_y of this ShapeImageExportOptions.  # noqa: E501
        :rtype: float
        """
        return self._scale_y

    @scale_y.setter
    def scale_y(self, scale_y):
        """Sets the scale_y of this ShapeImageExportOptions.

        Get or sets scaling ratio by Y axis.  # noqa: E501

        :param scale_y: The scale_y of this ShapeImageExportOptions.  # noqa: E501
        :type: float
        """
        self._scale_y = scale_y

    @property
    def thumbnail_bounds(self):
        """Gets the thumbnail_bounds of this ShapeImageExportOptions.  # noqa: E501

        Get or sets thumbnail bounds  # noqa: E501

        :return: The thumbnail_bounds of this ShapeImageExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._thumbnail_bounds

    @thumbnail_bounds.setter
    def thumbnail_bounds(self, thumbnail_bounds):
        """Sets the thumbnail_bounds of this ShapeImageExportOptions.

        Get or sets thumbnail bounds  # noqa: E501

        :param thumbnail_bounds: The thumbnail_bounds of this ShapeImageExportOptions.  # noqa: E501
        :type: str
        """
        if thumbnail_bounds is not None:
            allowed_values = ["Slide", "Shape", "Appearance"]  # noqa: E501
            if thumbnail_bounds not in allowed_values:
                raise ValueError(
                    "Invalid value for `thumbnail_bounds` ({0}), must be one of {1}"  # noqa: E501
                    .format(thumbnail_bounds, allowed_values)
                )
        self._thumbnail_bounds = thumbnail_bounds

    @property
    def format(self):
        """Gets the format of this ShapeImageExportOptions.  # noqa: E501

        Gets export format.  # noqa: E501

        :return: The format of this ShapeImageExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._format

    @format.setter
    def format(self, format):
        """Sets the format of this ShapeImageExportOptions.

        Gets export format.  # noqa: E501

        :param format: The format of this ShapeImageExportOptions.  # noqa: E501
        :type: str
        """
        self._format = format

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
        if not isinstance(other, ShapeImageExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
