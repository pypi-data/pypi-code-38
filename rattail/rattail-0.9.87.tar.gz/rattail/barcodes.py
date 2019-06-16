# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Barcode Utilities
"""

from __future__ import unicode_literals, absolute_import

# import re

import six


def upc_check_digit(data):
    """
    Calculates the check digit for ``data``, according to the standard
    `UPC algorithm <http://en.wikipedia.org/wiki/Check_digit#UPC>`_.  The check
    digit will be returned in integer form.
    """
    sum_ = 0
    for i in range(len(data) - 1, -1, -2):
        sum_ += int(data[i]) * 3
    for i in range(len(data) - 2, -1, -2):
        sum_ += int(data[i])
    remainder = sum_ % 10
    if remainder == 0:
        return 0
    return 10 - remainder


def luhn_check_digit(data):
    """
    Calculate the check digit for ``data`` according to the
    `Luhn algorithm <http://en.wikipedia.org/wiki/Luhn_algorithm>`_.  The check
    digit will be returned in integer form.
    """
    reverse_data = ''.join([x for x in reversed(data)])
    sum_ = 0
    for i in range(len(reverse_data)):
        digit = int(reverse_data[i])
        if i % 2 == 0:
            digit *= 2
            digit = sum([int(x) for x in six.text_type(digit)])
        sum_ += digit
    remainder = sum_ % 10
    if remainder == 0:
        return 0
    return 10 - remainder
        

def price_check_digit(data):
    """
    Calculates a check digit according to the `Price Check Digit algorithm`_.

    This typically would be used to validate a random weight UPC.
  
    :param data: The price data, without check digit.  The length of the data
       string must be exactly 4 characters.
    :type data: string

    :returns: The calculated check digit.
    :rtype: integer

    .. _Price Check Digit algorithm: http://barcodes.gs1us.org/GS1%20US%20BarCodes%20and%20eCom%20-%20The%20Global%20Language%20of%20Business.htm#PCD
    """
    if not isinstance(data, six.string_types) or len(data) != 4:
        raise ValueError("'data' must be 4-character string; got: {}".format(data))

    map1 = {0:0, 1:2, 2:4, 3:6, 4:8, 5:9, 6:1, 7:3, 8:5, 9:7}
    map2 = {0:0, 1:3, 2:6, 3:9, 4:2, 5:5, 6:8, 7:1, 8:4, 9:7}
    map3 = {0:0, 1:5, 2:9, 3:4, 4:8, 5:3, 6:7, 7:2, 8:6, 9:1}

    data = [int(x) for x in data]
    sum_ = map1[data[0]] + map1[data[1]] + map2[data[2]] + map3[data[3]]
    return int(six.text_type(3 * sum_)[-1])


def upce_to_upca(data, include_check_digit=False):
    """
    Converts a `UPC-E`_ (zero-compressed) barcode to its expanded UPC-A equivalent.

    :param data: The UPC-E barcode data.  The length of the data string must be
       either 6 or 8 characters.
    :type data: string

    :param include_check_digit: Whether or not to include the check digit in
       the return value.
    :type include_check_digit: boolean

    :returns: The expanded UPC-A barcode data.  The length of the data string
       will be 11 or 12 characters, depending on the ``include_check_digit``
       parameter.
    :rtype: string

    .. _UPC-E: http://en.wikipedia.org/wiki/Universal_Product_Code#UPC-E
    """
    if len(data) == 8:
        data = data[1:7]
    assert len(data) == 6
    assert data.isdigit()
    upce = data

    last_digit = int(upce[-1])

    if last_digit == 0:
        upca = "0%02u00000%03u" % (int(upce[0:2]), int(upce[2:5]))
    elif last_digit == 1:
        upca  = "0%02u10000%03u" % (int(upce[0:2]), int(upce[2:5]))
    elif last_digit == 2:
        upca = "0%02u20000%03u" % (int(upce[0:2]), int(upce[2:5]))
    elif last_digit == 3:
        upca = "0%03u00000%02u" % (int(upce[0:3]), int(upce[3:5]))
    elif last_digit == 4:
        upca = "0%04u00000%01u" % (int(upce[0:4]), int(upce[4]))
    elif last_digit == 5:
        upca = "0%05u00005" % int(upce[0:5])
    elif last_digit == 6:
        upca = "0%05u00006" % int(upce[0:5])
    elif last_digit == 7:
        upca = "0%05u00007" % int(upce[0:5])
    elif last_digit == 8:
        upca = "0%05u00008" % int(upce[0:5])
    elif last_digit == 9:
        upca = "0%05u00009" % int(upce[0:5])

    if include_check_digit:
        upca += six.text_type(upc_check_digit(upca))

    return upca


# TODO: Finish and verify this function, eventually...  (I wound up not needing
# it for the moment.)

# def upca_to_upce(upca):
#     """
#     Accepts a UPC-A barcode and returns its UPC-E (compressed) equivalent.

#     .. note::
#        Not all UPC-A barcodes support compression; in fact relatively few do.
#        This function will return ``None`` if it is not able to compress the
#        UPC-A it receives as input.
#     """
#     assert len(upca) == 11

#     m = re.match(r'^0(\d{2})00000(\d{3})$', upca)
#     if m:
#         return '%s%s0' % (m.group(1), m.group(2))
#     m = re.match(r'^0(\d{2})10000(\d{3})$', upca)
#     if m:
#         return '%s%s1' % (m.group(1), m.group(2))
#     m = re.match(r'^0(\d{2})20000(\d{3})$', upca)
#     if m:
#         return '%s%s2' % (m.group(1), m.group(2))
#     m = re.match(r'^0(\d{3})00000(\d{2})$', upca)
#     if m:
#         return '%s%s3' % (m.group(1), m.group(2))
#     m = re.match(r'^0(\d{4})00000(\d)$', upca)
#     if m:
#         return '%s%s4' % (m.group(1), m.group(2))
#     m = re.match(r'^0(\d{5})00005$', upca)
#     if m:
#         return '%s5' % m.group(1)
#     m = re.match(r'^0(\d{5})00006$', upca)
#     if m:
#         return '%s6' % m.group(1)
#     m = re.match(r'^0(\d{5})00007$', upca)
#     if m:
#         return '%s7' % m.group(1)
#     m = re.match(r'^0(\d{5})00008$', upca)
#     if m:
#         return '%s8' % m.group(1)
#     m = re.match(r'^0(\d{5})00009$', upca)
#     if m:
#         return '%s9' % m.group(1)
#     return None
