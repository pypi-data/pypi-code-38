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

from asposeslidescloud.models.series import Series

class ScatterSeries(Series):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'name': 'str',
        'is_color_varied': 'bool',
        'inverted_solid_fill_color': 'str',
        'smooth': 'bool',
        'plot_on_second_axis': 'bool',
        'order': 'int',
        'number_format_of_y_values': 'str',
        'number_format_of_x_values': 'str',
        'number_format_of_values': 'str',
        'number_format_of_bubble_sizes': 'str',
        'invert_if_negative': 'bool',
        'explosion': 'int',
        'marker': 'SeriesMarker',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'data_point_type': 'str',
        'data_points': 'list[ScatterChartDataPoint]'
    }

    attribute_map = {
        'type': 'Type',
        'name': 'Name',
        'is_color_varied': 'IsColorVaried',
        'inverted_solid_fill_color': 'InvertedSolidFillColor',
        'smooth': 'Smooth',
        'plot_on_second_axis': 'PlotOnSecondAxis',
        'order': 'Order',
        'number_format_of_y_values': 'NumberFormatOfYValues',
        'number_format_of_x_values': 'NumberFormatOfXValues',
        'number_format_of_values': 'NumberFormatOfValues',
        'number_format_of_bubble_sizes': 'NumberFormatOfBubbleSizes',
        'invert_if_negative': 'InvertIfNegative',
        'explosion': 'Explosion',
        'marker': 'Marker',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'data_point_type': 'DataPointType',
        'data_points': 'DataPoints'
    }

    def __init__(self, type=None, name=None, is_color_varied=None, inverted_solid_fill_color=None, smooth=None, plot_on_second_axis=None, order=None, number_format_of_y_values=None, number_format_of_x_values=None, number_format_of_values=None, number_format_of_bubble_sizes=None, invert_if_negative=None, explosion=None, marker=None, fill_format=None, effect_format=None, line_format=None, data_point_type=None, data_points=None):  # noqa: E501
        """ScatterSeries - a model defined in Swagger"""  # noqa: E501
        super(ScatterSeries, self).__init__(type, name, is_color_varied, inverted_solid_fill_color, smooth, plot_on_second_axis, order, number_format_of_y_values, number_format_of_x_values, number_format_of_values, number_format_of_bubble_sizes, invert_if_negative, explosion, marker, fill_format, effect_format, line_format)

        self._data_point_type = None
        self._data_points = None

        self.data_point_type = data_point_type
        if data_points is not None:
            self.data_points = data_points

    @property
    def data_point_type(self):
        """Gets the data_point_type of this ScatterSeries.  # noqa: E501

        Data point type.  # noqa: E501

        :return: The data_point_type of this ScatterSeries.  # noqa: E501
        :rtype: str
        """
        return self._data_point_type

    @data_point_type.setter
    def data_point_type(self, data_point_type):
        """Sets the data_point_type of this ScatterSeries.

        Data point type.  # noqa: E501

        :param data_point_type: The data_point_type of this ScatterSeries.  # noqa: E501
        :type: str
        """
        if data_point_type is not None:
            allowed_values = ["OneValue", "Scatter", "Bubble"]  # noqa: E501
            if data_point_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `data_point_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(data_point_type, allowed_values)
                )
        self._data_point_type = data_point_type

    @property
    def data_points(self):
        """Gets the data_points of this ScatterSeries.  # noqa: E501

        Gets or sets the values.  # noqa: E501

        :return: The data_points of this ScatterSeries.  # noqa: E501
        :rtype: list[ScatterChartDataPoint]
        """
        return self._data_points

    @data_points.setter
    def data_points(self, data_points):
        """Sets the data_points of this ScatterSeries.

        Gets or sets the values.  # noqa: E501

        :param data_points: The data_points of this ScatterSeries.  # noqa: E501
        :type: list[ScatterChartDataPoint]
        """
        self._data_points = data_points

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
        if not isinstance(other, ScatterSeries):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
