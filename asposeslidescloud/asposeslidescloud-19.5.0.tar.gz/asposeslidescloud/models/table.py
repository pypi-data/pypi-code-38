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

class Table(ShapeBase):


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
        'style': 'str',
        'rows': 'list[TableRow]',
        'columns': 'list[TableColumn]',
        'first_col': 'bool',
        'first_row': 'bool',
        'horizontal_banding': 'bool',
        'last_col': 'bool',
        'last_row': 'bool',
        'right_to_left': 'bool',
        'vertical_banding': 'bool'
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
        'style': 'Style',
        'rows': 'Rows',
        'columns': 'Columns',
        'first_col': 'FirstCol',
        'first_row': 'FirstRow',
        'horizontal_banding': 'HorizontalBanding',
        'last_col': 'LastCol',
        'last_row': 'LastRow',
        'right_to_left': 'RightToLeft',
        'vertical_banding': 'VerticalBanding'
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, width=None, height=None, alternative_text=None, hidden=None, x=None, y=None, z_order_position=None, shapes=None, fill_format=None, effect_format=None, line_format=None, type='Table', shape_type='Table', style=None, rows=None, columns=None, first_col=None, first_row=None, horizontal_banding=None, last_col=None, last_row=None, right_to_left=None, vertical_banding=None):  # noqa: E501
        """Table - a model defined in Swagger"""  # noqa: E501
        super(Table, self).__init__(self_uri, alternate_links, name, width, height, alternative_text, hidden, x, y, z_order_position, shapes, fill_format, effect_format, line_format, type, shape_type)

        self._style = None
        self._rows = None
        self._columns = None
        self._first_col = None
        self._first_row = None
        self._horizontal_banding = None
        self._last_col = None
        self._last_row = None
        self._right_to_left = None
        self._vertical_banding = None

        self.style = style
        if rows is not None:
            self.rows = rows
        if columns is not None:
            self.columns = columns
        self.first_col = first_col
        self.first_row = first_row
        self.horizontal_banding = horizontal_banding
        self.last_col = last_col
        self.last_row = last_row
        self.right_to_left = right_to_left
        self.vertical_banding = vertical_banding

    @property
    def style(self):
        """Gets the style of this Table.  # noqa: E501

        Builtin table style.  # noqa: E501

        :return: The style of this Table.  # noqa: E501
        :rtype: str
        """
        return self._style

    @style.setter
    def style(self, style):
        """Sets the style of this Table.

        Builtin table style.  # noqa: E501

        :param style: The style of this Table.  # noqa: E501
        :type: str
        """
        if style is not None:
            allowed_values = ["None", "MediumStyle2Accent1", "MediumStyle2", "NoStyleNoGrid", "ThemedStyle1Accent1", "ThemedStyle1Accent2", "ThemedStyle1Accent3", "ThemedStyle1Accent4", "ThemedStyle1Accent5", "ThemedStyle1Accent6", "NoStyleTableGrid", "ThemedStyle2Accent1", "ThemedStyle2Accent2", "ThemedStyle2Accent3", "ThemedStyle2Accent4", "ThemedStyle2Accent5", "ThemedStyle2Accent6", "LightStyle1", "LightStyle1Accent1", "LightStyle1Accent2", "LightStyle1Accent3", "LightStyle1Accent4", "LightStyle2Accent5", "LightStyle1Accent6", "LightStyle2", "LightStyle2Accent1", "LightStyle2Accent2", "LightStyle2Accent3", "MediumStyle2Accent3", "MediumStyle2Accent4", "MediumStyle2Accent5", "LightStyle2Accent6", "LightStyle2Accent4", "LightStyle3", "LightStyle3Accent1", "MediumStyle2Accent2", "LightStyle3Accent2", "LightStyle3Accent3", "LightStyle3Accent4", "LightStyle3Accent5", "LightStyle3Accent6", "MediumStyle1", "MediumStyle1Accent1", "MediumStyle1Accent2", "MediumStyle1Accent3", "MediumStyle1Accent4", "MediumStyle1Accent5", "MediumStyle1Accent6", "MediumStyle2Accent6", "MediumStyle3", "MediumStyle3Accent1", "MediumStyle3Accent2", "MediumStyle3Accent3", "MediumStyle3Accent4", "MediumStyle3Accent5", "MediumStyle3Accent6", "MediumStyle4", "MediumStyle4Accent1", "MediumStyle4Accent2", "MediumStyle4Accent3", "MediumStyle4Accent4", "MediumStyle4Accent5", "MediumStyle4Accent6", "DarkStyle1", "DarkStyle1Accent1", "DarkStyle1Accent2", "DarkStyle1Accent3", "DarkStyle1Accent4", "DarkStyle1Accent5", "DarkStyle1Accent6", "DarkStyle2", "DarkStyle2Accent1Accent2", "DarkStyle2Accent3Accent4", "DarkStyle2Accent5Accent6", "LightStyle1Accent5", "Custom"]  # noqa: E501
            if style not in allowed_values:
                raise ValueError(
                    "Invalid value for `style` ({0}), must be one of {1}"  # noqa: E501
                    .format(style, allowed_values)
                )
        self._style = style

    @property
    def rows(self):
        """Gets the rows of this Table.  # noqa: E501

        Rows.  # noqa: E501

        :return: The rows of this Table.  # noqa: E501
        :rtype: list[TableRow]
        """
        return self._rows

    @rows.setter
    def rows(self, rows):
        """Sets the rows of this Table.

        Rows.  # noqa: E501

        :param rows: The rows of this Table.  # noqa: E501
        :type: list[TableRow]
        """
        self._rows = rows

    @property
    def columns(self):
        """Gets the columns of this Table.  # noqa: E501

        Columns.  # noqa: E501

        :return: The columns of this Table.  # noqa: E501
        :rtype: list[TableColumn]
        """
        return self._columns

    @columns.setter
    def columns(self, columns):
        """Sets the columns of this Table.

        Columns.  # noqa: E501

        :param columns: The columns of this Table.  # noqa: E501
        :type: list[TableColumn]
        """
        self._columns = columns

    @property
    def first_col(self):
        """Gets the first_col of this Table.  # noqa: E501

        Determines whether the first column of a table has to be drawn with a special formatting.  # noqa: E501

        :return: The first_col of this Table.  # noqa: E501
        :rtype: bool
        """
        return self._first_col

    @first_col.setter
    def first_col(self, first_col):
        """Sets the first_col of this Table.

        Determines whether the first column of a table has to be drawn with a special formatting.  # noqa: E501

        :param first_col: The first_col of this Table.  # noqa: E501
        :type: bool
        """
        self._first_col = first_col

    @property
    def first_row(self):
        """Gets the first_row of this Table.  # noqa: E501

        Determines whether the first row of a table has to be drawn with a special formatting.  # noqa: E501

        :return: The first_row of this Table.  # noqa: E501
        :rtype: bool
        """
        return self._first_row

    @first_row.setter
    def first_row(self, first_row):
        """Sets the first_row of this Table.

        Determines whether the first row of a table has to be drawn with a special formatting.  # noqa: E501

        :param first_row: The first_row of this Table.  # noqa: E501
        :type: bool
        """
        self._first_row = first_row

    @property
    def horizontal_banding(self):
        """Gets the horizontal_banding of this Table.  # noqa: E501

        Determines whether the even rows has to be drawn with a different formatting.  # noqa: E501

        :return: The horizontal_banding of this Table.  # noqa: E501
        :rtype: bool
        """
        return self._horizontal_banding

    @horizontal_banding.setter
    def horizontal_banding(self, horizontal_banding):
        """Sets the horizontal_banding of this Table.

        Determines whether the even rows has to be drawn with a different formatting.  # noqa: E501

        :param horizontal_banding: The horizontal_banding of this Table.  # noqa: E501
        :type: bool
        """
        self._horizontal_banding = horizontal_banding

    @property
    def last_col(self):
        """Gets the last_col of this Table.  # noqa: E501

        Determines whether the last column of a table has to be drawn with a special formatting.  # noqa: E501

        :return: The last_col of this Table.  # noqa: E501
        :rtype: bool
        """
        return self._last_col

    @last_col.setter
    def last_col(self, last_col):
        """Sets the last_col of this Table.

        Determines whether the last column of a table has to be drawn with a special formatting.  # noqa: E501

        :param last_col: The last_col of this Table.  # noqa: E501
        :type: bool
        """
        self._last_col = last_col

    @property
    def last_row(self):
        """Gets the last_row of this Table.  # noqa: E501

        Determines whether the last row of a table has to be drawn with a special formatting.  # noqa: E501

        :return: The last_row of this Table.  # noqa: E501
        :rtype: bool
        """
        return self._last_row

    @last_row.setter
    def last_row(self, last_row):
        """Sets the last_row of this Table.

        Determines whether the last row of a table has to be drawn with a special formatting.  # noqa: E501

        :param last_row: The last_row of this Table.  # noqa: E501
        :type: bool
        """
        self._last_row = last_row

    @property
    def right_to_left(self):
        """Gets the right_to_left of this Table.  # noqa: E501

        Determines whether the table has right to left reading order.  # noqa: E501

        :return: The right_to_left of this Table.  # noqa: E501
        :rtype: bool
        """
        return self._right_to_left

    @right_to_left.setter
    def right_to_left(self, right_to_left):
        """Sets the right_to_left of this Table.

        Determines whether the table has right to left reading order.  # noqa: E501

        :param right_to_left: The right_to_left of this Table.  # noqa: E501
        :type: bool
        """
        self._right_to_left = right_to_left

    @property
    def vertical_banding(self):
        """Gets the vertical_banding of this Table.  # noqa: E501

        Determines whether the even columns has to be drawn with a different formatting.  # noqa: E501

        :return: The vertical_banding of this Table.  # noqa: E501
        :rtype: bool
        """
        return self._vertical_banding

    @vertical_banding.setter
    def vertical_banding(self, vertical_banding):
        """Sets the vertical_banding of this Table.

        Determines whether the even columns has to be drawn with a different formatting.  # noqa: E501

        :param vertical_banding: The vertical_banding of this Table.  # noqa: E501
        :type: bool
        """
        self._vertical_banding = vertical_banding

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
        if not isinstance(other, Table):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
