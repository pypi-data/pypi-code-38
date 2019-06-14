# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="VerifyDigitalOptions.py">
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

from groupdocs_signature_cloud.models import VerifyOptions

class VerifyDigitalOptions(VerifyOptions):
    """
    Defines options to verify Digital signature within a document
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'password': 'str',
        'certificate_guid': 'str',
        'comments': 'str',
        'sign_date_time_from': 'datetime',
        'sign_date_time_to': 'datetime',
        'reason': 'str',
        'contact': 'str',
        'location': 'str'
    }

    attribute_map = {
        'password': 'Password',
        'certificate_guid': 'CertificateGuid',
        'comments': 'Comments',
        'sign_date_time_from': 'SignDateTimeFrom',
        'sign_date_time_to': 'SignDateTimeTo',
        'reason': 'Reason',
        'contact': 'Contact',
        'location': 'Location'
    }

    def __init__(self, password=None, certificate_guid=None, comments=None, sign_date_time_from=None, sign_date_time_to=None, reason=None, contact=None, location=None, **kwargs):  # noqa: E501
        """Initializes new instance of VerifyDigitalOptions"""  # noqa: E501

        self._password = None
        self._certificate_guid = None
        self._comments = None
        self._sign_date_time_from = None
        self._sign_date_time_to = None
        self._reason = None
        self._contact = None
        self._location = None

        if password is not None:
            self.password = password
        if certificate_guid is not None:
            self.certificate_guid = certificate_guid
        if comments is not None:
            self.comments = comments
        if sign_date_time_from is not None:
            self.sign_date_time_from = sign_date_time_from
        if sign_date_time_to is not None:
            self.sign_date_time_to = sign_date_time_to
        if reason is not None:
            self.reason = reason
        if contact is not None:
            self.contact = contact
        if location is not None:
            self.location = location

        base = super(VerifyDigitalOptions, self)
        base.__init__(**kwargs)

        self.swagger_types.update(base.swagger_types)
        self.attribute_map.update(base.attribute_map)
    
    @property
    def password(self):
        """
        Gets the password.  # noqa: E501

        Password of Digital Certificate if required  # noqa: E501

        :return: The password.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Sets the password.

        Password of Digital Certificate if required  # noqa: E501

        :param password: The password.  # noqa: E501
        :type: str
        """
        self._password = password
    
    @property
    def certificate_guid(self):
        """
        Gets the certificate_guid.  # noqa: E501

        File Guid of Digital Certificate  # noqa: E501

        :return: The certificate_guid.  # noqa: E501
        :rtype: str
        """
        return self._certificate_guid

    @certificate_guid.setter
    def certificate_guid(self, certificate_guid):
        """
        Sets the certificate_guid.

        File Guid of Digital Certificate  # noqa: E501

        :param certificate_guid: The certificate_guid.  # noqa: E501
        :type: str
        """
        self._certificate_guid = certificate_guid
    
    @property
    def comments(self):
        """
        Gets the comments.  # noqa: E501

        Comments of Digital Signature to validate Suitable for Spreadsheet and Words Processing document types  # noqa: E501

        :return: The comments.  # noqa: E501
        :rtype: str
        """
        return self._comments

    @comments.setter
    def comments(self, comments):
        """
        Sets the comments.

        Comments of Digital Signature to validate Suitable for Spreadsheet and Words Processing document types  # noqa: E501

        :param comments: The comments.  # noqa: E501
        :type: str
        """
        self._comments = comments
    
    @property
    def sign_date_time_from(self):
        """
        Gets the sign_date_time_from.  # noqa: E501

        Date and time range of Digital Signature to validate. Null value will be ignored. Suitable for Spreadsheet and Words Processing document types  # noqa: E501

        :return: The sign_date_time_from.  # noqa: E501
        :rtype: datetime
        """
        return self._sign_date_time_from

    @sign_date_time_from.setter
    def sign_date_time_from(self, sign_date_time_from):
        """
        Sets the sign_date_time_from.

        Date and time range of Digital Signature to validate. Null value will be ignored. Suitable for Spreadsheet and Words Processing document types  # noqa: E501

        :param sign_date_time_from: The sign_date_time_from.  # noqa: E501
        :type: datetime
        """
        self._sign_date_time_from = sign_date_time_from
    
    @property
    def sign_date_time_to(self):
        """
        Gets the sign_date_time_to.  # noqa: E501

        Date and time range of Digital Signature to validate. Null value will be ignored Suitable for Spreadsheet and Words Processing document types  # noqa: E501

        :return: The sign_date_time_to.  # noqa: E501
        :rtype: datetime
        """
        return self._sign_date_time_to

    @sign_date_time_to.setter
    def sign_date_time_to(self, sign_date_time_to):
        """
        Sets the sign_date_time_to.

        Date and time range of Digital Signature to validate. Null value will be ignored Suitable for Spreadsheet and Words Processing document types  # noqa: E501

        :param sign_date_time_to: The sign_date_time_to.  # noqa: E501
        :type: datetime
        """
        self._sign_date_time_to = sign_date_time_to
    
    @property
    def reason(self):
        """
        Gets the reason.  # noqa: E501

        Reason of Digital Signature to validate Suitable for Pdf document type  # noqa: E501

        :return: The reason.  # noqa: E501
        :rtype: str
        """
        return self._reason

    @reason.setter
    def reason(self, reason):
        """
        Sets the reason.

        Reason of Digital Signature to validate Suitable for Pdf document type  # noqa: E501

        :param reason: The reason.  # noqa: E501
        :type: str
        """
        self._reason = reason
    
    @property
    def contact(self):
        """
        Gets the contact.  # noqa: E501

        Signature Contact to validate Suitable for Pdf document type  # noqa: E501

        :return: The contact.  # noqa: E501
        :rtype: str
        """
        return self._contact

    @contact.setter
    def contact(self, contact):
        """
        Sets the contact.

        Signature Contact to validate Suitable for Pdf document type  # noqa: E501

        :param contact: The contact.  # noqa: E501
        :type: str
        """
        self._contact = contact
    
    @property
    def location(self):
        """
        Gets the location.  # noqa: E501

        Signature Location to validate Suitable for Pdf document type  # noqa: E501

        :return: The location.  # noqa: E501
        :rtype: str
        """
        return self._location

    @location.setter
    def location(self, location):
        """
        Sets the location.

        Signature Location to validate Suitable for Pdf document type  # noqa: E501

        :param location: The location.  # noqa: E501
        :type: str
        """
        self._location = location

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
        if not isinstance(other, VerifyDigitalOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
