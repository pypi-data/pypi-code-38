# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="Signature.py">
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

class Signature(object):
    """
    Describes base class for signatures
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'document_type': 'str',
        'signature_type': 'str'
    }

    attribute_map = {
        'document_type': 'DocumentType',
        'signature_type': 'SignatureType'
    }

    def __init__(self, document_type=None, signature_type=None, **kwargs):  # noqa: E501
        """Initializes new instance of Signature"""  # noqa: E501

        self._document_type = None
        self._signature_type = None

        if document_type is not None:
            self.document_type = document_type
        if signature_type is not None:
            self.signature_type = signature_type
    
    @property
    def document_type(self):
        """
        Gets the document_type.  # noqa: E501

        Specifies the type of document to process (Image, Pdf, Presentation, Spreadsheet, WordProcessing)  # noqa: E501

        :return: The document_type.  # noqa: E501
        :rtype: str
        """
        return self._document_type

    @document_type.setter
    def document_type(self, document_type):
        """
        Sets the document_type.

        Specifies the type of document to process (Image, Pdf, Presentation, Spreadsheet, WordProcessing)  # noqa: E501

        :param document_type: The document_type.  # noqa: E501
        :type: str
        """
        if document_type is None:
            raise ValueError("Invalid value for `document_type`, must not be `None`")  # noqa: E501
        allowed_values = ["Image", "Pdf", "Presentation", "Spreadsheet", "WordProcessing"]  # noqa: E501
        if not document_type.isdigit():	
            if document_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `document_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(document_type, allowed_values))
            self._document_type = document_type
        else:
            self._document_type = allowed_values[int(document_type) if six.PY3 else long(document_type)]
    
    @property
    def signature_type(self):
        """
        Gets the signature_type.  # noqa: E501

        Specifies the signature type (Text, Image, Digital, Barcode, QRCode, Stamp)  # noqa: E501

        :return: The signature_type.  # noqa: E501
        :rtype: str
        """
        return self._signature_type

    @signature_type.setter
    def signature_type(self, signature_type):
        """
        Sets the signature_type.

        Specifies the signature type (Text, Image, Digital, Barcode, QRCode, Stamp)  # noqa: E501

        :param signature_type: The signature_type.  # noqa: E501
        :type: str
        """
        if signature_type is None:
            raise ValueError("Invalid value for `signature_type`, must not be `None`")  # noqa: E501
        allowed_values = ["None", "Text", "Image", "Digital", "Barcode", "QRCode", "Stamp"]  # noqa: E501
        if not signature_type.isdigit():	
            if signature_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `signature_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(signature_type, allowed_values))
            self._signature_type = signature_type
        else:
            self._signature_type = allowed_values[int(signature_type) if six.PY3 else long(signature_type)]

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
        if not isinstance(other, Signature):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
