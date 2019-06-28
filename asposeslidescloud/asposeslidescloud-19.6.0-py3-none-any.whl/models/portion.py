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

class Portion(ResourceBase):


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
        'text': 'str',
        'font_bold': 'str',
        'font_italic': 'str',
        'font_underline': 'str',
        'strikethrough_type': 'str',
        'text_cap_type': 'str',
        'escapement': 'float',
        'spacing': 'float',
        'font_color': 'str',
        'highlight_color': 'str',
        'font_height': 'float',
        'normalise_height': 'str',
        'proof_disabled': 'str',
        'smart_tag_clean': 'bool',
        'kerning_minimal_size': 'float',
        'kumimoji': 'str',
        'language_id': 'str',
        'alternative_language_id': 'str',
        'is_hard_underline_fill': 'str',
        'is_hard_underline_line': 'str',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'underline_fill_format': 'FillFormat',
        'underline_line_format': 'LineFormat'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'text': 'Text',
        'font_bold': 'FontBold',
        'font_italic': 'FontItalic',
        'font_underline': 'FontUnderline',
        'strikethrough_type': 'StrikethroughType',
        'text_cap_type': 'TextCapType',
        'escapement': 'Escapement',
        'spacing': 'Spacing',
        'font_color': 'FontColor',
        'highlight_color': 'HighlightColor',
        'font_height': 'FontHeight',
        'normalise_height': 'NormaliseHeight',
        'proof_disabled': 'ProofDisabled',
        'smart_tag_clean': 'SmartTagClean',
        'kerning_minimal_size': 'KerningMinimalSize',
        'kumimoji': 'Kumimoji',
        'language_id': 'LanguageId',
        'alternative_language_id': 'AlternativeLanguageId',
        'is_hard_underline_fill': 'IsHardUnderlineFill',
        'is_hard_underline_line': 'IsHardUnderlineLine',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'underline_fill_format': 'UnderlineFillFormat',
        'underline_line_format': 'UnderlineLineFormat'
    }

    def __init__(self, self_uri=None, alternate_links=None, text=None, font_bold=None, font_italic=None, font_underline=None, strikethrough_type=None, text_cap_type=None, escapement=None, spacing=None, font_color=None, highlight_color=None, font_height=None, normalise_height=None, proof_disabled=None, smart_tag_clean=None, kerning_minimal_size=None, kumimoji=None, language_id=None, alternative_language_id=None, is_hard_underline_fill=None, is_hard_underline_line=None, fill_format=None, effect_format=None, line_format=None, underline_fill_format=None, underline_line_format=None):  # noqa: E501
        """Portion - a model defined in Swagger"""  # noqa: E501
        super(Portion, self).__init__(self_uri, alternate_links)

        self._text = None
        self._font_bold = None
        self._font_italic = None
        self._font_underline = None
        self._strikethrough_type = None
        self._text_cap_type = None
        self._escapement = None
        self._spacing = None
        self._font_color = None
        self._highlight_color = None
        self._font_height = None
        self._normalise_height = None
        self._proof_disabled = None
        self._smart_tag_clean = None
        self._kerning_minimal_size = None
        self._kumimoji = None
        self._language_id = None
        self._alternative_language_id = None
        self._is_hard_underline_fill = None
        self._is_hard_underline_line = None
        self._fill_format = None
        self._effect_format = None
        self._line_format = None
        self._underline_fill_format = None
        self._underline_line_format = None

        if text is not None:
            self.text = text
        if font_bold is not None:
            self.font_bold = font_bold
        if font_italic is not None:
            self.font_italic = font_italic
        if font_underline is not None:
            self.font_underline = font_underline
        if strikethrough_type is not None:
            self.strikethrough_type = strikethrough_type
        if text_cap_type is not None:
            self.text_cap_type = text_cap_type
        if escapement is not None:
            self.escapement = escapement
        if spacing is not None:
            self.spacing = spacing
        if font_color is not None:
            self.font_color = font_color
        if highlight_color is not None:
            self.highlight_color = highlight_color
        if font_height is not None:
            self.font_height = font_height
        if normalise_height is not None:
            self.normalise_height = normalise_height
        if proof_disabled is not None:
            self.proof_disabled = proof_disabled
        if smart_tag_clean is not None:
            self.smart_tag_clean = smart_tag_clean
        if kerning_minimal_size is not None:
            self.kerning_minimal_size = kerning_minimal_size
        if kumimoji is not None:
            self.kumimoji = kumimoji
        if language_id is not None:
            self.language_id = language_id
        if alternative_language_id is not None:
            self.alternative_language_id = alternative_language_id
        if is_hard_underline_fill is not None:
            self.is_hard_underline_fill = is_hard_underline_fill
        if is_hard_underline_line is not None:
            self.is_hard_underline_line = is_hard_underline_line
        if fill_format is not None:
            self.fill_format = fill_format
        if effect_format is not None:
            self.effect_format = effect_format
        if line_format is not None:
            self.line_format = line_format
        if underline_fill_format is not None:
            self.underline_fill_format = underline_fill_format
        if underline_line_format is not None:
            self.underline_line_format = underline_line_format

    @property
    def text(self):
        """Gets the text of this Portion.  # noqa: E501


        :return: The text of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._text

    @text.setter
    def text(self, text):
        """Sets the text of this Portion.


        :param text: The text of this Portion.  # noqa: E501
        :type: str
        """
        self._text = text

    @property
    def font_bold(self):
        """Gets the font_bold of this Portion.  # noqa: E501


        :return: The font_bold of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._font_bold

    @font_bold.setter
    def font_bold(self, font_bold):
        """Sets the font_bold of this Portion.


        :param font_bold: The font_bold of this Portion.  # noqa: E501
        :type: str
        """
        if font_bold is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if font_bold not in allowed_values:
                raise ValueError(
                    "Invalid value for `font_bold` ({0}), must be one of {1}"  # noqa: E501
                    .format(font_bold, allowed_values)
                )
        self._font_bold = font_bold

    @property
    def font_italic(self):
        """Gets the font_italic of this Portion.  # noqa: E501


        :return: The font_italic of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._font_italic

    @font_italic.setter
    def font_italic(self, font_italic):
        """Sets the font_italic of this Portion.


        :param font_italic: The font_italic of this Portion.  # noqa: E501
        :type: str
        """
        if font_italic is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if font_italic not in allowed_values:
                raise ValueError(
                    "Invalid value for `font_italic` ({0}), must be one of {1}"  # noqa: E501
                    .format(font_italic, allowed_values)
                )
        self._font_italic = font_italic

    @property
    def font_underline(self):
        """Gets the font_underline of this Portion.  # noqa: E501


        :return: The font_underline of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._font_underline

    @font_underline.setter
    def font_underline(self, font_underline):
        """Sets the font_underline of this Portion.


        :param font_underline: The font_underline of this Portion.  # noqa: E501
        :type: str
        """
        if font_underline is not None:
            allowed_values = ["None", "Words", "Single", "Double", "Heavy", "Dotted", "HeavyDotted", "Dashed", "HeavyDashed", "LongDashed", "HeavyLongDashed", "DotDash", "HeavyDotDash", "DotDotDash", "HeavyDotDotDash", "Wavy", "HeavyWavy", "DoubleWavy", "NotDefined"]  # noqa: E501
            if font_underline not in allowed_values:
                raise ValueError(
                    "Invalid value for `font_underline` ({0}), must be one of {1}"  # noqa: E501
                    .format(font_underline, allowed_values)
                )
        self._font_underline = font_underline

    @property
    def strikethrough_type(self):
        """Gets the strikethrough_type of this Portion.  # noqa: E501


        :return: The strikethrough_type of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._strikethrough_type

    @strikethrough_type.setter
    def strikethrough_type(self, strikethrough_type):
        """Sets the strikethrough_type of this Portion.


        :param strikethrough_type: The strikethrough_type of this Portion.  # noqa: E501
        :type: str
        """
        if strikethrough_type is not None:
            allowed_values = ["None", "Single", "Double", "NotDefined"]  # noqa: E501
            if strikethrough_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `strikethrough_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(strikethrough_type, allowed_values)
                )
        self._strikethrough_type = strikethrough_type

    @property
    def text_cap_type(self):
        """Gets the text_cap_type of this Portion.  # noqa: E501


        :return: The text_cap_type of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._text_cap_type

    @text_cap_type.setter
    def text_cap_type(self, text_cap_type):
        """Sets the text_cap_type of this Portion.


        :param text_cap_type: The text_cap_type of this Portion.  # noqa: E501
        :type: str
        """
        if text_cap_type is not None:
            allowed_values = ["None", "Small", "All", "NotDefined"]  # noqa: E501
            if text_cap_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `text_cap_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(text_cap_type, allowed_values)
                )
        self._text_cap_type = text_cap_type

    @property
    def escapement(self):
        """Gets the escapement of this Portion.  # noqa: E501


        :return: The escapement of this Portion.  # noqa: E501
        :rtype: float
        """
        return self._escapement

    @escapement.setter
    def escapement(self, escapement):
        """Sets the escapement of this Portion.


        :param escapement: The escapement of this Portion.  # noqa: E501
        :type: float
        """
        self._escapement = escapement

    @property
    def spacing(self):
        """Gets the spacing of this Portion.  # noqa: E501


        :return: The spacing of this Portion.  # noqa: E501
        :rtype: float
        """
        return self._spacing

    @spacing.setter
    def spacing(self, spacing):
        """Sets the spacing of this Portion.


        :param spacing: The spacing of this Portion.  # noqa: E501
        :type: float
        """
        self._spacing = spacing

    @property
    def font_color(self):
        """Gets the font_color of this Portion.  # noqa: E501


        :return: The font_color of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._font_color

    @font_color.setter
    def font_color(self, font_color):
        """Sets the font_color of this Portion.


        :param font_color: The font_color of this Portion.  # noqa: E501
        :type: str
        """
        self._font_color = font_color

    @property
    def highlight_color(self):
        """Gets the highlight_color of this Portion.  # noqa: E501


        :return: The highlight_color of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._highlight_color

    @highlight_color.setter
    def highlight_color(self, highlight_color):
        """Sets the highlight_color of this Portion.


        :param highlight_color: The highlight_color of this Portion.  # noqa: E501
        :type: str
        """
        self._highlight_color = highlight_color

    @property
    def font_height(self):
        """Gets the font_height of this Portion.  # noqa: E501


        :return: The font_height of this Portion.  # noqa: E501
        :rtype: float
        """
        return self._font_height

    @font_height.setter
    def font_height(self, font_height):
        """Sets the font_height of this Portion.


        :param font_height: The font_height of this Portion.  # noqa: E501
        :type: float
        """
        self._font_height = font_height

    @property
    def normalise_height(self):
        """Gets the normalise_height of this Portion.  # noqa: E501


        :return: The normalise_height of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._normalise_height

    @normalise_height.setter
    def normalise_height(self, normalise_height):
        """Sets the normalise_height of this Portion.


        :param normalise_height: The normalise_height of this Portion.  # noqa: E501
        :type: str
        """
        if normalise_height is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if normalise_height not in allowed_values:
                raise ValueError(
                    "Invalid value for `normalise_height` ({0}), must be one of {1}"  # noqa: E501
                    .format(normalise_height, allowed_values)
                )
        self._normalise_height = normalise_height

    @property
    def proof_disabled(self):
        """Gets the proof_disabled of this Portion.  # noqa: E501


        :return: The proof_disabled of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._proof_disabled

    @proof_disabled.setter
    def proof_disabled(self, proof_disabled):
        """Sets the proof_disabled of this Portion.


        :param proof_disabled: The proof_disabled of this Portion.  # noqa: E501
        :type: str
        """
        if proof_disabled is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if proof_disabled not in allowed_values:
                raise ValueError(
                    "Invalid value for `proof_disabled` ({0}), must be one of {1}"  # noqa: E501
                    .format(proof_disabled, allowed_values)
                )
        self._proof_disabled = proof_disabled

    @property
    def smart_tag_clean(self):
        """Gets the smart_tag_clean of this Portion.  # noqa: E501


        :return: The smart_tag_clean of this Portion.  # noqa: E501
        :rtype: bool
        """
        return self._smart_tag_clean

    @smart_tag_clean.setter
    def smart_tag_clean(self, smart_tag_clean):
        """Sets the smart_tag_clean of this Portion.


        :param smart_tag_clean: The smart_tag_clean of this Portion.  # noqa: E501
        :type: bool
        """
        self._smart_tag_clean = smart_tag_clean

    @property
    def kerning_minimal_size(self):
        """Gets the kerning_minimal_size of this Portion.  # noqa: E501


        :return: The kerning_minimal_size of this Portion.  # noqa: E501
        :rtype: float
        """
        return self._kerning_minimal_size

    @kerning_minimal_size.setter
    def kerning_minimal_size(self, kerning_minimal_size):
        """Sets the kerning_minimal_size of this Portion.


        :param kerning_minimal_size: The kerning_minimal_size of this Portion.  # noqa: E501
        :type: float
        """
        self._kerning_minimal_size = kerning_minimal_size

    @property
    def kumimoji(self):
        """Gets the kumimoji of this Portion.  # noqa: E501


        :return: The kumimoji of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._kumimoji

    @kumimoji.setter
    def kumimoji(self, kumimoji):
        """Sets the kumimoji of this Portion.


        :param kumimoji: The kumimoji of this Portion.  # noqa: E501
        :type: str
        """
        if kumimoji is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if kumimoji not in allowed_values:
                raise ValueError(
                    "Invalid value for `kumimoji` ({0}), must be one of {1}"  # noqa: E501
                    .format(kumimoji, allowed_values)
                )
        self._kumimoji = kumimoji

    @property
    def language_id(self):
        """Gets the language_id of this Portion.  # noqa: E501


        :return: The language_id of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._language_id

    @language_id.setter
    def language_id(self, language_id):
        """Sets the language_id of this Portion.


        :param language_id: The language_id of this Portion.  # noqa: E501
        :type: str
        """
        self._language_id = language_id

    @property
    def alternative_language_id(self):
        """Gets the alternative_language_id of this Portion.  # noqa: E501


        :return: The alternative_language_id of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._alternative_language_id

    @alternative_language_id.setter
    def alternative_language_id(self, alternative_language_id):
        """Sets the alternative_language_id of this Portion.


        :param alternative_language_id: The alternative_language_id of this Portion.  # noqa: E501
        :type: str
        """
        self._alternative_language_id = alternative_language_id

    @property
    def is_hard_underline_fill(self):
        """Gets the is_hard_underline_fill of this Portion.  # noqa: E501


        :return: The is_hard_underline_fill of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._is_hard_underline_fill

    @is_hard_underline_fill.setter
    def is_hard_underline_fill(self, is_hard_underline_fill):
        """Sets the is_hard_underline_fill of this Portion.


        :param is_hard_underline_fill: The is_hard_underline_fill of this Portion.  # noqa: E501
        :type: str
        """
        if is_hard_underline_fill is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if is_hard_underline_fill not in allowed_values:
                raise ValueError(
                    "Invalid value for `is_hard_underline_fill` ({0}), must be one of {1}"  # noqa: E501
                    .format(is_hard_underline_fill, allowed_values)
                )
        self._is_hard_underline_fill = is_hard_underline_fill

    @property
    def is_hard_underline_line(self):
        """Gets the is_hard_underline_line of this Portion.  # noqa: E501


        :return: The is_hard_underline_line of this Portion.  # noqa: E501
        :rtype: str
        """
        return self._is_hard_underline_line

    @is_hard_underline_line.setter
    def is_hard_underline_line(self, is_hard_underline_line):
        """Sets the is_hard_underline_line of this Portion.


        :param is_hard_underline_line: The is_hard_underline_line of this Portion.  # noqa: E501
        :type: str
        """
        if is_hard_underline_line is not None:
            allowed_values = ["False", "True", "NotDefined"]  # noqa: E501
            if is_hard_underline_line not in allowed_values:
                raise ValueError(
                    "Invalid value for `is_hard_underline_line` ({0}), must be one of {1}"  # noqa: E501
                    .format(is_hard_underline_line, allowed_values)
                )
        self._is_hard_underline_line = is_hard_underline_line

    @property
    def fill_format(self):
        """Gets the fill_format of this Portion.  # noqa: E501


        :return: The fill_format of this Portion.  # noqa: E501
        :rtype: FillFormat
        """
        return self._fill_format

    @fill_format.setter
    def fill_format(self, fill_format):
        """Sets the fill_format of this Portion.


        :param fill_format: The fill_format of this Portion.  # noqa: E501
        :type: FillFormat
        """
        self._fill_format = fill_format

    @property
    def effect_format(self):
        """Gets the effect_format of this Portion.  # noqa: E501


        :return: The effect_format of this Portion.  # noqa: E501
        :rtype: EffectFormat
        """
        return self._effect_format

    @effect_format.setter
    def effect_format(self, effect_format):
        """Sets the effect_format of this Portion.


        :param effect_format: The effect_format of this Portion.  # noqa: E501
        :type: EffectFormat
        """
        self._effect_format = effect_format

    @property
    def line_format(self):
        """Gets the line_format of this Portion.  # noqa: E501


        :return: The line_format of this Portion.  # noqa: E501
        :rtype: LineFormat
        """
        return self._line_format

    @line_format.setter
    def line_format(self, line_format):
        """Sets the line_format of this Portion.


        :param line_format: The line_format of this Portion.  # noqa: E501
        :type: LineFormat
        """
        self._line_format = line_format

    @property
    def underline_fill_format(self):
        """Gets the underline_fill_format of this Portion.  # noqa: E501


        :return: The underline_fill_format of this Portion.  # noqa: E501
        :rtype: FillFormat
        """
        return self._underline_fill_format

    @underline_fill_format.setter
    def underline_fill_format(self, underline_fill_format):
        """Sets the underline_fill_format of this Portion.


        :param underline_fill_format: The underline_fill_format of this Portion.  # noqa: E501
        :type: FillFormat
        """
        self._underline_fill_format = underline_fill_format

    @property
    def underline_line_format(self):
        """Gets the underline_line_format of this Portion.  # noqa: E501


        :return: The underline_line_format of this Portion.  # noqa: E501
        :rtype: LineFormat
        """
        return self._underline_line_format

    @underline_line_format.setter
    def underline_line_format(self, underline_line_format):
        """Sets the underline_line_format of this Portion.


        :param underline_line_format: The underline_line_format of this Portion.  # noqa: E501
        :type: LineFormat
        """
        self._underline_line_format = underline_line_format

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
        if not isinstance(other, Portion):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
