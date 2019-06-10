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

from asposeslidescloud.models.shape_base import ShapeBase

class Chart(ShapeBase):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'self_uri': 'ResourceUri',
        'alternate_links': 'list[ResourceUri]',
        'name': 'str',
        'width': 'float',
        'height': 'float',
        'alternative_text': 'str',
        'hidden': 'bool',
        'x': 'float',
        'y': 'float',
        'z_order_position': 'int',
        'shapes': 'ResourceUriElement',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'type': 'str',
        'shape_type': 'str',
        'chart_type': 'str',
        'series': 'list[Series]',
        'categories': 'list[str]',
        'title': 'ChartTitle',
        'back_wall': 'ChartWall',
        'side_wall': 'ChartWall',
        'floor': 'ChartWall',
        'legend': 'Legend',
        'axes': 'Axes',
        'plot_area': 'PlotArea'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'name': 'Name',
        'width': 'Width',
        'height': 'Height',
        'alternative_text': 'AlternativeText',
        'hidden': 'Hidden',
        'x': 'X',
        'y': 'Y',
        'z_order_position': 'ZOrderPosition',
        'shapes': 'Shapes',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'type': 'Type',
        'shape_type': 'ShapeType',
        'chart_type': 'ChartType',
        'series': 'Series',
        'categories': 'Categories',
        'title': 'Title',
        'back_wall': 'BackWall',
        'side_wall': 'SideWall',
        'floor': 'Floor',
        'legend': 'Legend',
        'axes': 'Axes',
        'plot_area': 'PlotArea'
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, width=None, height=None, alternative_text=None, hidden=None, x=None, y=None, z_order_position=None, shapes=None, fill_format=None, effect_format=None, line_format=None, type='Chart', shape_type='Chart', chart_type=None, series=None, categories=None, title=None, back_wall=None, side_wall=None, floor=None, legend=None, axes=None, plot_area=None):  # noqa: E501
        """Chart - a model defined in Swagger"""  # noqa: E501
        super(Chart, self).__init__(self_uri, alternate_links, name, width, height, alternative_text, hidden, x, y, z_order_position, shapes, fill_format, effect_format, line_format, type, shape_type)

        self._chart_type = None
        self._series = None
        self._categories = None
        self._title = None
        self._back_wall = None
        self._side_wall = None
        self._floor = None
        self._legend = None
        self._axes = None
        self._plot_area = None

        self.chart_type = chart_type
        if series is not None:
            self.series = series
        if categories is not None:
            self.categories = categories
        if title is not None:
            self.title = title
        if back_wall is not None:
            self.back_wall = back_wall
        if side_wall is not None:
            self.side_wall = side_wall
        if floor is not None:
            self.floor = floor
        if legend is not None:
            self.legend = legend
        if axes is not None:
            self.axes = axes
        if plot_area is not None:
            self.plot_area = plot_area

    @property
    def chart_type(self):
        """Gets the chart_type of this Chart.  # noqa: E501

        Gets or sets the type of the chart.  # noqa: E501

        :return: The chart_type of this Chart.  # noqa: E501
        :rtype: str
        """
        return self._chart_type

    @chart_type.setter
    def chart_type(self, chart_type):
        """Sets the chart_type of this Chart.

        Gets or sets the type of the chart.  # noqa: E501

        :param chart_type: The chart_type of this Chart.  # noqa: E501
        :type: str
        """
        if chart_type is not None:
            allowed_values = ["ClusteredColumn", "StackedColumn", "PercentsStackedColumn", "ClusteredColumn3D", "StackedColumn3D", "PercentsStackedColumn3D", "Column3D", "ClusteredCylinder", "StackedCylinder", "PercentsStackedCylinder", "Cylinder3D", "ClusteredCone", "StackedCone", "PercentsStackedCone", "Cone3D", "ClusteredPyramid", "StackedPyramid", "PercentsStackedPyramid", "Pyramid3D", "Line", "StackedLine", "PercentsStackedLine", "LineWithMarkers", "StackedLineWithMarkers", "PercentsStackedLineWithMarkers", "Line3D", "Pie", "Pie3D", "PieOfPie", "ExplodedPie", "ExplodedPie3D", "BarOfPie", "PercentsStackedBar", "ClusteredBar3D", "ClusteredBar", "StackedBar", "StackedBar3D", "PercentsStackedBar3D", "ClusteredHorizontalCylinder", "StackedHorizontalCylinder", "PercentsStackedHorizontalCylinder", "ClusteredHorizontalCone", "StackedHorizontalCone", "PercentsStackedHorizontalCone", "ClusteredHorizontalPyramid", "StackedHorizontalPyramid", "PercentsStackedHorizontalPyramid", "Area", "StackedArea", "PercentsStackedArea", "Area3D", "StackedArea3D", "PercentsStackedArea3D", "ScatterWithMarkers", "ScatterWithSmoothLinesAndMarkers", "ScatterWithSmoothLines", "ScatterWithStraightLinesAndMarkers", "ScatterWithStraightLines", "HighLowClose", "OpenHighLowClose", "VolumeHighLowClose", "VolumeOpenHighLowClose", "Surface3D", "WireframeSurface3D", "Contour", "WireframeContour", "Doughnut", "ExplodedDoughnut", "Bubble", "BubbleWith3D", "Radar", "RadarWithMarkers", "FilledRadar", "SeriesOfMixedTypes"]  # noqa: E501
            if chart_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `chart_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(chart_type, allowed_values)
                )
        self._chart_type = chart_type

    @property
    def series(self):
        """Gets the series of this Chart.  # noqa: E501

        Gets or sets the series of chart data values.  # noqa: E501

        :return: The series of this Chart.  # noqa: E501
        :rtype: list[Series]
        """
        return self._series

    @series.setter
    def series(self, series):
        """Sets the series of this Chart.

        Gets or sets the series of chart data values.  # noqa: E501

        :param series: The series of this Chart.  # noqa: E501
        :type: list[Series]
        """
        self._series = series

    @property
    def categories(self):
        """Gets the categories of this Chart.  # noqa: E501

        Gets or sets the categories for chart data  # noqa: E501

        :return: The categories of this Chart.  # noqa: E501
        :rtype: list[str]
        """
        return self._categories

    @categories.setter
    def categories(self, categories):
        """Sets the categories of this Chart.

        Gets or sets the categories for chart data  # noqa: E501

        :param categories: The categories of this Chart.  # noqa: E501
        :type: list[str]
        """
        self._categories = categories

    @property
    def title(self):
        """Gets the title of this Chart.  # noqa: E501

        Gets or sets the title.  # noqa: E501

        :return: The title of this Chart.  # noqa: E501
        :rtype: ChartTitle
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this Chart.

        Gets or sets the title.  # noqa: E501

        :param title: The title of this Chart.  # noqa: E501
        :type: ChartTitle
        """
        self._title = title

    @property
    def back_wall(self):
        """Gets the back_wall of this Chart.  # noqa: E501

        Gets or sets the back wall.  # noqa: E501

        :return: The back_wall of this Chart.  # noqa: E501
        :rtype: ChartWall
        """
        return self._back_wall

    @back_wall.setter
    def back_wall(self, back_wall):
        """Sets the back_wall of this Chart.

        Gets or sets the back wall.  # noqa: E501

        :param back_wall: The back_wall of this Chart.  # noqa: E501
        :type: ChartWall
        """
        self._back_wall = back_wall

    @property
    def side_wall(self):
        """Gets the side_wall of this Chart.  # noqa: E501

        Gets or sets the side wall.  # noqa: E501

        :return: The side_wall of this Chart.  # noqa: E501
        :rtype: ChartWall
        """
        return self._side_wall

    @side_wall.setter
    def side_wall(self, side_wall):
        """Sets the side_wall of this Chart.

        Gets or sets the side wall.  # noqa: E501

        :param side_wall: The side_wall of this Chart.  # noqa: E501
        :type: ChartWall
        """
        self._side_wall = side_wall

    @property
    def floor(self):
        """Gets the floor of this Chart.  # noqa: E501

        Gets or sets the floor.  # noqa: E501

        :return: The floor of this Chart.  # noqa: E501
        :rtype: ChartWall
        """
        return self._floor

    @floor.setter
    def floor(self, floor):
        """Sets the floor of this Chart.

        Gets or sets the floor.  # noqa: E501

        :param floor: The floor of this Chart.  # noqa: E501
        :type: ChartWall
        """
        self._floor = floor

    @property
    def legend(self):
        """Gets the legend of this Chart.  # noqa: E501

        Gets or sets the legend.  # noqa: E501

        :return: The legend of this Chart.  # noqa: E501
        :rtype: Legend
        """
        return self._legend

    @legend.setter
    def legend(self, legend):
        """Sets the legend of this Chart.

        Gets or sets the legend.  # noqa: E501

        :param legend: The legend of this Chart.  # noqa: E501
        :type: Legend
        """
        self._legend = legend

    @property
    def axes(self):
        """Gets the axes of this Chart.  # noqa: E501

        Gets or sets the axes.  # noqa: E501

        :return: The axes of this Chart.  # noqa: E501
        :rtype: Axes
        """
        return self._axes

    @axes.setter
    def axes(self, axes):
        """Sets the axes of this Chart.

        Gets or sets the axes.  # noqa: E501

        :param axes: The axes of this Chart.  # noqa: E501
        :type: Axes
        """
        self._axes = axes

    @property
    def plot_area(self):
        """Gets the plot_area of this Chart.  # noqa: E501

        Gets or sets the plot area.  # noqa: E501

        :return: The plot_area of this Chart.  # noqa: E501
        :rtype: PlotArea
        """
        return self._plot_area

    @plot_area.setter
    def plot_area(self, plot_area):
        """Sets the plot_area of this Chart.

        Gets or sets the plot area.  # noqa: E501

        :param plot_area: The plot_area of this Chart.  # noqa: E501
        :type: PlotArea
        """
        self._plot_area = plot_area

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
        if not isinstance(other, Chart):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
