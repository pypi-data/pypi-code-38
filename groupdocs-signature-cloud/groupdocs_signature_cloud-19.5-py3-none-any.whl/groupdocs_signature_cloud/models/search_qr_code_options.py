# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="SearchQRCodeOptions.py">
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

from groupdocs_signature_cloud.models import SearchOptions

class SearchQRCodeOptions(SearchOptions):
    """
    Defines options to search QR-Code signature of document
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'qr_code_type': 'str',
        'text': 'str',
        'match_type': 'str'
    }

    attribute_map = {
        'qr_code_type': 'QRCodeType',
        'text': 'Text',
        'match_type': 'MatchType'
    }

    def __init__(self, qr_code_type=None, text=None, match_type=None, **kwargs):  # noqa: E501
        """Initializes new instance of SearchQRCodeOptions"""  # noqa: E501

        self._qr_code_type = None
        self._text = None
        self._match_type = None

        if qr_code_type is not None:
            self.qr_code_type = qr_code_type
        if text is not None:
            self.text = text
        if match_type is not None:
            self.match_type = match_type

        base = super(SearchQRCodeOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def qr_code_type(self):
        """
        Gets the qr_code_type.  # noqa: E501

        Specifies Encode Type property to search barcodes. If this value is not set, search is processed for all supported barcode types  # noqa: E501

        :return: The qr_code_type.  # noqa: E501
        :rtype: str
        """
        return self._qr_code_type

    @qr_code_type.setter
    def qr_code_type(self, qr_code_type):
        """
        Sets the qr_code_type.

        Specifies Encode Type property to search barcodes. If this value is not set, search is processed for all supported barcode types  # noqa: E501

        :param qr_code_type: The qr_code_type.  # noqa: E501
        :type: str
        """
        self._qr_code_type = qr_code_type
    
    @property
    def text(self):
        """
        Gets the text.  # noqa: E501

        Specifies text for searching and matching in barcode signature  # noqa: E501

        :return: The text.  # noqa: E501
        :rtype: str
        """
        return self._text

    @text.setter
    def text(self, text):
        """
        Sets the text.

        Specifies text for searching and matching in barcode signature  # noqa: E501

        :param text: The text.  # noqa: E501
        :type: str
        """
        self._text = text
    
    @property
    def match_type(self):
        """
        Gets the match_type.  # noqa: E501

        Get or set barcode text Match Type search. It is used only when Text property is set  # noqa: E501

        :return: The match_type.  # noqa: E501
        :rtype: str
        """
        return self._match_type

    @match_type.setter
    def match_type(self, match_type):
        """
        Sets the match_type.

        Get or set barcode text Match Type search. It is used only when Text property is set  # noqa: E501

        :param match_type: The match_type.  # noqa: E501
        :type: str
        """
        if match_type is None:
            raise ValueError("Invalid value for `match_type`, must not be `None`")  # noqa: E501
        allowed_values = ["Exact", "StartsWith", "EndsWith", "Contains"]  # noqa: E501
        if not match_type.isdigit():	
            if match_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `match_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(match_type, allowed_values))
            self._match_type = match_type
        else:
            self._match_type = allowed_values[int(match_type) if six.PY3 else long(match_type)]

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
        if not isinstance(other, SearchQRCodeOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
