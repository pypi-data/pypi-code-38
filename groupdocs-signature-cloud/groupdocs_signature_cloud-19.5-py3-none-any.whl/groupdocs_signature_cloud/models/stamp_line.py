# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="StampLine.py">
#   Copyright (c) 2003-2019 Aspose Pty Ltd
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

class StampLine(object):
    """
    Specify Stamp line properties
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'height': 'int',
        'background_color': 'Color',
        'text': 'str',
        'font': 'SignatureFont',
        'text_color': 'Color',
        'text_bottom_intent': 'int',
        'text_repeat_type': 'str',
        'outer_border': 'BorderLine',
        'inner_border': 'BorderLine',
        'visible': 'bool'
    }

    attribute_map = {
        'height': 'Height',
        'background_color': 'BackgroundColor',
        'text': 'Text',
        'font': 'Font',
        'text_color': 'TextColor',
        'text_bottom_intent': 'TextBottomIntent',
        'text_repeat_type': 'TextRepeatType',
        'outer_border': 'OuterBorder',
        'inner_border': 'InnerBorder',
        'visible': 'Visible'
    }

    def __init__(self, height=None, background_color=None, text=None, font=None, text_color=None, text_bottom_intent=None, text_repeat_type=None, outer_border=None, inner_border=None, visible=None, **kwargs):  # noqa: E501
        """Initializes new instance of StampLine"""  # noqa: E501

        self._height = None
        self._background_color = None
        self._text = None
        self._font = None
        self._text_color = None
        self._text_bottom_intent = None
        self._text_repeat_type = None
        self._outer_border = None
        self._inner_border = None
        self._visible = None

        if height is not None:
            self.height = height
        if background_color is not None:
            self.background_color = background_color
        if text is not None:
            self.text = text
        if font is not None:
            self.font = font
        if text_color is not None:
            self.text_color = text_color
        if text_bottom_intent is not None:
            self.text_bottom_intent = text_bottom_intent
        if text_repeat_type is not None:
            self.text_repeat_type = text_repeat_type
        if outer_border is not None:
            self.outer_border = outer_border
        if inner_border is not None:
            self.inner_border = inner_border
        if visible is not None:
            self.visible = visible
    
    @property
    def height(self):
        """
        Gets the height.  # noqa: E501

        Gets or sets the line height on Stamp  # noqa: E501

        :return: The height.  # noqa: E501
        :rtype: int
        """
        return self._height

    @height.setter
    def height(self, height):
        """
        Sets the height.

        Gets or sets the line height on Stamp  # noqa: E501

        :param height: The height.  # noqa: E501
        :type: int
        """
        if height is None:
            raise ValueError("Invalid value for `height`, must not be `None`")  # noqa: E501
        self._height = height
    
    @property
    def background_color(self):
        """
        Gets the background_color.  # noqa: E501

        Gets or sets the background color of signature  # noqa: E501

        :return: The background_color.  # noqa: E501
        :rtype: Color
        """
        return self._background_color

    @background_color.setter
    def background_color(self, background_color):
        """
        Sets the background_color.

        Gets or sets the background color of signature  # noqa: E501

        :param background_color: The background_color.  # noqa: E501
        :type: Color
        """
        self._background_color = background_color
    
    @property
    def text(self):
        """
        Gets the text.  # noqa: E501

        Gets or sets the text of stamp line  # noqa: E501

        :return: The text.  # noqa: E501
        :rtype: str
        """
        return self._text

    @text.setter
    def text(self, text):
        """
        Sets the text.

        Gets or sets the text of stamp line  # noqa: E501

        :param text: The text.  # noqa: E501
        :type: str
        """
        self._text = text
    
    @property
    def font(self):
        """
        Gets the font.  # noqa: E501

        Get or set Font of Stamp Line text  # noqa: E501

        :return: The font.  # noqa: E501
        :rtype: SignatureFont
        """
        return self._font

    @font.setter
    def font(self, font):
        """
        Sets the font.

        Get or set Font of Stamp Line text  # noqa: E501

        :param font: The font.  # noqa: E501
        :type: SignatureFont
        """
        self._font = font
    
    @property
    def text_color(self):
        """
        Gets the text_color.  # noqa: E501

        Gets or sets the text color of signature  # noqa: E501

        :return: The text_color.  # noqa: E501
        :rtype: Color
        """
        return self._text_color

    @text_color.setter
    def text_color(self, text_color):
        """
        Sets the text_color.

        Gets or sets the text color of signature  # noqa: E501

        :param text_color: The text_color.  # noqa: E501
        :type: Color
        """
        self._text_color = text_color
    
    @property
    def text_bottom_intent(self):
        """
        Gets the text_bottom_intent.  # noqa: E501

        Gets or sets the bottom intent of text  # noqa: E501

        :return: The text_bottom_intent.  # noqa: E501
        :rtype: int
        """
        return self._text_bottom_intent

    @text_bottom_intent.setter
    def text_bottom_intent(self, text_bottom_intent):
        """
        Sets the text_bottom_intent.

        Gets or sets the bottom intent of text  # noqa: E501

        :param text_bottom_intent: The text_bottom_intent.  # noqa: E501
        :type: int
        """
        if text_bottom_intent is None:
            raise ValueError("Invalid value for `text_bottom_intent`, must not be `None`")  # noqa: E501
        self._text_bottom_intent = text_bottom_intent
    
    @property
    def text_repeat_type(self):
        """
        Gets the text_repeat_type.  # noqa: E501

        Gets or sets text repeat type  # noqa: E501

        :return: The text_repeat_type.  # noqa: E501
        :rtype: str
        """
        return self._text_repeat_type

    @text_repeat_type.setter
    def text_repeat_type(self, text_repeat_type):
        """
        Sets the text_repeat_type.

        Gets or sets text repeat type  # noqa: E501

        :param text_repeat_type: The text_repeat_type.  # noqa: E501
        :type: str
        """
        if text_repeat_type is None:
            raise ValueError("Invalid value for `text_repeat_type`, must not be `None`")  # noqa: E501
        allowed_values = ["None", "FullTextRepeat", "RepeatWithTruncation"]  # noqa: E501
        if not text_repeat_type.isdigit():	
            if text_repeat_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `text_repeat_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(text_repeat_type, allowed_values))
            self._text_repeat_type = text_repeat_type
        else:
            self._text_repeat_type = allowed_values[int(text_repeat_type) if six.PY3 else long(text_repeat_type)]
    
    @property
    def outer_border(self):
        """
        Gets the outer_border.  # noqa: E501

        Setup Outer Border  # noqa: E501

        :return: The outer_border.  # noqa: E501
        :rtype: BorderLine
        """
        return self._outer_border

    @outer_border.setter
    def outer_border(self, outer_border):
        """
        Sets the outer_border.

        Setup Outer Border  # noqa: E501

        :param outer_border: The outer_border.  # noqa: E501
        :type: BorderLine
        """
        self._outer_border = outer_border
    
    @property
    def inner_border(self):
        """
        Gets the inner_border.  # noqa: E501

        Setup Internal Border  # noqa: E501

        :return: The inner_border.  # noqa: E501
        :rtype: BorderLine
        """
        return self._inner_border

    @inner_border.setter
    def inner_border(self, inner_border):
        """
        Sets the inner_border.

        Setup Internal Border  # noqa: E501

        :param inner_border: The inner_border.  # noqa: E501
        :type: BorderLine
        """
        self._inner_border = inner_border
    
    @property
    def visible(self):
        """
        Gets the visible.  # noqa: E501

        Get and set visibility of Stamp Line  # noqa: E501

        :return: The visible.  # noqa: E501
        :rtype: bool
        """
        return self._visible

    @visible.setter
    def visible(self, visible):
        """
        Sets the visible.

        Get and set visibility of Stamp Line  # noqa: E501

        :param visible: The visible.  # noqa: E501
        :type: bool
        """
        if visible is None:
            raise ValueError("Invalid value for `visible`, must not be `None`")  # noqa: E501
        self._visible = visible

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
        if not isinstance(other, StampLine):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
