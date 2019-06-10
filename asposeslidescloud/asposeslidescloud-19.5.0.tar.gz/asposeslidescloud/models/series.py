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


class Series(object):


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
        'line_format': 'LineFormat'
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
        'line_format': 'LineFormat'
    }

    def __init__(self, type=None, name=None, is_color_varied=None, inverted_solid_fill_color=None, smooth=None, plot_on_second_axis=None, order=None, number_format_of_y_values=None, number_format_of_x_values=None, number_format_of_values=None, number_format_of_bubble_sizes=None, invert_if_negative=None, explosion=None, marker=None, fill_format=None, effect_format=None, line_format=None):  # noqa: E501
        """Series - a model defined in Swagger"""  # noqa: E501

        self._type = None
        self._name = None
        self._is_color_varied = None
        self._inverted_solid_fill_color = None
        self._smooth = None
        self._plot_on_second_axis = None
        self._order = None
        self._number_format_of_y_values = None
        self._number_format_of_x_values = None
        self._number_format_of_values = None
        self._number_format_of_bubble_sizes = None
        self._invert_if_negative = None
        self._explosion = None
        self._marker = None
        self._fill_format = None
        self._effect_format = None
        self._line_format = None

        self.type = type
        if name is not None:
            self.name = name
        self.is_color_varied = is_color_varied
        if inverted_solid_fill_color is not None:
            self.inverted_solid_fill_color = inverted_solid_fill_color
        self.smooth = smooth
        self.plot_on_second_axis = plot_on_second_axis
        self.order = order
        if number_format_of_y_values is not None:
            self.number_format_of_y_values = number_format_of_y_values
        if number_format_of_x_values is not None:
            self.number_format_of_x_values = number_format_of_x_values
        if number_format_of_values is not None:
            self.number_format_of_values = number_format_of_values
        if number_format_of_bubble_sizes is not None:
            self.number_format_of_bubble_sizes = number_format_of_bubble_sizes
        self.invert_if_negative = invert_if_negative
        self.explosion = explosion
        if marker is not None:
            self.marker = marker
        if fill_format is not None:
            self.fill_format = fill_format
        if effect_format is not None:
            self.effect_format = effect_format
        if line_format is not None:
            self.line_format = line_format

    @property
    def type(self):
        """Gets the type of this Series.  # noqa: E501

        Series type.  # noqa: E501

        :return: The type of this Series.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Series.

        Series type.  # noqa: E501

        :param type: The type of this Series.  # noqa: E501
        :type: str
        """
        if type is not None:
            allowed_values = ["ClusteredColumn", "StackedColumn", "PercentsStackedColumn", "ClusteredColumn3D", "StackedColumn3D", "PercentsStackedColumn3D", "Column3D", "ClusteredCylinder", "StackedCylinder", "PercentsStackedCylinder", "Cylinder3D", "ClusteredCone", "StackedCone", "PercentsStackedCone", "Cone3D", "ClusteredPyramid", "StackedPyramid", "PercentsStackedPyramid", "Pyramid3D", "Line", "StackedLine", "PercentsStackedLine", "LineWithMarkers", "StackedLineWithMarkers", "PercentsStackedLineWithMarkers", "Line3D", "Pie", "Pie3D", "PieOfPie", "ExplodedPie", "ExplodedPie3D", "BarOfPie", "PercentsStackedBar", "ClusteredBar3D", "ClusteredBar", "StackedBar", "StackedBar3D", "PercentsStackedBar3D", "ClusteredHorizontalCylinder", "StackedHorizontalCylinder", "PercentsStackedHorizontalCylinder", "ClusteredHorizontalCone", "StackedHorizontalCone", "PercentsStackedHorizontalCone", "ClusteredHorizontalPyramid", "StackedHorizontalPyramid", "PercentsStackedHorizontalPyramid", "Area", "StackedArea", "PercentsStackedArea", "Area3D", "StackedArea3D", "PercentsStackedArea3D", "ScatterWithMarkers", "ScatterWithSmoothLinesAndMarkers", "ScatterWithSmoothLines", "ScatterWithStraightLinesAndMarkers", "ScatterWithStraightLines", "HighLowClose", "OpenHighLowClose", "VolumeHighLowClose", "VolumeOpenHighLowClose", "Surface3D", "WireframeSurface3D", "Contour", "WireframeContour", "Doughnut", "ExplodedDoughnut", "Bubble", "BubbleWith3D", "Radar", "RadarWithMarkers", "FilledRadar", "SeriesOfMixedTypes"]  # noqa: E501
            if type not in allowed_values:
                raise ValueError(
                    "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                    .format(type, allowed_values)
                )
        self._type = type

    @property
    def name(self):
        """Gets the name of this Series.  # noqa: E501

        Series name.  # noqa: E501

        :return: The name of this Series.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Series.

        Series name.  # noqa: E501

        :param name: The name of this Series.  # noqa: E501
        :type: str
        """
        self._name = name

    @property
    def is_color_varied(self):
        """Gets the is_color_varied of this Series.  # noqa: E501

        True if each data marker in the series has a different color.  # noqa: E501

        :return: The is_color_varied of this Series.  # noqa: E501
        :rtype: bool
        """
        return self._is_color_varied

    @is_color_varied.setter
    def is_color_varied(self, is_color_varied):
        """Sets the is_color_varied of this Series.

        True if each data marker in the series has a different color.  # noqa: E501

        :param is_color_varied: The is_color_varied of this Series.  # noqa: E501
        :type: bool
        """
        self._is_color_varied = is_color_varied

    @property
    def inverted_solid_fill_color(self):
        """Gets the inverted_solid_fill_color of this Series.  # noqa: E501

        Invert solid color for the series.  # noqa: E501

        :return: The inverted_solid_fill_color of this Series.  # noqa: E501
        :rtype: str
        """
        return self._inverted_solid_fill_color

    @inverted_solid_fill_color.setter
    def inverted_solid_fill_color(self, inverted_solid_fill_color):
        """Sets the inverted_solid_fill_color of this Series.

        Invert solid color for the series.  # noqa: E501

        :param inverted_solid_fill_color: The inverted_solid_fill_color of this Series.  # noqa: E501
        :type: str
        """
        self._inverted_solid_fill_color = inverted_solid_fill_color

    @property
    def smooth(self):
        """Gets the smooth of this Series.  # noqa: E501

        True if curve smoothing is turned on. Applies only to line and scatter connected by lines charts.  # noqa: E501

        :return: The smooth of this Series.  # noqa: E501
        :rtype: bool
        """
        return self._smooth

    @smooth.setter
    def smooth(self, smooth):
        """Sets the smooth of this Series.

        True if curve smoothing is turned on. Applies only to line and scatter connected by lines charts.  # noqa: E501

        :param smooth: The smooth of this Series.  # noqa: E501
        :type: bool
        """
        self._smooth = smooth

    @property
    def plot_on_second_axis(self):
        """Gets the plot_on_second_axis of this Series.  # noqa: E501

        True if the series is plotted on second value axis.  # noqa: E501

        :return: The plot_on_second_axis of this Series.  # noqa: E501
        :rtype: bool
        """
        return self._plot_on_second_axis

    @plot_on_second_axis.setter
    def plot_on_second_axis(self, plot_on_second_axis):
        """Sets the plot_on_second_axis of this Series.

        True if the series is plotted on second value axis.  # noqa: E501

        :param plot_on_second_axis: The plot_on_second_axis of this Series.  # noqa: E501
        :type: bool
        """
        self._plot_on_second_axis = plot_on_second_axis

    @property
    def order(self):
        """Gets the order of this Series.  # noqa: E501

        Series order.  # noqa: E501

        :return: The order of this Series.  # noqa: E501
        :rtype: int
        """
        return self._order

    @order.setter
    def order(self, order):
        """Sets the order of this Series.

        Series order.  # noqa: E501

        :param order: The order of this Series.  # noqa: E501
        :type: int
        """
        self._order = order

    @property
    def number_format_of_y_values(self):
        """Gets the number_format_of_y_values of this Series.  # noqa: E501

        The number format for the series y values.  # noqa: E501

        :return: The number_format_of_y_values of this Series.  # noqa: E501
        :rtype: str
        """
        return self._number_format_of_y_values

    @number_format_of_y_values.setter
    def number_format_of_y_values(self, number_format_of_y_values):
        """Sets the number_format_of_y_values of this Series.

        The number format for the series y values.  # noqa: E501

        :param number_format_of_y_values: The number_format_of_y_values of this Series.  # noqa: E501
        :type: str
        """
        self._number_format_of_y_values = number_format_of_y_values

    @property
    def number_format_of_x_values(self):
        """Gets the number_format_of_x_values of this Series.  # noqa: E501

        The number format for the series x values.  # noqa: E501

        :return: The number_format_of_x_values of this Series.  # noqa: E501
        :rtype: str
        """
        return self._number_format_of_x_values

    @number_format_of_x_values.setter
    def number_format_of_x_values(self, number_format_of_x_values):
        """Sets the number_format_of_x_values of this Series.

        The number format for the series x values.  # noqa: E501

        :param number_format_of_x_values: The number_format_of_x_values of this Series.  # noqa: E501
        :type: str
        """
        self._number_format_of_x_values = number_format_of_x_values

    @property
    def number_format_of_values(self):
        """Gets the number_format_of_values of this Series.  # noqa: E501

        The number format for the series values.  # noqa: E501

        :return: The number_format_of_values of this Series.  # noqa: E501
        :rtype: str
        """
        return self._number_format_of_values

    @number_format_of_values.setter
    def number_format_of_values(self, number_format_of_values):
        """Sets the number_format_of_values of this Series.

        The number format for the series values.  # noqa: E501

        :param number_format_of_values: The number_format_of_values of this Series.  # noqa: E501
        :type: str
        """
        self._number_format_of_values = number_format_of_values

    @property
    def number_format_of_bubble_sizes(self):
        """Gets the number_format_of_bubble_sizes of this Series.  # noqa: E501

        The number format for the series bubble sizes.  # noqa: E501

        :return: The number_format_of_bubble_sizes of this Series.  # noqa: E501
        :rtype: str
        """
        return self._number_format_of_bubble_sizes

    @number_format_of_bubble_sizes.setter
    def number_format_of_bubble_sizes(self, number_format_of_bubble_sizes):
        """Sets the number_format_of_bubble_sizes of this Series.

        The number format for the series bubble sizes.  # noqa: E501

        :param number_format_of_bubble_sizes: The number_format_of_bubble_sizes of this Series.  # noqa: E501
        :type: str
        """
        self._number_format_of_bubble_sizes = number_format_of_bubble_sizes

    @property
    def invert_if_negative(self):
        """Gets the invert_if_negative of this Series.  # noqa: E501

        True if the series shall invert its colors if the value is negative. Applies to bar, column and bubble series.  # noqa: E501

        :return: The invert_if_negative of this Series.  # noqa: E501
        :rtype: bool
        """
        return self._invert_if_negative

    @invert_if_negative.setter
    def invert_if_negative(self, invert_if_negative):
        """Sets the invert_if_negative of this Series.

        True if the series shall invert its colors if the value is negative. Applies to bar, column and bubble series.  # noqa: E501

        :param invert_if_negative: The invert_if_negative of this Series.  # noqa: E501
        :type: bool
        """
        self._invert_if_negative = invert_if_negative

    @property
    def explosion(self):
        """Gets the explosion of this Series.  # noqa: E501

        The distance of an open pie slice from the center of the pie chart is expressed as a percentage of the pie diameter.  # noqa: E501

        :return: The explosion of this Series.  # noqa: E501
        :rtype: int
        """
        return self._explosion

    @explosion.setter
    def explosion(self, explosion):
        """Sets the explosion of this Series.

        The distance of an open pie slice from the center of the pie chart is expressed as a percentage of the pie diameter.  # noqa: E501

        :param explosion: The explosion of this Series.  # noqa: E501
        :type: int
        """
        self._explosion = explosion

    @property
    def marker(self):
        """Gets the marker of this Series.  # noqa: E501

        Series marker.  # noqa: E501

        :return: The marker of this Series.  # noqa: E501
        :rtype: SeriesMarker
        """
        return self._marker

    @marker.setter
    def marker(self, marker):
        """Sets the marker of this Series.

        Series marker.  # noqa: E501

        :param marker: The marker of this Series.  # noqa: E501
        :type: SeriesMarker
        """
        self._marker = marker

    @property
    def fill_format(self):
        """Gets the fill_format of this Series.  # noqa: E501

        Fill properties set for the series.  # noqa: E501

        :return: The fill_format of this Series.  # noqa: E501
        :rtype: FillFormat
        """
        return self._fill_format

    @fill_format.setter
    def fill_format(self, fill_format):
        """Sets the fill_format of this Series.

        Fill properties set for the series.  # noqa: E501

        :param fill_format: The fill_format of this Series.  # noqa: E501
        :type: FillFormat
        """
        self._fill_format = fill_format

    @property
    def effect_format(self):
        """Gets the effect_format of this Series.  # noqa: E501

        Effect properties set for the series.  # noqa: E501

        :return: The effect_format of this Series.  # noqa: E501
        :rtype: EffectFormat
        """
        return self._effect_format

    @effect_format.setter
    def effect_format(self, effect_format):
        """Sets the effect_format of this Series.

        Effect properties set for the series.  # noqa: E501

        :param effect_format: The effect_format of this Series.  # noqa: E501
        :type: EffectFormat
        """
        self._effect_format = effect_format

    @property
    def line_format(self):
        """Gets the line_format of this Series.  # noqa: E501

        Line properties set for the series.  # noqa: E501

        :return: The line_format of this Series.  # noqa: E501
        :rtype: LineFormat
        """
        return self._line_format

    @line_format.setter
    def line_format(self, line_format):
        """Sets the line_format of this Series.

        Line properties set for the series.  # noqa: E501

        :param line_format: The line_format of this Series.  # noqa: E501
        :type: LineFormat
        """
        self._line_format = line_format

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
        if not isinstance(other, Series):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
