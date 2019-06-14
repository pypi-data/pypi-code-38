# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="SignBarcodeOptions.py">
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

from groupdocs_signature_cloud.models import SignTextOptions

class SignBarcodeOptions(SignTextOptions):
    """
    Represents the Barcode signature options
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'barcode_type': 'str',
        'border_weight': 'float',
        'opacity': 'float',
        'code_text_alignment': 'str',
        'inner_margins': 'Padding'
    }

    attribute_map = {
        'barcode_type': 'BarcodeType',
        'border_weight': 'BorderWeight',
        'opacity': 'Opacity',
        'code_text_alignment': 'CodeTextAlignment',
        'inner_margins': 'InnerMargins'
    }

    def __init__(self, barcode_type=None, border_weight=None, opacity=None, code_text_alignment=None, inner_margins=None, **kwargs):  # noqa: E501
        """Initializes new instance of SignBarcodeOptions"""  # noqa: E501

        self._barcode_type = None
        self._border_weight = None
        self._opacity = None
        self._code_text_alignment = None
        self._inner_margins = None

        if barcode_type is not None:
            self.barcode_type = barcode_type
        if border_weight is not None:
            self.border_weight = border_weight
        if opacity is not None:
            self.opacity = opacity
        if code_text_alignment is not None:
            self.code_text_alignment = code_text_alignment
        if inner_margins is not None:
            self.inner_margins = inner_margins

        base = super(SignBarcodeOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def barcode_type(self):
        """
        Gets the barcode_type.  # noqa: E501

        Get or set Barcode type. Pick one from supported barcode types list  # noqa: E501

        :return: The barcode_type.  # noqa: E501
        :rtype: str
        """
        return self._barcode_type

    @barcode_type.setter
    def barcode_type(self, barcode_type):
        """
        Sets the barcode_type.

        Get or set Barcode type. Pick one from supported barcode types list  # noqa: E501

        :param barcode_type: The barcode_type.  # noqa: E501
        :type: str
        """
        self._barcode_type = barcode_type
    
    @property
    def border_weight(self):
        """
        Gets the border_weight.  # noqa: E501

        Gets or sets the weight of the signature border  # noqa: E501

        :return: The border_weight.  # noqa: E501
        :rtype: float
        """
        return self._border_weight

    @border_weight.setter
    def border_weight(self, border_weight):
        """
        Sets the border_weight.

        Gets or sets the weight of the signature border  # noqa: E501

        :param border_weight: The border_weight.  # noqa: E501
        :type: float
        """
        if border_weight is None:
            raise ValueError("Invalid value for `border_weight`, must not be `None`")  # noqa: E501
        self._border_weight = border_weight
    
    @property
    def opacity(self):
        """
        Gets the opacity.  # noqa: E501

        Gets or sets the signature opacity (value from 0.0 (clear) through 1.0 (opaque)). By default the value is 1.0  # noqa: E501

        :return: The opacity.  # noqa: E501
        :rtype: float
        """
        return self._opacity

    @opacity.setter
    def opacity(self, opacity):
        """
        Sets the opacity.

        Gets or sets the signature opacity (value from 0.0 (clear) through 1.0 (opaque)). By default the value is 1.0  # noqa: E501

        :param opacity: The opacity.  # noqa: E501
        :type: float
        """
        self._opacity = opacity
    
    @property
    def code_text_alignment(self):
        """
        Gets the code_text_alignment.  # noqa: E501

        Gets or sets the alignment of text in the result Barcode Default value is None  # noqa: E501

        :return: The code_text_alignment.  # noqa: E501
        :rtype: str
        """
        return self._code_text_alignment

    @code_text_alignment.setter
    def code_text_alignment(self, code_text_alignment):
        """
        Sets the code_text_alignment.

        Gets or sets the alignment of text in the result Barcode Default value is None  # noqa: E501

        :param code_text_alignment: The code_text_alignment.  # noqa: E501
        :type: str
        """
        if code_text_alignment is None:
            raise ValueError("Invalid value for `code_text_alignment`, must not be `None`")  # noqa: E501
        allowed_values = ["None", "Above", "Below", "Right"]  # noqa: E501
        if not code_text_alignment.isdigit():	
            if code_text_alignment not in allowed_values:
                raise ValueError(
                    "Invalid value for `code_text_alignment` ({0}), must be one of {1}"  # noqa: E501
                    .format(code_text_alignment, allowed_values))
            self._code_text_alignment = code_text_alignment
        else:
            self._code_text_alignment = allowed_values[int(code_text_alignment) if six.PY3 else long(code_text_alignment)]
    
    @property
    def inner_margins(self):
        """
        Gets the inner_margins.  # noqa: E501

        Gets or sets the space between Barcode elements and result image borders  # noqa: E501

        :return: The inner_margins.  # noqa: E501
        :rtype: Padding
        """
        return self._inner_margins

    @inner_margins.setter
    def inner_margins(self, inner_margins):
        """
        Sets the inner_margins.

        Gets or sets the space between Barcode elements and result image borders  # noqa: E501

        :param inner_margins: The inner_margins.  # noqa: E501
        :type: Padding
        """
        self._inner_margins = inner_margins

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
        if not isinstance(other, SignBarcodeOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
