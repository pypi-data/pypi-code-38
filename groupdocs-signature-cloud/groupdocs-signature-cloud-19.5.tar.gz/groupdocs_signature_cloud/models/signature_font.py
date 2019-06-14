# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="SignatureFont.py">
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

class SignatureFont(object):
    """
    Create instance of SignatureFont class to specify Font properties
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'font_family': 'str',
        'font_size': 'float',
        'bold': 'bool',
        'italic': 'bool',
        'underline': 'bool'
    }

    attribute_map = {
        'font_family': 'FontFamily',
        'font_size': 'FontSize',
        'bold': 'Bold',
        'italic': 'Italic',
        'underline': 'Underline'
    }

    def __init__(self, font_family=None, font_size=None, bold=None, italic=None, underline=None, **kwargs):  # noqa: E501
        """Initializes new instance of SignatureFont"""  # noqa: E501

        self._font_family = None
        self._font_size = None
        self._bold = None
        self._italic = None
        self._underline = None

        if font_family is not None:
            self.font_family = font_family
        if font_size is not None:
            self.font_size = font_size
        if bold is not None:
            self.bold = bold
        if italic is not None:
            self.italic = italic
        if underline is not None:
            self.underline = underline
    
    @property
    def font_family(self):
        """
        Gets the font_family.  # noqa: E501

        Font Family Name  # noqa: E501

        :return: The font_family.  # noqa: E501
        :rtype: str
        """
        return self._font_family

    @font_family.setter
    def font_family(self, font_family):
        """
        Sets the font_family.

        Font Family Name  # noqa: E501

        :param font_family: The font_family.  # noqa: E501
        :type: str
        """
        self._font_family = font_family
    
    @property
    def font_size(self):
        """
        Gets the font_size.  # noqa: E501

        Font Size   # noqa: E501

        :return: The font_size.  # noqa: E501
        :rtype: float
        """
        return self._font_size

    @font_size.setter
    def font_size(self, font_size):
        """
        Sets the font_size.

        Font Size   # noqa: E501

        :param font_size: The font_size.  # noqa: E501
        :type: float
        """
        if font_size is None:
            raise ValueError("Invalid value for `font_size`, must not be `None`")  # noqa: E501
        self._font_size = font_size
    
    @property
    def bold(self):
        """
        Gets the bold.  # noqa: E501

        Apply Font Bold Style  # noqa: E501

        :return: The bold.  # noqa: E501
        :rtype: bool
        """
        return self._bold

    @bold.setter
    def bold(self, bold):
        """
        Sets the bold.

        Apply Font Bold Style  # noqa: E501

        :param bold: The bold.  # noqa: E501
        :type: bool
        """
        if bold is None:
            raise ValueError("Invalid value for `bold`, must not be `None`")  # noqa: E501
        self._bold = bold
    
    @property
    def italic(self):
        """
        Gets the italic.  # noqa: E501

        Apply Font Italic Style  # noqa: E501

        :return: The italic.  # noqa: E501
        :rtype: bool
        """
        return self._italic

    @italic.setter
    def italic(self, italic):
        """
        Sets the italic.

        Apply Font Italic Style  # noqa: E501

        :param italic: The italic.  # noqa: E501
        :type: bool
        """
        if italic is None:
            raise ValueError("Invalid value for `italic`, must not be `None`")  # noqa: E501
        self._italic = italic
    
    @property
    def underline(self):
        """
        Gets the underline.  # noqa: E501

        Apply Underline Style  # noqa: E501

        :return: The underline.  # noqa: E501
        :rtype: bool
        """
        return self._underline

    @underline.setter
    def underline(self, underline):
        """
        Sets the underline.

        Apply Underline Style  # noqa: E501

        :param underline: The underline.  # noqa: E501
        :type: bool
        """
        if underline is None:
            raise ValueError("Invalid value for `underline`, must not be `None`")  # noqa: E501
        self._underline = underline

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
        if not isinstance(other, SignatureFont):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
