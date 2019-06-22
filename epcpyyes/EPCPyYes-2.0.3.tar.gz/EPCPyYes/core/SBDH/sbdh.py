# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.

import enum
from datetime import datetime
from typing import List
from uuid import uuid4


class PartnerType(enum.Enum):
    '''
    The SBDH must have partners as either senders or receivers- this
    enum is used to denote this distinction between Partner instances.
    '''
    SENDER = 'Sender'
    RECEIVER = 'Receiver'

    def __str__(self):
        return self.value

class PartnerIdentification(object):
    '''
    PartnerIdentification as defined in the GS1 SBDH schema.
    '''

    def __init__(self, authority: str, value: str):
        '''
        Initializes a new PI class
        :param authority: The authority attribute, for example 'EAN.UCC'
        :param value: The value associated with that authority attribute.
        '''
        self._authority = authority
        self._value = value

    @property
    def authority(self):
        return self._authority

    @authority.setter
    def authority(self, value):
        self._authority = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Partner(object):
    '''
    Partner represents the partner as defined in the GS1 SBDH schema of
    the same name.
    '''

    def __init__(
            self,
            partner_type: PartnerType,
            partner_id: PartnerIdentification = None,
            contact: str = None,
            email_address: str = None,
            fax_number: str = None,
            telephone_number: str = None,
            contact_type_identifier: str = None
    ):
        self._partner_type = partner_type
        self._partner_id = partner_id
        self._contact = contact
        self._email_address = email_address
        self._fax_number = fax_number
        self._telephone_number = telephone_number
        self._contact_type_identifier = contact_type_identifier

    @property
    def partner_type(self):
        '''
        Returns the value of the PartnerIdentification enum.
        :return: String- the value of the PartnerIdentification enum.
        '''
        return self._partner_type.value

    @partner_type.setter
    def partner_type(self, value: PartnerIdentification):
        if not isinstance(value, PartnerIdentification):
            raise TypeError('Requires a PartnerIdentification instance.')
        self._partner_type = value

    @property
    def partner_id(self):
        return self._partner_id

    @partner_id.setter
    def partner_id(self, value):
        self._partner_id = value

    @property
    def contact(self):
        return self._contact

    @contact.setter
    def contact(self, value):
        self._contact = value

    @property
    def email_address(self):
        return self._email_address

    @email_address.setter
    def email_address(self, value):
        self._email_address = value

    @property
    def fax_number(self):
        return self._fax_number

    @fax_number.setter
    def fax_number(self, value):
        self._fax_number = value

    @property
    def telephone_number(self):
        return self._telephone_number

    @telephone_number.setter
    def telephone_number(self, value):
        self._telephone_number = value

    @property
    def contact_type_identifier(self):
        return self._contact_type_identifier

    @contact_type_identifier.setter
    def contact_type_identifier(self, value):
        self._contact_type_identifier = value

    @property
    def has_contact_info(self):
        return self._contact or self._email_address or self._fax_number or \
               self._telephone_number or self._contact_type_identifier


class DocumentType(enum.Enum):
    '''
    As defined on page 85 of the EPCIS 1.2 standard- these are the possible
    values for the 'Type' value for the DocumentIdentification element of
    the SBDH.
    '''
    EVENTS = 'Events'
    MASTER_DATA = 'MasterData'
    QUERYCONTROL_REQUEST = 'QueryControl-Request'
    QUERYCONTROL_RESPONSE = 'QueryControl-Reponse'
    QUERYCALLBACK = 'QueryCallBack'
    QUERY = 'Query'

    def __str__(self):
        return self.value

class DocumentIdentification(object):
    '''
    As defined by the SBDH GS1 standard in the schema of the same name.
    '''

    def __init__(
            self,
            standard: str = 'EPCglobal',
            type_version: str = '1.0',
            instance_identifier: str = None,
            document_type: DocumentType = DocumentType.EVENTS,
            multiple_type: bool = None,
            creation_date_and_time: datetime = None
    ):
        self._standard = standard
        self._type_version = type_version
        self._instance_identifier = instance_identifier or str(uuid4())
        self._document_type = document_type
        self._multiple_type = multiple_type
        self._creation_date_and_time = creation_date_and_time

    @property
    def standard(self):
        return self._standard

    @standard.setter
    def standard(self, value):
        self._standard = value

    @property
    def type_version(self):
        return self._type_version

    @type_version.setter
    def type_version(self, value):
        self._type_version = value

    @property
    def instance_identifier(self):
        return self._instance_identifier

    @instance_identifier.setter
    def instance_identifier(self, value):
        self._instance_identifier = value

    @property
    def document_type(self):
        '''
        Returns the string value of the document type enum.
        :return: A string value of the DocumentType enum.
        '''
        if isinstance(self._document_type, DocumentType):
            ret = self._document_type.value
        else:
            ret = self._document_type
        return ret

    @document_type.setter
    def document_type(self, value: DocumentType):
        self._document_type = value

    @property
    def multiple_type(self):
        '''
        Note: returns an XML compatible lower-case bool string.
        :return: 'true' or 'false'
        '''
        if isinstance(self._multiple_type, bool):
            ret = str(self._multiple_type).lower()
        else:
            ret = self._multiple_type
        return ret

    @multiple_type.setter
    def multiple_type(self, value: bool):
        self._multiple_type = value

    @property
    def creation_date_and_time(self):
        '''
        Returns a string representation of the _creation_date_and_time
        field.
        :return: ISO 8601 date string.
        '''
        if isinstance(self._creation_date_and_time, datetime):
            ret = self._creation_date_and_time.isformat()
        else:
            ret = self._creation_date_and_time
        return ret

    @creation_date_and_time.setter
    def creation_date_and_time(self, value: datetime):
        '''
        Set the date and time of creation.
        :param value: A datetime.datetime instance.
        :return: Will return an ISO 8601 date string.
        '''
        self._creation_date_and_time = value


PartnerList = List[Partner]


class StandardBusinessDocumentHeader(object):
    '''
    The SBDH header as defined in the GS1 protocol.
    '''

    def __init__(
            self,
            namespace: str = 'sbdh',
            schema_location=('http://www.unece.org/cefact/namespaces/'
                             'StandardBusinessDocumentHeader'),
            document_identification: DocumentIdentification = None,
            partners: PartnerList = None,
            header_version: str = '1.0',
    ):
        self._header_version = header_version
        self._namespace = namespace
        self._schema_location = schema_location
        self._document_identification = \
            document_identification or DocumentIdentification()
        self._partners = partners

    @property
    def header_version(self):
        return self._header_version

    @header_version.setter
    def header_version(self, value: str):
        self._header_version = value

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, value):
        self._namespace = value

    @property
    def document_identification(self):
        return self._document_identification

    @document_identification.setter
    def document_identification(self, value: DocumentIdentification):
        self._document_identification = value

    @property
    def partners(self):
        return self._partners

    @partners.setter
    def partners(self, value: PartnerList):
        self._partners = value

    @property
    def schema_location(self):
        return self._schema_location

    @schema_location.setter
    def schema_location(self, value):
        self._schema_location = value
