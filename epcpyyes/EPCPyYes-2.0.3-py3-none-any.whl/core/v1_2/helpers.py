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
# Copyright 2018 Rob Magee.  All rights reserved.
import re
import gettext
from datetime import datetime, timezone

_ = gettext.gettext


def get_iso_8601_regex():
    '''
    Returns a compiled ISO 8601 regex for use in validation of date strings.
    :return: A compiled regex.
    '''

    pattern = r'/(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+)|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d)|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d)/'
    return re.compile(pattern, re.VERBOSE)


def gtin_urn_generator(company_prefix, indicator, item_reference,
                       serial_numbers: list):
    '''
    A python generator that creates SGTIN URNs for the list of serial numbers
    passed in.

    :param company_prefix: The company prefix (GS1).
    :param indicator: The GS1 indicator digit for the GTIN
    :param item_reference: The item reference number for the GTIN
    :param serial_numbers: A list of serial numbers in string or integer format.
    :return: Generates a sgtin URN string for each serial number provided.
    '''
    prefix = 'urn:epc:id:sgtin:{0}.{1}{2}.'.format(company_prefix, indicator,
                                                   item_reference)
    if len(indicator) > 1:
        raise ValueError(_('The indicator may only be one digit in length.'))
    if len(company_prefix + indicator + item_reference) != 13:
        raise ValueError(_('The combined length of the company prefix,'
                           ' indicator digit and item reference number must'
                           ' be 13.'))
    for serial_number in serial_numbers:
        yield ''.join([prefix, str(serial_number)])


def sscc_urn_generator(company_prefix, extension, serial_numbers: list):
    '''
    A python generator that creates SSCC URNs for the list of serial numbers
    passed in.

    :param company_prefix: The company prefix (GS1).
    :param extension: The extension digit.
    :param serial_numbers: The serial reference numbers for the SSCC
    :return: Generates a SSCC URN string for each serial reference provided.
    '''
    sscc_length = 17
    prefix = 'urn:epc:id:sscc:{0}.{1}'.format(company_prefix, extension)

    for serial_number in serial_numbers:
        actual_length = len(company_prefix + extension + str(serial_number))
        if actual_length < sscc_length:
            padding = '0' * (sscc_length - actual_length)
        elif actual_length > sscc_length:
            raise ValueError(_('The combined length of the company prefix,'
                               ' extension digit and serial number'
                               ' must be 17 or less.'))
        else:
            padding = ''  # no padding by default.
        yield ''.join([prefix, padding, str(serial_number)])


def gtin_to_urn(company_prefix, indicator, item_reference,
                serial_number: str):
    '''
    A python generator that creates SGTIN URNs for the list of serial numbers
    passed in.

    :param company_prefix: The company prefix (GS1).
    :param indicator: The GS1 indicator digit for the GTIN
    :param item_reference: The item reference number for the GTIN
    :param serial_number: A serial number.
    :return: Generates a sgtin URN string for each serial number provided.
    '''
    return 'urn:epc:id:sgtin:{0}.{1}{2}.{3}'.format(company_prefix, indicator,
                                                    item_reference,
                                                    serial_number)


def get_current_utc_time_and_offset():
    '''
    Based on the inbound datetime value, it will reuturn the ISO string
    and the ISO timezone offset value.  Helps when creating EPCIS events
    on the fly.

    :param datetime: The datetime instance you want to convert to a string.
    :return: A two-tuple with the datetime ISO string and the ISO timezone
        offset.
    '''
    val = datetime.now(timezone.utc).isoformat()
    return val, val[-6:]


def gln13_data_to_sgln_urn(company_prefix, location_reference, extension='0'):
    '''
    Takes the three parameters and outputs a compliant EPCGlobal urn.
    The company prefix and location reference must be a total of 12 digits-
    do not send in the check digit as part of the location reference.

    :param company_prefix: The company prefix
    :param location_reference: The location reference
    :param extension: The id of the sub-site for the GLN
    :return: An TDS 1.9 compliant SGLN URN value.
    '''

    if not (len(str(company_prefix) + str(location_reference)) == 12):
        raise ValueError(
            _('The company prefix and location reference variables'
              ' must total 12 digits in lenght when combined.'))
    return 'urn:epc:id:sgln:{0}.{1}.{2}'.format(company_prefix,
                                                location_reference,
                                                extension)
