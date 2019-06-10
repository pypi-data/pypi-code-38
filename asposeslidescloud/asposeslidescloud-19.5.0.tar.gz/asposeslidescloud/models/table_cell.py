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


class TableCell(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'text': 'str',
        'row_span': 'int',
        'col_span': 'int',
        'margin_top': 'float',
        'margin_right': 'float',
        'margin_left': 'float',
        'margin_bottom': 'float',
        'text_anchor_type': 'str',
        'text_vertical_type': 'str',
        'fill_format': 'FillFormat',
        'border_top': 'LineFormat',
        'border_right': 'LineFormat',
        'border_left': 'LineFormat',
        'border_bottom': 'LineFormat',
        'border_diagonal_up': 'LineFormat',
        'border_diagonal_down': 'LineFormat'
    }

    attribute_map = {
        'text': 'Text',
        'row_span': 'RowSpan',
        'col_span': 'ColSpan',
        'margin_top': 'MarginTop',
        'margin_right': 'MarginRight',
        'margin_left': 'MarginLeft',
        'margin_bottom': 'MarginBottom',
        'text_anchor_type': 'TextAnchorType',
        'text_vertical_type': 'TextVerticalType',
        'fill_format': 'FillFormat',
        'border_top': 'BorderTop',
        'border_right': 'BorderRight',
        'border_left': 'BorderLeft',
        'border_bottom': 'BorderBottom',
        'border_diagonal_up': 'BorderDiagonalUp',
        'border_diagonal_down': 'BorderDiagonalDown'
    }

    def __init__(self, text=None, row_span=None, col_span=None, margin_top=None, margin_right=None, margin_left=None, margin_bottom=None, text_anchor_type=None, text_vertical_type=None, fill_format=None, border_top=None, border_right=None, border_left=None, border_bottom=None, border_diagonal_up=None, border_diagonal_down=None):  # noqa: E501
        """TableCell - a model defined in Swagger"""  # noqa: E501

        self._text = None
        self._row_span = None
        self._col_span = None
        self._margin_top = None
        self._margin_right = None
        self._margin_left = None
        self._margin_bottom = None
        self._text_anchor_type = None
        self._text_vertical_type = None
        self._fill_format = None
        self._border_top = None
        self._border_right = None
        self._border_left = None
        self._border_bottom = None
        self._border_diagonal_up = None
        self._border_diagonal_down = None

        if text is not None:
            self.text = text
        self.row_span = row_span
        self.col_span = col_span
        self.margin_top = margin_top
        self.margin_right = margin_right
        self.margin_left = margin_left
        self.margin_bottom = margin_bottom
        self.text_anchor_type = text_anchor_type
        self.text_vertical_type = text_vertical_type
        if fill_format is not None:
            self.fill_format = fill_format
        if border_top is not None:
            self.border_top = border_top
        if border_right is not None:
            self.border_right = border_right
        if border_left is not None:
            self.border_left = border_left
        if border_bottom is not None:
            self.border_bottom = border_bottom
        if border_diagonal_up is not None:
            self.border_diagonal_up = border_diagonal_up
        if border_diagonal_down is not None:
            self.border_diagonal_down = border_diagonal_down

    @property
    def text(self):
        """Gets the text of this TableCell.  # noqa: E501

        Cell text.  # noqa: E501

        :return: The text of this TableCell.  # noqa: E501
        :rtype: str
        """
        return self._text

    @text.setter
    def text(self, text):
        """Sets the text of this TableCell.

        Cell text.  # noqa: E501

        :param text: The text of this TableCell.  # noqa: E501
        :type: str
        """
        self._text = text

    @property
    def row_span(self):
        """Gets the row_span of this TableCell.  # noqa: E501

        The number of rows spanned by a merged cell.  # noqa: E501

        :return: The row_span of this TableCell.  # noqa: E501
        :rtype: int
        """
        return self._row_span

    @row_span.setter
    def row_span(self, row_span):
        """Sets the row_span of this TableCell.

        The number of rows spanned by a merged cell.  # noqa: E501

        :param row_span: The row_span of this TableCell.  # noqa: E501
        :type: int
        """
        self._row_span = row_span

    @property
    def col_span(self):
        """Gets the col_span of this TableCell.  # noqa: E501

        The number of columns spanned by a merged cell.  # noqa: E501

        :return: The col_span of this TableCell.  # noqa: E501
        :rtype: int
        """
        return self._col_span

    @col_span.setter
    def col_span(self, col_span):
        """Sets the col_span of this TableCell.

        The number of columns spanned by a merged cell.  # noqa: E501

        :param col_span: The col_span of this TableCell.  # noqa: E501
        :type: int
        """
        self._col_span = col_span

    @property
    def margin_top(self):
        """Gets the margin_top of this TableCell.  # noqa: E501

        The top margin of the cell.  # noqa: E501

        :return: The margin_top of this TableCell.  # noqa: E501
        :rtype: float
        """
        return self._margin_top

    @margin_top.setter
    def margin_top(self, margin_top):
        """Sets the margin_top of this TableCell.

        The top margin of the cell.  # noqa: E501

        :param margin_top: The margin_top of this TableCell.  # noqa: E501
        :type: float
        """
        self._margin_top = margin_top

    @property
    def margin_right(self):
        """Gets the margin_right of this TableCell.  # noqa: E501

        The right margin of the cell.  # noqa: E501

        :return: The margin_right of this TableCell.  # noqa: E501
        :rtype: float
        """
        return self._margin_right

    @margin_right.setter
    def margin_right(self, margin_right):
        """Sets the margin_right of this TableCell.

        The right margin of the cell.  # noqa: E501

        :param margin_right: The margin_right of this TableCell.  # noqa: E501
        :type: float
        """
        self._margin_right = margin_right

    @property
    def margin_left(self):
        """Gets the margin_left of this TableCell.  # noqa: E501

        The left margin of the cell.  # noqa: E501

        :return: The margin_left of this TableCell.  # noqa: E501
        :rtype: float
        """
        return self._margin_left

    @margin_left.setter
    def margin_left(self, margin_left):
        """Sets the margin_left of this TableCell.

        The left margin of the cell.  # noqa: E501

        :param margin_left: The margin_left of this TableCell.  # noqa: E501
        :type: float
        """
        self._margin_left = margin_left

    @property
    def margin_bottom(self):
        """Gets the margin_bottom of this TableCell.  # noqa: E501

        The bottom margin of the cell.  # noqa: E501

        :return: The margin_bottom of this TableCell.  # noqa: E501
        :rtype: float
        """
        return self._margin_bottom

    @margin_bottom.setter
    def margin_bottom(self, margin_bottom):
        """Sets the margin_bottom of this TableCell.

        The bottom margin of the cell.  # noqa: E501

        :param margin_bottom: The margin_bottom of this TableCell.  # noqa: E501
        :type: float
        """
        self._margin_bottom = margin_bottom

    @property
    def text_anchor_type(self):
        """Gets the text_anchor_type of this TableCell.  # noqa: E501

        Text anchor type.  # noqa: E501

        :return: The text_anchor_type of this TableCell.  # noqa: E501
        :rtype: str
        """
        return self._text_anchor_type

    @text_anchor_type.setter
    def text_anchor_type(self, text_anchor_type):
        """Sets the text_anchor_type of this TableCell.

        Text anchor type.  # noqa: E501

        :param text_anchor_type: The text_anchor_type of this TableCell.  # noqa: E501
        :type: str
        """
        if text_anchor_type is not None:
            allowed_values = ["Top", "Center", "Bottom", "Justified", "Distributed", "NotDefined"]  # noqa: E501
            if text_anchor_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `text_anchor_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(text_anchor_type, allowed_values)
                )
        self._text_anchor_type = text_anchor_type

    @property
    def text_vertical_type(self):
        """Gets the text_vertical_type of this TableCell.  # noqa: E501

        The type of vertical text.  # noqa: E501

        :return: The text_vertical_type of this TableCell.  # noqa: E501
        :rtype: str
        """
        return self._text_vertical_type

    @text_vertical_type.setter
    def text_vertical_type(self, text_vertical_type):
        """Sets the text_vertical_type of this TableCell.

        The type of vertical text.  # noqa: E501

        :param text_vertical_type: The text_vertical_type of this TableCell.  # noqa: E501
        :type: str
        """
        if text_vertical_type is not None:
            allowed_values = ["Horizontal", "Vertical", "Vertical270", "WordArtVertical", "EastAsianVertical", "MongolianVertical", "WordArtVerticalRightToLeft", "NotDefined"]  # noqa: E501
            if text_vertical_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `text_vertical_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(text_vertical_type, allowed_values)
                )
        self._text_vertical_type = text_vertical_type

    @property
    def fill_format(self):
        """Gets the fill_format of this TableCell.  # noqa: E501

        Fill properties set of the cell.  # noqa: E501

        :return: The fill_format of this TableCell.  # noqa: E501
        :rtype: FillFormat
        """
        return self._fill_format

    @fill_format.setter
    def fill_format(self, fill_format):
        """Sets the fill_format of this TableCell.

        Fill properties set of the cell.  # noqa: E501

        :param fill_format: The fill_format of this TableCell.  # noqa: E501
        :type: FillFormat
        """
        self._fill_format = fill_format

    @property
    def border_top(self):
        """Gets the border_top of this TableCell.  # noqa: E501

        Line properties set for the top border of the cell.  # noqa: E501

        :return: The border_top of this TableCell.  # noqa: E501
        :rtype: LineFormat
        """
        return self._border_top

    @border_top.setter
    def border_top(self, border_top):
        """Sets the border_top of this TableCell.

        Line properties set for the top border of the cell.  # noqa: E501

        :param border_top: The border_top of this TableCell.  # noqa: E501
        :type: LineFormat
        """
        self._border_top = border_top

    @property
    def border_right(self):
        """Gets the border_right of this TableCell.  # noqa: E501

        Line properties set for the right border of the cell.  # noqa: E501

        :return: The border_right of this TableCell.  # noqa: E501
        :rtype: LineFormat
        """
        return self._border_right

    @border_right.setter
    def border_right(self, border_right):
        """Sets the border_right of this TableCell.

        Line properties set for the right border of the cell.  # noqa: E501

        :param border_right: The border_right of this TableCell.  # noqa: E501
        :type: LineFormat
        """
        self._border_right = border_right

    @property
    def border_left(self):
        """Gets the border_left of this TableCell.  # noqa: E501

        Line properties set for the left border of the cell.  # noqa: E501

        :return: The border_left of this TableCell.  # noqa: E501
        :rtype: LineFormat
        """
        return self._border_left

    @border_left.setter
    def border_left(self, border_left):
        """Sets the border_left of this TableCell.

        Line properties set for the left border of the cell.  # noqa: E501

        :param border_left: The border_left of this TableCell.  # noqa: E501
        :type: LineFormat
        """
        self._border_left = border_left

    @property
    def border_bottom(self):
        """Gets the border_bottom of this TableCell.  # noqa: E501

        Line properties set for the bottom border of the cell.  # noqa: E501

        :return: The border_bottom of this TableCell.  # noqa: E501
        :rtype: LineFormat
        """
        return self._border_bottom

    @border_bottom.setter
    def border_bottom(self, border_bottom):
        """Sets the border_bottom of this TableCell.

        Line properties set for the bottom border of the cell.  # noqa: E501

        :param border_bottom: The border_bottom of this TableCell.  # noqa: E501
        :type: LineFormat
        """
        self._border_bottom = border_bottom

    @property
    def border_diagonal_up(self):
        """Gets the border_diagonal_up of this TableCell.  # noqa: E501

        Line properties set for the diagonal up border of the cell.  # noqa: E501

        :return: The border_diagonal_up of this TableCell.  # noqa: E501
        :rtype: LineFormat
        """
        return self._border_diagonal_up

    @border_diagonal_up.setter
    def border_diagonal_up(self, border_diagonal_up):
        """Sets the border_diagonal_up of this TableCell.

        Line properties set for the diagonal up border of the cell.  # noqa: E501

        :param border_diagonal_up: The border_diagonal_up of this TableCell.  # noqa: E501
        :type: LineFormat
        """
        self._border_diagonal_up = border_diagonal_up

    @property
    def border_diagonal_down(self):
        """Gets the border_diagonal_down of this TableCell.  # noqa: E501

        Line properties set for the diagonal down border of the cell.  # noqa: E501

        :return: The border_diagonal_down of this TableCell.  # noqa: E501
        :rtype: LineFormat
        """
        return self._border_diagonal_down

    @border_diagonal_down.setter
    def border_diagonal_down(self, border_diagonal_down):
        """Sets the border_diagonal_down of this TableCell.

        Line properties set for the diagonal down border of the cell.  # noqa: E501

        :param border_diagonal_down: The border_diagonal_down of this TableCell.  # noqa: E501
        :type: LineFormat
        """
        self._border_diagonal_down = border_diagonal_down

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
        if not isinstance(other, TableCell):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
