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


class Axis(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'is_visible': 'bool',
        'has_title': 'bool',
        'position': 'str',
        'display_unit': 'str',
        'base_unit_scale': 'str',
        'is_automatic_major_unit': 'bool',
        'major_unit': 'float',
        'major_unit_scale': 'str',
        'major_tick_mark': 'str',
        'is_automatic_minor_unit': 'bool',
        'minor_unit': 'float',
        'minor_unit_scale': 'str',
        'minor_tick_mark': 'str',
        'is_automatic_max_value': 'bool',
        'max_value': 'float',
        'is_automatic_min_value': 'bool',
        'min_value': 'float',
        'is_logarithmic': 'bool',
        'log_base': 'float',
        'category_axis_type': 'str',
        'axis_between_categories': 'bool',
        'label_offset': 'int',
        'is_plot_order_reversed': 'bool',
        'is_number_format_linked_to_source': 'bool',
        'number_format': 'str',
        'cross_type': 'str',
        'cross_at': 'float',
        'is_automatic_tick_marks_spacing': 'bool',
        'tick_marks_spacing': 'int',
        'is_automatic_tick_label_spacing': 'bool',
        'tick_label_spacing': 'int',
        'tick_label_position': 'str',
        'tick_label_rotation_angle': 'float',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat'
    }

    attribute_map = {
        'is_visible': 'IsVisible',
        'has_title': 'HasTitle',
        'position': 'Position',
        'display_unit': 'DisplayUnit',
        'base_unit_scale': 'BaseUnitScale',
        'is_automatic_major_unit': 'IsAutomaticMajorUnit',
        'major_unit': 'MajorUnit',
        'major_unit_scale': 'MajorUnitScale',
        'major_tick_mark': 'MajorTickMark',
        'is_automatic_minor_unit': 'IsAutomaticMinorUnit',
        'minor_unit': 'MinorUnit',
        'minor_unit_scale': 'MinorUnitScale',
        'minor_tick_mark': 'MinorTickMark',
        'is_automatic_max_value': 'IsAutomaticMaxValue',
        'max_value': 'MaxValue',
        'is_automatic_min_value': 'IsAutomaticMinValue',
        'min_value': 'MinValue',
        'is_logarithmic': 'IsLogarithmic',
        'log_base': 'LogBase',
        'category_axis_type': 'CategoryAxisType',
        'axis_between_categories': 'AxisBetweenCategories',
        'label_offset': 'LabelOffset',
        'is_plot_order_reversed': 'IsPlotOrderReversed',
        'is_number_format_linked_to_source': 'IsNumberFormatLinkedToSource',
        'number_format': 'NumberFormat',
        'cross_type': 'CrossType',
        'cross_at': 'CrossAt',
        'is_automatic_tick_marks_spacing': 'IsAutomaticTickMarksSpacing',
        'tick_marks_spacing': 'TickMarksSpacing',
        'is_automatic_tick_label_spacing': 'IsAutomaticTickLabelSpacing',
        'tick_label_spacing': 'TickLabelSpacing',
        'tick_label_position': 'TickLabelPosition',
        'tick_label_rotation_angle': 'TickLabelRotationAngle',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat'
    }

    def __init__(self, is_visible=None, has_title=None, position=None, display_unit=None, base_unit_scale=None, is_automatic_major_unit=None, major_unit=None, major_unit_scale=None, major_tick_mark=None, is_automatic_minor_unit=None, minor_unit=None, minor_unit_scale=None, minor_tick_mark=None, is_automatic_max_value=None, max_value=None, is_automatic_min_value=None, min_value=None, is_logarithmic=None, log_base=None, category_axis_type=None, axis_between_categories=None, label_offset=None, is_plot_order_reversed=None, is_number_format_linked_to_source=None, number_format=None, cross_type=None, cross_at=None, is_automatic_tick_marks_spacing=None, tick_marks_spacing=None, is_automatic_tick_label_spacing=None, tick_label_spacing=None, tick_label_position=None, tick_label_rotation_angle=None, fill_format=None, effect_format=None, line_format=None):  # noqa: E501
        """Axis - a model defined in Swagger"""  # noqa: E501

        self._is_visible = None
        self._has_title = None
        self._position = None
        self._display_unit = None
        self._base_unit_scale = None
        self._is_automatic_major_unit = None
        self._major_unit = None
        self._major_unit_scale = None
        self._major_tick_mark = None
        self._is_automatic_minor_unit = None
        self._minor_unit = None
        self._minor_unit_scale = None
        self._minor_tick_mark = None
        self._is_automatic_max_value = None
        self._max_value = None
        self._is_automatic_min_value = None
        self._min_value = None
        self._is_logarithmic = None
        self._log_base = None
        self._category_axis_type = None
        self._axis_between_categories = None
        self._label_offset = None
        self._is_plot_order_reversed = None
        self._is_number_format_linked_to_source = None
        self._number_format = None
        self._cross_type = None
        self._cross_at = None
        self._is_automatic_tick_marks_spacing = None
        self._tick_marks_spacing = None
        self._is_automatic_tick_label_spacing = None
        self._tick_label_spacing = None
        self._tick_label_position = None
        self._tick_label_rotation_angle = None
        self._fill_format = None
        self._effect_format = None
        self._line_format = None

        self.is_visible = is_visible
        self.has_title = has_title
        self.position = position
        self.display_unit = display_unit
        self.base_unit_scale = base_unit_scale
        self.is_automatic_major_unit = is_automatic_major_unit
        self.major_unit = major_unit
        self.major_unit_scale = major_unit_scale
        self.major_tick_mark = major_tick_mark
        self.is_automatic_minor_unit = is_automatic_minor_unit
        self.minor_unit = minor_unit
        self.minor_unit_scale = minor_unit_scale
        self.minor_tick_mark = minor_tick_mark
        self.is_automatic_max_value = is_automatic_max_value
        self.max_value = max_value
        self.is_automatic_min_value = is_automatic_min_value
        self.min_value = min_value
        self.is_logarithmic = is_logarithmic
        self.log_base = log_base
        self.category_axis_type = category_axis_type
        self.axis_between_categories = axis_between_categories
        self.label_offset = label_offset
        self.is_plot_order_reversed = is_plot_order_reversed
        self.is_number_format_linked_to_source = is_number_format_linked_to_source
        if number_format is not None:
            self.number_format = number_format
        self.cross_type = cross_type
        self.cross_at = cross_at
        self.is_automatic_tick_marks_spacing = is_automatic_tick_marks_spacing
        self.tick_marks_spacing = tick_marks_spacing
        self.is_automatic_tick_label_spacing = is_automatic_tick_label_spacing
        self.tick_label_spacing = tick_label_spacing
        self.tick_label_position = tick_label_position
        self.tick_label_rotation_angle = tick_label_rotation_angle
        if fill_format is not None:
            self.fill_format = fill_format
        if effect_format is not None:
            self.effect_format = effect_format
        if line_format is not None:
            self.line_format = line_format

    @property
    def is_visible(self):
        """Gets the is_visible of this Axis.  # noqa: E501

        True if the axis is visible  # noqa: E501

        :return: The is_visible of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._is_visible

    @is_visible.setter
    def is_visible(self, is_visible):
        """Sets the is_visible of this Axis.

        True if the axis is visible  # noqa: E501

        :param is_visible: The is_visible of this Axis.  # noqa: E501
        :type: bool
        """
        self._is_visible = is_visible

    @property
    def has_title(self):
        """Gets the has_title of this Axis.  # noqa: E501

        True if the axis has a visible title  # noqa: E501

        :return: The has_title of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._has_title

    @has_title.setter
    def has_title(self, has_title):
        """Sets the has_title of this Axis.

        True if the axis has a visible title  # noqa: E501

        :param has_title: The has_title of this Axis.  # noqa: E501
        :type: bool
        """
        self._has_title = has_title

    @property
    def position(self):
        """Gets the position of this Axis.  # noqa: E501

        Axis position  # noqa: E501

        :return: The position of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._position

    @position.setter
    def position(self, position):
        """Sets the position of this Axis.

        Axis position  # noqa: E501

        :param position: The position of this Axis.  # noqa: E501
        :type: str
        """
        if position is not None:
            allowed_values = ["Bottom", "Left", "Right", "Top"]  # noqa: E501
            if position not in allowed_values:
                raise ValueError(
                    "Invalid value for `position` ({0}), must be one of {1}"  # noqa: E501
                    .format(position, allowed_values)
                )
        self._position = position

    @property
    def display_unit(self):
        """Gets the display_unit of this Axis.  # noqa: E501

        The scaling value of the display units for the value axis  # noqa: E501

        :return: The display_unit of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._display_unit

    @display_unit.setter
    def display_unit(self, display_unit):
        """Sets the display_unit of this Axis.

        The scaling value of the display units for the value axis  # noqa: E501

        :param display_unit: The display_unit of this Axis.  # noqa: E501
        :type: str
        """
        if display_unit is not None:
            allowed_values = ["None", "Hundreds", "Thousands", "TenThousands", "HundredThousands", "Millions", "TenMillions", "HundredMillions", "Billions", "Trillions", "CustomValue"]  # noqa: E501
            if display_unit not in allowed_values:
                raise ValueError(
                    "Invalid value for `display_unit` ({0}), must be one of {1}"  # noqa: E501
                    .format(display_unit, allowed_values)
                )
        self._display_unit = display_unit

    @property
    def base_unit_scale(self):
        """Gets the base_unit_scale of this Axis.  # noqa: E501

        The smallest time unit that is represented on the date axis  # noqa: E501

        :return: The base_unit_scale of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._base_unit_scale

    @base_unit_scale.setter
    def base_unit_scale(self, base_unit_scale):
        """Sets the base_unit_scale of this Axis.

        The smallest time unit that is represented on the date axis  # noqa: E501

        :param base_unit_scale: The base_unit_scale of this Axis.  # noqa: E501
        :type: str
        """
        if base_unit_scale is not None:
            allowed_values = ["Days", "Months", "Years"]  # noqa: E501
            if base_unit_scale not in allowed_values:
                raise ValueError(
                    "Invalid value for `base_unit_scale` ({0}), must be one of {1}"  # noqa: E501
                    .format(base_unit_scale, allowed_values)
                )
        self._base_unit_scale = base_unit_scale

    @property
    def is_automatic_major_unit(self):
        """Gets the is_automatic_major_unit of this Axis.  # noqa: E501

        True the major unit of the axis is automatically assigned  # noqa: E501

        :return: The is_automatic_major_unit of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._is_automatic_major_unit

    @is_automatic_major_unit.setter
    def is_automatic_major_unit(self, is_automatic_major_unit):
        """Sets the is_automatic_major_unit of this Axis.

        True the major unit of the axis is automatically assigned  # noqa: E501

        :param is_automatic_major_unit: The is_automatic_major_unit of this Axis.  # noqa: E501
        :type: bool
        """
        self._is_automatic_major_unit = is_automatic_major_unit

    @property
    def major_unit(self):
        """Gets the major_unit of this Axis.  # noqa: E501

        The major units for the date or value axis  # noqa: E501

        :return: The major_unit of this Axis.  # noqa: E501
        :rtype: float
        """
        return self._major_unit

    @major_unit.setter
    def major_unit(self, major_unit):
        """Sets the major_unit of this Axis.

        The major units for the date or value axis  # noqa: E501

        :param major_unit: The major_unit of this Axis.  # noqa: E501
        :type: float
        """
        self._major_unit = major_unit

    @property
    def major_unit_scale(self):
        """Gets the major_unit_scale of this Axis.  # noqa: E501

        The major unit scale for the date axis  # noqa: E501

        :return: The major_unit_scale of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._major_unit_scale

    @major_unit_scale.setter
    def major_unit_scale(self, major_unit_scale):
        """Sets the major_unit_scale of this Axis.

        The major unit scale for the date axis  # noqa: E501

        :param major_unit_scale: The major_unit_scale of this Axis.  # noqa: E501
        :type: str
        """
        if major_unit_scale is not None:
            allowed_values = ["Days", "Months", "Years"]  # noqa: E501
            if major_unit_scale not in allowed_values:
                raise ValueError(
                    "Invalid value for `major_unit_scale` ({0}), must be one of {1}"  # noqa: E501
                    .format(major_unit_scale, allowed_values)
                )
        self._major_unit_scale = major_unit_scale

    @property
    def major_tick_mark(self):
        """Gets the major_tick_mark of this Axis.  # noqa: E501

        The type of major tick mark for the specified axis  # noqa: E501

        :return: The major_tick_mark of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._major_tick_mark

    @major_tick_mark.setter
    def major_tick_mark(self, major_tick_mark):
        """Sets the major_tick_mark of this Axis.

        The type of major tick mark for the specified axis  # noqa: E501

        :param major_tick_mark: The major_tick_mark of this Axis.  # noqa: E501
        :type: str
        """
        if major_tick_mark is not None:
            allowed_values = ["Cross", "Inside", "None", "Outside"]  # noqa: E501
            if major_tick_mark not in allowed_values:
                raise ValueError(
                    "Invalid value for `major_tick_mark` ({0}), must be one of {1}"  # noqa: E501
                    .format(major_tick_mark, allowed_values)
                )
        self._major_tick_mark = major_tick_mark

    @property
    def is_automatic_minor_unit(self):
        """Gets the is_automatic_minor_unit of this Axis.  # noqa: E501

        True the minor unit of the axis is automatically assigned  # noqa: E501

        :return: The is_automatic_minor_unit of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._is_automatic_minor_unit

    @is_automatic_minor_unit.setter
    def is_automatic_minor_unit(self, is_automatic_minor_unit):
        """Sets the is_automatic_minor_unit of this Axis.

        True the minor unit of the axis is automatically assigned  # noqa: E501

        :param is_automatic_minor_unit: The is_automatic_minor_unit of this Axis.  # noqa: E501
        :type: bool
        """
        self._is_automatic_minor_unit = is_automatic_minor_unit

    @property
    def minor_unit(self):
        """Gets the minor_unit of this Axis.  # noqa: E501

        The minor units for the date or value axis  # noqa: E501

        :return: The minor_unit of this Axis.  # noqa: E501
        :rtype: float
        """
        return self._minor_unit

    @minor_unit.setter
    def minor_unit(self, minor_unit):
        """Sets the minor_unit of this Axis.

        The minor units for the date or value axis  # noqa: E501

        :param minor_unit: The minor_unit of this Axis.  # noqa: E501
        :type: float
        """
        self._minor_unit = minor_unit

    @property
    def minor_unit_scale(self):
        """Gets the minor_unit_scale of this Axis.  # noqa: E501

        The minor unit scale for the date axis  # noqa: E501

        :return: The minor_unit_scale of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._minor_unit_scale

    @minor_unit_scale.setter
    def minor_unit_scale(self, minor_unit_scale):
        """Sets the minor_unit_scale of this Axis.

        The minor unit scale for the date axis  # noqa: E501

        :param minor_unit_scale: The minor_unit_scale of this Axis.  # noqa: E501
        :type: str
        """
        if minor_unit_scale is not None:
            allowed_values = ["Days", "Months", "Years"]  # noqa: E501
            if minor_unit_scale not in allowed_values:
                raise ValueError(
                    "Invalid value for `minor_unit_scale` ({0}), must be one of {1}"  # noqa: E501
                    .format(minor_unit_scale, allowed_values)
                )
        self._minor_unit_scale = minor_unit_scale

    @property
    def minor_tick_mark(self):
        """Gets the minor_tick_mark of this Axis.  # noqa: E501

        The type of minor tick mark for the specified axis  # noqa: E501

        :return: The minor_tick_mark of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._minor_tick_mark

    @minor_tick_mark.setter
    def minor_tick_mark(self, minor_tick_mark):
        """Sets the minor_tick_mark of this Axis.

        The type of minor tick mark for the specified axis  # noqa: E501

        :param minor_tick_mark: The minor_tick_mark of this Axis.  # noqa: E501
        :type: str
        """
        if minor_tick_mark is not None:
            allowed_values = ["Cross", "Inside", "None", "Outside"]  # noqa: E501
            if minor_tick_mark not in allowed_values:
                raise ValueError(
                    "Invalid value for `minor_tick_mark` ({0}), must be one of {1}"  # noqa: E501
                    .format(minor_tick_mark, allowed_values)
                )
        self._minor_tick_mark = minor_tick_mark

    @property
    def is_automatic_max_value(self):
        """Gets the is_automatic_max_value of this Axis.  # noqa: E501

        True if the max value is automatically assigned  # noqa: E501

        :return: The is_automatic_max_value of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._is_automatic_max_value

    @is_automatic_max_value.setter
    def is_automatic_max_value(self, is_automatic_max_value):
        """Sets the is_automatic_max_value of this Axis.

        True if the max value is automatically assigned  # noqa: E501

        :param is_automatic_max_value: The is_automatic_max_value of this Axis.  # noqa: E501
        :type: bool
        """
        self._is_automatic_max_value = is_automatic_max_value

    @property
    def max_value(self):
        """Gets the max_value of this Axis.  # noqa: E501

        The maximum value on the value axis  # noqa: E501

        :return: The max_value of this Axis.  # noqa: E501
        :rtype: float
        """
        return self._max_value

    @max_value.setter
    def max_value(self, max_value):
        """Sets the max_value of this Axis.

        The maximum value on the value axis  # noqa: E501

        :param max_value: The max_value of this Axis.  # noqa: E501
        :type: float
        """
        self._max_value = max_value

    @property
    def is_automatic_min_value(self):
        """Gets the is_automatic_min_value of this Axis.  # noqa: E501

        True if the min value is automatically assigned  # noqa: E501

        :return: The is_automatic_min_value of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._is_automatic_min_value

    @is_automatic_min_value.setter
    def is_automatic_min_value(self, is_automatic_min_value):
        """Sets the is_automatic_min_value of this Axis.

        True if the min value is automatically assigned  # noqa: E501

        :param is_automatic_min_value: The is_automatic_min_value of this Axis.  # noqa: E501
        :type: bool
        """
        self._is_automatic_min_value = is_automatic_min_value

    @property
    def min_value(self):
        """Gets the min_value of this Axis.  # noqa: E501

        The minimum value on the value axis  # noqa: E501

        :return: The min_value of this Axis.  # noqa: E501
        :rtype: float
        """
        return self._min_value

    @min_value.setter
    def min_value(self, min_value):
        """Sets the min_value of this Axis.

        The minimum value on the value axis  # noqa: E501

        :param min_value: The min_value of this Axis.  # noqa: E501
        :type: float
        """
        self._min_value = min_value

    @property
    def is_logarithmic(self):
        """Gets the is_logarithmic of this Axis.  # noqa: E501

        True if the value axis scale type is logarithmic  # noqa: E501

        :return: The is_logarithmic of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._is_logarithmic

    @is_logarithmic.setter
    def is_logarithmic(self, is_logarithmic):
        """Sets the is_logarithmic of this Axis.

        True if the value axis scale type is logarithmic  # noqa: E501

        :param is_logarithmic: The is_logarithmic of this Axis.  # noqa: E501
        :type: bool
        """
        self._is_logarithmic = is_logarithmic

    @property
    def log_base(self):
        """Gets the log_base of this Axis.  # noqa: E501

        The logarithmic base. Default value is 10  # noqa: E501

        :return: The log_base of this Axis.  # noqa: E501
        :rtype: float
        """
        return self._log_base

    @log_base.setter
    def log_base(self, log_base):
        """Sets the log_base of this Axis.

        The logarithmic base. Default value is 10  # noqa: E501

        :param log_base: The log_base of this Axis.  # noqa: E501
        :type: float
        """
        self._log_base = log_base

    @property
    def category_axis_type(self):
        """Gets the category_axis_type of this Axis.  # noqa: E501

        The type of the category axis  # noqa: E501

        :return: The category_axis_type of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._category_axis_type

    @category_axis_type.setter
    def category_axis_type(self, category_axis_type):
        """Sets the category_axis_type of this Axis.

        The type of the category axis  # noqa: E501

        :param category_axis_type: The category_axis_type of this Axis.  # noqa: E501
        :type: str
        """
        if category_axis_type is not None:
            allowed_values = ["Text", "Date"]  # noqa: E501
            if category_axis_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `category_axis_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(category_axis_type, allowed_values)
                )
        self._category_axis_type = category_axis_type

    @property
    def axis_between_categories(self):
        """Gets the axis_between_categories of this Axis.  # noqa: E501

        True if the value axis crosses the category axis between categories. This property applies only to category axes, and it doesn't apply to 3-D charts  # noqa: E501

        :return: The axis_between_categories of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._axis_between_categories

    @axis_between_categories.setter
    def axis_between_categories(self, axis_between_categories):
        """Sets the axis_between_categories of this Axis.

        True if the value axis crosses the category axis between categories. This property applies only to category axes, and it doesn't apply to 3-D charts  # noqa: E501

        :param axis_between_categories: The axis_between_categories of this Axis.  # noqa: E501
        :type: bool
        """
        self._axis_between_categories = axis_between_categories

    @property
    def label_offset(self):
        """Gets the label_offset of this Axis.  # noqa: E501

        The distance of labels from the axis. Applied to category or date axis. Value must be between 0% and 1000%.               # noqa: E501

        :return: The label_offset of this Axis.  # noqa: E501
        :rtype: int
        """
        return self._label_offset

    @label_offset.setter
    def label_offset(self, label_offset):
        """Sets the label_offset of this Axis.

        The distance of labels from the axis. Applied to category or date axis. Value must be between 0% and 1000%.               # noqa: E501

        :param label_offset: The label_offset of this Axis.  # noqa: E501
        :type: int
        """
        self._label_offset = label_offset

    @property
    def is_plot_order_reversed(self):
        """Gets the is_plot_order_reversed of this Axis.  # noqa: E501

        True if MS PowerPoint plots data points from last to first  # noqa: E501

        :return: The is_plot_order_reversed of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._is_plot_order_reversed

    @is_plot_order_reversed.setter
    def is_plot_order_reversed(self, is_plot_order_reversed):
        """Sets the is_plot_order_reversed of this Axis.

        True if MS PowerPoint plots data points from last to first  # noqa: E501

        :param is_plot_order_reversed: The is_plot_order_reversed of this Axis.  # noqa: E501
        :type: bool
        """
        self._is_plot_order_reversed = is_plot_order_reversed

    @property
    def is_number_format_linked_to_source(self):
        """Gets the is_number_format_linked_to_source of this Axis.  # noqa: E501

        True if the format is linked to source data  # noqa: E501

        :return: The is_number_format_linked_to_source of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._is_number_format_linked_to_source

    @is_number_format_linked_to_source.setter
    def is_number_format_linked_to_source(self, is_number_format_linked_to_source):
        """Sets the is_number_format_linked_to_source of this Axis.

        True if the format is linked to source data  # noqa: E501

        :param is_number_format_linked_to_source: The is_number_format_linked_to_source of this Axis.  # noqa: E501
        :type: bool
        """
        self._is_number_format_linked_to_source = is_number_format_linked_to_source

    @property
    def number_format(self):
        """Gets the number_format of this Axis.  # noqa: E501

        the format string for the Axis Labels  # noqa: E501

        :return: The number_format of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._number_format

    @number_format.setter
    def number_format(self, number_format):
        """Sets the number_format of this Axis.

        the format string for the Axis Labels  # noqa: E501

        :param number_format: The number_format of this Axis.  # noqa: E501
        :type: str
        """
        self._number_format = number_format

    @property
    def cross_type(self):
        """Gets the cross_type of this Axis.  # noqa: E501

        The CrossType on the specified axis where the other axis crosses  # noqa: E501

        :return: The cross_type of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._cross_type

    @cross_type.setter
    def cross_type(self, cross_type):
        """Sets the cross_type of this Axis.

        The CrossType on the specified axis where the other axis crosses  # noqa: E501

        :param cross_type: The cross_type of this Axis.  # noqa: E501
        :type: str
        """
        if cross_type is not None:
            allowed_values = ["AxisCrossesAtZero", "Maximum", "Custom"]  # noqa: E501
            if cross_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `cross_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(cross_type, allowed_values)
                )
        self._cross_type = cross_type

    @property
    def cross_at(self):
        """Gets the cross_at of this Axis.  # noqa: E501

        The point on the axis where the perpendicular axis crosses it  # noqa: E501

        :return: The cross_at of this Axis.  # noqa: E501
        :rtype: float
        """
        return self._cross_at

    @cross_at.setter
    def cross_at(self, cross_at):
        """Sets the cross_at of this Axis.

        The point on the axis where the perpendicular axis crosses it  # noqa: E501

        :param cross_at: The cross_at of this Axis.  # noqa: E501
        :type: float
        """
        self._cross_at = cross_at

    @property
    def is_automatic_tick_marks_spacing(self):
        """Gets the is_automatic_tick_marks_spacing of this Axis.  # noqa: E501

        True for automatic tick marks spacing value  # noqa: E501

        :return: The is_automatic_tick_marks_spacing of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._is_automatic_tick_marks_spacing

    @is_automatic_tick_marks_spacing.setter
    def is_automatic_tick_marks_spacing(self, is_automatic_tick_marks_spacing):
        """Sets the is_automatic_tick_marks_spacing of this Axis.

        True for automatic tick marks spacing value  # noqa: E501

        :param is_automatic_tick_marks_spacing: The is_automatic_tick_marks_spacing of this Axis.  # noqa: E501
        :type: bool
        """
        self._is_automatic_tick_marks_spacing = is_automatic_tick_marks_spacing

    @property
    def tick_marks_spacing(self):
        """Gets the tick_marks_spacing of this Axis.  # noqa: E501

        Specifies how many tick marks shall be skipped before the next one shall be drawn. Applied to category or series axis.  # noqa: E501

        :return: The tick_marks_spacing of this Axis.  # noqa: E501
        :rtype: int
        """
        return self._tick_marks_spacing

    @tick_marks_spacing.setter
    def tick_marks_spacing(self, tick_marks_spacing):
        """Sets the tick_marks_spacing of this Axis.

        Specifies how many tick marks shall be skipped before the next one shall be drawn. Applied to category or series axis.  # noqa: E501

        :param tick_marks_spacing: The tick_marks_spacing of this Axis.  # noqa: E501
        :type: int
        """
        self._tick_marks_spacing = tick_marks_spacing

    @property
    def is_automatic_tick_label_spacing(self):
        """Gets the is_automatic_tick_label_spacing of this Axis.  # noqa: E501

        True for automatic tick label spacing value  # noqa: E501

        :return: The is_automatic_tick_label_spacing of this Axis.  # noqa: E501
        :rtype: bool
        """
        return self._is_automatic_tick_label_spacing

    @is_automatic_tick_label_spacing.setter
    def is_automatic_tick_label_spacing(self, is_automatic_tick_label_spacing):
        """Sets the is_automatic_tick_label_spacing of this Axis.

        True for automatic tick label spacing value  # noqa: E501

        :param is_automatic_tick_label_spacing: The is_automatic_tick_label_spacing of this Axis.  # noqa: E501
        :type: bool
        """
        self._is_automatic_tick_label_spacing = is_automatic_tick_label_spacing

    @property
    def tick_label_spacing(self):
        """Gets the tick_label_spacing of this Axis.  # noqa: E501

        Specifies how many tick labels to skip between label that is drawn.  # noqa: E501

        :return: The tick_label_spacing of this Axis.  # noqa: E501
        :rtype: int
        """
        return self._tick_label_spacing

    @tick_label_spacing.setter
    def tick_label_spacing(self, tick_label_spacing):
        """Sets the tick_label_spacing of this Axis.

        Specifies how many tick labels to skip between label that is drawn.  # noqa: E501

        :param tick_label_spacing: The tick_label_spacing of this Axis.  # noqa: E501
        :type: int
        """
        self._tick_label_spacing = tick_label_spacing

    @property
    def tick_label_position(self):
        """Gets the tick_label_position of this Axis.  # noqa: E501

        The position of tick-mark labels on the specified axis.  # noqa: E501

        :return: The tick_label_position of this Axis.  # noqa: E501
        :rtype: str
        """
        return self._tick_label_position

    @tick_label_position.setter
    def tick_label_position(self, tick_label_position):
        """Sets the tick_label_position of this Axis.

        The position of tick-mark labels on the specified axis.  # noqa: E501

        :param tick_label_position: The tick_label_position of this Axis.  # noqa: E501
        :type: str
        """
        if tick_label_position is not None:
            allowed_values = ["High", "Low", "NextTo", "None"]  # noqa: E501
            if tick_label_position not in allowed_values:
                raise ValueError(
                    "Invalid value for `tick_label_position` ({0}), must be one of {1}"  # noqa: E501
                    .format(tick_label_position, allowed_values)
                )
        self._tick_label_position = tick_label_position

    @property
    def tick_label_rotation_angle(self):
        """Gets the tick_label_rotation_angle of this Axis.  # noqa: E501

        Represents the rotation angle of tick labels.  # noqa: E501

        :return: The tick_label_rotation_angle of this Axis.  # noqa: E501
        :rtype: float
        """
        return self._tick_label_rotation_angle

    @tick_label_rotation_angle.setter
    def tick_label_rotation_angle(self, tick_label_rotation_angle):
        """Sets the tick_label_rotation_angle of this Axis.

        Represents the rotation angle of tick labels.  # noqa: E501

        :param tick_label_rotation_angle: The tick_label_rotation_angle of this Axis.  # noqa: E501
        :type: float
        """
        self._tick_label_rotation_angle = tick_label_rotation_angle

    @property
    def fill_format(self):
        """Gets the fill_format of this Axis.  # noqa: E501

        Get or sets the fill format.  # noqa: E501

        :return: The fill_format of this Axis.  # noqa: E501
        :rtype: FillFormat
        """
        return self._fill_format

    @fill_format.setter
    def fill_format(self, fill_format):
        """Sets the fill_format of this Axis.

        Get or sets the fill format.  # noqa: E501

        :param fill_format: The fill_format of this Axis.  # noqa: E501
        :type: FillFormat
        """
        self._fill_format = fill_format

    @property
    def effect_format(self):
        """Gets the effect_format of this Axis.  # noqa: E501

        Get or sets the effect format.  # noqa: E501

        :return: The effect_format of this Axis.  # noqa: E501
        :rtype: EffectFormat
        """
        return self._effect_format

    @effect_format.setter
    def effect_format(self, effect_format):
        """Sets the effect_format of this Axis.

        Get or sets the effect format.  # noqa: E501

        :param effect_format: The effect_format of this Axis.  # noqa: E501
        :type: EffectFormat
        """
        self._effect_format = effect_format

    @property
    def line_format(self):
        """Gets the line_format of this Axis.  # noqa: E501

        Get or sets the line format.  # noqa: E501

        :return: The line_format of this Axis.  # noqa: E501
        :rtype: LineFormat
        """
        return self._line_format

    @line_format.setter
    def line_format(self, line_format):
        """Sets the line_format of this Axis.

        Get or sets the line format.  # noqa: E501

        :param line_format: The line_format of this Axis.  # noqa: E501
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
        if not isinstance(other, Axis):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
