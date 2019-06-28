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

from asposeslidescloud.models.resource_base import ResourceBase

class Paragraph(ResourceBase):


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
        'margin_left': 'float',
        'margin_right': 'float',
        'space_before': 'float',
        'space_after': 'float',
        'space_within': 'float',
        'indent': 'float',
        'alignment': 'str',
        'font_alignment': 'str',
        'default_tab_size': 'float',
        'depth': 'int',
        'bullet_char': 'str',
        'bullet_height': 'float',
        'bullet_type': 'str',
        'numbered_bullet_start_with': 'int',
        'numbered_bullet_style': 'str',
        'hanging_punctuation': 'str',
        'east_asian_line_break': 'str',
        'latin_line_break': 'str',
        'right_to_left': 'str',
        'portion_list': 'list[ResourceUriElement]'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'margin_left': 'MarginLeft',
        'margin_right': 'MarginRight',
        'space_before': 'SpaceBefore',
        'space_after': 'SpaceAfter',
        'space_within': 'SpaceWithin',
        'indent': 'Indent',
        'alignment': 'Alignment',
        'font_alignment': 'FontAlignment',
        'default_tab_size': 'DefaultTabSize',
        'depth': 'Depth',
        'bullet_char': 'BulletChar',
        'bullet_height': 'BulletHeight',
        'bullet_type': 'BulletType',
        'numbered_bullet_start_with': 'NumberedBulletStartWith',
        'numbered_bullet_style': 'NumberedBulletStyle',
        'hanging_punctuation': 'HangingPunctuation',
        'east_asian_line_break': 'EastAsianLineBreak',
        'latin_line_break': 'LatinLineBreak',
        'right_to_left': 'RightToLeft',
        'portion_list': 'PortionList'
    }

    def __init__(self, self_uri=None, alternate_links=None, margin_left=None, margin_right=None, space_before=None, space_after=None, space_within=None, indent=None, alignment=None, font_alignment=None, default_tab_size=None, depth=None, bullet_char=None, bullet_height=None, bullet_type=None, numbered_bullet_start_with=None, numbered_bullet_style=None, hanging_punctuation=None, east_asian_line_break=None, latin_line_break=None, right_to_left=None, portion_list=None):  # noqa: E501
        """Paragraph - a model defined in Swagger"""  # noqa: E501
        super(Paragraph, self).__init__(self_uri, alternate_links)

        self._margin_left = None
        self._margin_right = None
        self._space_before = None
        self._space_after = None
        self._space_within = None
        self._indent = None
        self._alignment = None
        self._font_alignment = None
        self._default_tab_size = None
        self._depth = None
        self._bullet_char = None
        self._bullet_height = None
        self._bullet_type = None
        self._numbered_bullet_start_with = None
        self._numbered_bullet_style = None
        self._hanging_punctuation = None
        self._east_asian_line_break = None
        self._latin_line_break = None
        self._right_to_left = None
        self._portion_list = None

        if margin_left is not None:
            self.margin_left = margin_left
        if margin_right is not None:
            self.margin_right = margin_right
        if space_before is not None:
            self.space_before = space_before
        if space_after is not None:
            self.space_after = space_after
        if space_within is not None:
            self.space_within = space_within
        if indent is not None:
            self.indent = indent
        if alignment is not None:
            self.alignment = alignment
        if font_alignment is not None:
            self.font_alignment = font_alignment
        if default_tab_size is not None:
            self.default_tab_size = default_tab_size
        if depth is not None:
            self.depth = depth
        if bullet_char is not None:
            self.bullet_char = bullet_char
        if bullet_height is not None:
            self.bullet_height = bullet_height
        if bullet_type is not None:
            self.bullet_type = bullet_type
        if numbered_bullet_start_with is not None:
            self.numbered_bullet_start_with = numbered_bullet_start_with
        if numbered_bullet_style is not None:
            self.numbered_bullet_style = numbered_bullet_style
        if hanging_punctuation is not None:
            self.hanging_punctuation = hanging_punctuation
        if east_asian_line_break is not None:
            self.east_asian_line_break = east_asian_line_break
        if latin_line_break is not None:
            self.latin_line_break = latin_line_break
        if right_to_left is not None:
            self.right_to_left = right_to_left
        if portion_list is not None:
            self.portion_list = portion_list

    @property
    def margin_left(self):
        """Gets the margin_left of this Paragraph.  # noqa: E501


        :return: The margin_left of this Paragraph.  # noqa: E501
        :rtype: float
        """
        return self._margin_left

    @margin_left.setter
    def margin_left(self, margin_left):
        """Sets the margin_left of this Paragraph.


        :param margin_left: The margin_left of this Paragraph.  # noqa: E501
        :type: float
        """
        self._margin_left = margin_left

    @property
    def margin_right(self):
        """Gets the margin_right of this Paragraph.  # noqa: E501


        :return: The margin_right of this Paragraph.  # noqa: E501
        :rtype: float
        """
        return self._margin_right

    @margin_right.setter
    def margin_right(self, margin_right):
        """Sets the margin_right of this Paragraph.


        :param margin_right: The margin_right of this Paragraph.  # noqa: E501
        :type: float
        """
        self._margin_right = margin_right

    @property
    def space_before(self):
        """Gets the space_before of this Paragraph.  # noqa: E501


        :return: The space_before of this Paragraph.  # noqa: E501
        :rtype: float
        """
        return self._space_before

    @space_before.setter
    def space_before(self, space_before):
        """Sets the space_before of this Paragraph.


        :param space_before: The space_before of this Paragraph.  # noqa: E501
        :type: float
        """
        self._space_before = space_before

    @property
    def space_after(self):
        """Gets the space_after of this Paragraph.  # noqa: E501


        :return: The space_after of this Paragraph.  # noqa: E501
        :rtype: float
        """
        return self._space_after

    @space_after.setter
    def space_after(self, space_after):
        """Sets the space_after of this Paragraph.


        :param space_after: The space_after of this Paragraph.  # noqa: E501
        :type: float
        """
        self._space_after = space_after

    @property
    def space_within(self):
        """Gets the space_within of this Paragraph.  # noqa: E501


        :return: The space_within of this Paragraph.  # noqa: E501
        :rtype: float
        """
        return self._space_within

    @space_within.setter
    def space_within(self, space_within):
        """Sets the space_within of this Paragraph.


        :param space_within: The space_within of this Paragraph.  # noqa: E501
        :type: float
        """
        self._space_within = space_within

    @property
    def indent(self):
        """Gets the indent of this Paragraph.  # noqa: E501


        :return: The indent of this Paragraph.  # noqa: E501
        :rtype: float
        """
        return self._indent

    @indent.setter
    def indent(self, indent):
        """Sets the indent of this Paragraph.


        :param indent: The indent of this Paragraph.  # noqa: E501
        :type: float
        """
        self._indent = indent

    @property
    def alignment(self):
        """Gets the alignment of this Paragraph.  # noqa: E501


        :return: The alignment of this Paragraph.  # noqa: E501
        :rtype: str
        """
        return self._alignment

    @alignment.setter
    def alignment(self, alignment):
        """Sets the alignment of this Paragraph.


        :param alignment: The alignment of this Paragraph.  # noqa: E501
        :type: str
        """
        if alignment is not None:
            allowed_values = ["Left", "Center", "Right", "Justify", "JustifyLow", "Distributed", "NotDefined"]  # noqa: E501
            if alignment not in allowed_values:
                raise ValueError(
                    "Invalid value for `alignment` ({0}), must be one of {1}"  # noqa: E501
                    .format(alignment, allowed_values)
                )
        self._alignment = alignment

    @property
    def font_alignment(self):
        """Gets the font_alignment of this Paragraph.  # noqa: E501


        :return: The font_alignment of this Paragraph.  # noqa: E501
        :rtype: str
        """
        return self._font_alignment

    @font_alignment.setter
    def font_alignment(self, font_alignment):
        """Sets the font_alignment of this Paragraph.


        :param font_alignment: The font_alignment of this Paragraph.  # noqa: E501
        :type: str
        """
        if font_alignment is not None:
            allowed_values = ["Automatic", "Top", "Center", "Bottom", "Baseline", "Default"]  # noqa: E501
            if font_alignment not in allowed_values:
                raise ValueError(
                    "Invalid value for `font_alignment` ({0}), must be one of {1}"  # noqa: E501
                    .format(font_alignment, allowed_values)
                )
        self._font_alignment = font_alignment

    @property
    def default_tab_size(self):
        """Gets the default_tab_size of this Paragraph.  # noqa: E501


        :return: The default_tab_size of this Paragraph.  # noqa: E501
        :rtype: float
        """
        return self._default_tab_size

    @default_tab_size.setter
    def default_tab_size(self, default_tab_size):
        """Sets the default_tab_size of this Paragraph.


        :param default_tab_size: The default_tab_size of this Paragraph.  # noqa: E501
        :type: float
        """
        self._default_tab_size = default_tab_size

    @property
    def depth(self):
        """Gets the depth of this Paragraph.  # noqa: E501


        :return: The depth of this Paragraph.  # noqa: E501
        :rtype: int
        """
        return self._depth

    @depth.setter
    def depth(self, depth):
        """Sets the depth of this Paragraph.


        :param depth: The depth of this Paragraph.  # noqa: E501
        :type: int
        """
        self._depth = depth

    @property
    def bullet_char(self):
        """Gets the bullet_char of this Paragraph.  # noqa: E501


        :return: The bullet_char of this Paragraph.  # noqa: E501
        :rtype: str
        """
        return self._bullet_char

    @bullet_char.setter
    def bullet_char(self, bullet_char):
        """Sets the bullet_char of this Paragraph.


        :param bullet_char: The bullet_char of this Paragraph.  # noqa: E501
        :type: str
        """
        self._bullet_char = bullet_char

    @property
    def bullet_height(self):
        """Gets the bullet_height of this Paragraph.  # noqa: E501


        :return: The bullet_height of this Paragraph.  # noqa: E501
        :rtype: float
        """
        return self._bullet_height

    @bullet_height.setter
    def bullet_height(self, bullet_height):
        """Sets the bullet_height of this Paragraph.


        :param bullet_height: The bullet_height of this Paragraph.  # noqa: E501
        :type: float
        """
        self._bullet_height = bullet_height

    @property
    def bullet_type(self):
        """Gets the bullet_type of this Paragraph.  # noqa: E501


        :return: The bullet_type of this Paragraph.  # noqa: E501
        :rtype: str
        """
        return self._bullet_type

    @bullet_type.setter
    def bullet_type(self, bullet_type):
        """Sets the bullet_type of this Paragraph.


        :param bullet_type: The bullet_type of this Paragraph.  # noqa: E501
        :type: str
        """
        if bullet_type is not None:
            allowed_values = ["None", "Symbol", "Numbered", "Picture", "NotDefined"]  # noqa: E501
            if bullet_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `bullet_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(bullet_type, allowed_values)
                )
        self._bullet_type = bullet_type

    @property
    def numbered_bullet_start_with(self):
        """Gets the numbered_bullet_start_with of this Paragraph.  # noqa: E501


        :return: The numbered_bullet_start_with of this Paragraph.  # noqa: E501
        :rtype: int
        """
        return self._numbered_bullet_start_with

    @numbered_bullet_start_with.setter
    def numbered_bullet_start_with(self, numbered_bullet_start_with):
        """Sets the numbered_bullet_start_with of this Paragraph.


        :param numbered_bullet_start_with: The numbered_bullet_start_with of this Paragraph.  # noqa: E501
        :type: int
        """
        self._numbered_bullet_start_with = numbered_bullet_start_with

    @property
    def numbered_bullet_style(self):
        """Gets the numbered_bullet_style of this Paragraph.  # noqa: E501


        :return: The numbered_bullet_style of this Paragraph.  # noqa: E501
        :rtype: str
        """
        return self._numbered_bullet_style

    @numbered_bullet_style.setter
    def numbered_bullet_style(self, numbered_bullet_style):
        """Sets the numbered_bullet_style of this Paragraph.


        :param numbered_bullet_style: The numbered_bullet_style of this Paragraph.  # noqa: E501
        :type: str
        """
        if numbered_bullet_style is not None:
            allowed_values = ["BulletAlphaLCPeriod", "BulletAlphaUCPeriod", "BulletArabicParenRight", "BulletArabicPeriod", "BulletRomanLCParenBoth", "BulletRomanLCParenRight", "BulletRomanLCPeriod", "BulletRomanUCPeriod", "BulletAlphaLCParenBoth", "BulletAlphaLCParenRight", "BulletAlphaUCParenBoth", "BulletAlphaUCParenRight", "BulletArabicParenBoth", "BulletArabicPlain", "BulletRomanUCParenBoth", "BulletRomanUCParenRight", "BulletSimpChinPlain", "BulletSimpChinPeriod", "BulletCircleNumDBPlain", "BulletCircleNumWDWhitePlain", "BulletCircleNumWDBlackPlain", "BulletTradChinPlain", "BulletTradChinPeriod", "BulletArabicAlphaDash", "BulletArabicAbjadDash", "BulletHebrewAlphaDash", "BulletKanjiKoreanPlain", "BulletKanjiKoreanPeriod", "BulletArabicDBPlain", "BulletArabicDBPeriod", "BulletThaiAlphaPeriod", "BulletThaiAlphaParenRight", "BulletThaiAlphaParenBoth", "BulletThaiNumPeriod", "BulletThaiNumParenRight", "BulletThaiNumParenBoth", "BulletHindiAlphaPeriod", "BulletHindiNumPeriod", "BulletKanjiSimpChinDBPeriod", "BulletHindiNumParenRight", "BulletHindiAlpha1Period", "NotDefined"]  # noqa: E501
            if numbered_bullet_style not in allowed_values:
                raise ValueError(
                    "Invalid value for `numbered_bullet_style` ({0}), must be one of {1}"  # noqa: E501
                    .format(numbered_bullet_style, allowed_values)
                )
        self._numbered_bullet_style = numbered_bullet_style

    @property
    def hanging_punctuation(self):
        """Gets the hanging_punctuation of this Paragraph.  # noqa: E501


        :return: The hanging_punctuation of this Paragraph.  # noqa: E501
        :rtype: str
        """
        return self._hanging_punctuation

    @hanging_punctuation.setter
    def hanging_punctuation(self, hanging_punctuation):
        """Sets the hanging_punctuation of this Paragraph.


        :param hanging_punctuation: The hanging_punctuation of this Paragraph.  # noqa: E501
        :type: str
        """
        if hanging_punctuation is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if hanging_punctuation not in allowed_values:
                raise ValueError(
                    "Invalid value for `hanging_punctuation` ({0}), must be one of {1}"  # noqa: E501
                    .format(hanging_punctuation, allowed_values)
                )
        self._hanging_punctuation = hanging_punctuation

    @property
    def east_asian_line_break(self):
        """Gets the east_asian_line_break of this Paragraph.  # noqa: E501


        :return: The east_asian_line_break of this Paragraph.  # noqa: E501
        :rtype: str
        """
        return self._east_asian_line_break

    @east_asian_line_break.setter
    def east_asian_line_break(self, east_asian_line_break):
        """Sets the east_asian_line_break of this Paragraph.


        :param east_asian_line_break: The east_asian_line_break of this Paragraph.  # noqa: E501
        :type: str
        """
        if east_asian_line_break is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if east_asian_line_break not in allowed_values:
                raise ValueError(
                    "Invalid value for `east_asian_line_break` ({0}), must be one of {1}"  # noqa: E501
                    .format(east_asian_line_break, allowed_values)
                )
        self._east_asian_line_break = east_asian_line_break

    @property
    def latin_line_break(self):
        """Gets the latin_line_break of this Paragraph.  # noqa: E501


        :return: The latin_line_break of this Paragraph.  # noqa: E501
        :rtype: str
        """
        return self._latin_line_break

    @latin_line_break.setter
    def latin_line_break(self, latin_line_break):
        """Sets the latin_line_break of this Paragraph.


        :param latin_line_break: The latin_line_break of this Paragraph.  # noqa: E501
        :type: str
        """
        if latin_line_break is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if latin_line_break not in allowed_values:
                raise ValueError(
                    "Invalid value for `latin_line_break` ({0}), must be one of {1}"  # noqa: E501
                    .format(latin_line_break, allowed_values)
                )
        self._latin_line_break = latin_line_break

    @property
    def right_to_left(self):
        """Gets the right_to_left of this Paragraph.  # noqa: E501


        :return: The right_to_left of this Paragraph.  # noqa: E501
        :rtype: str
        """
        return self._right_to_left

    @right_to_left.setter
    def right_to_left(self, right_to_left):
        """Sets the right_to_left of this Paragraph.


        :param right_to_left: The right_to_left of this Paragraph.  # noqa: E501
        :type: str
        """
        if right_to_left is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if right_to_left not in allowed_values:
                raise ValueError(
                    "Invalid value for `right_to_left` ({0}), must be one of {1}"  # noqa: E501
                    .format(right_to_left, allowed_values)
                )
        self._right_to_left = right_to_left

    @property
    def portion_list(self):
        """Gets the portion_list of this Paragraph.  # noqa: E501


        :return: The portion_list of this Paragraph.  # noqa: E501
        :rtype: list[ResourceUriElement]
        """
        return self._portion_list

    @portion_list.setter
    def portion_list(self, portion_list):
        """Sets the portion_list of this Paragraph.


        :param portion_list: The portion_list of this Paragraph.  # noqa: E501
        :type: list[ResourceUriElement]
        """
        self._portion_list = portion_list

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
        if not isinstance(other, Paragraph):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
