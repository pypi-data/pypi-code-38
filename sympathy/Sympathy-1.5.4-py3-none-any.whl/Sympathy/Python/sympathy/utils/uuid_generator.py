# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Flow elements UUID handling
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import uuid
import six


def generate_uuid():
    """
    Generate a unique UUID.
    :return: Unique UUID.
    """
    # The UUID version 1 algorithm is based on a hardware node and a clock.
    # It is guaranteed not to produce any duplicates as long as less than
    # 2**14 UUID:s are generated in 100ns.
    # http://stackoverflow.com/questions/1785503/when-should-i-use-uuid-uuid1-vs-uuid-uuid4-in-python
    # There are no privacy issues with using this UUID which means that
    # there is no problem basing it on the current hardware.
    # generate_uuid.counter += 1L
    return generate_uuid.new_uuid()


generate_uuid.new_uuid = lambda: six.text_type(u'{{{}}}'.format(uuid.uuid4()))


def join_uuid(namespace_uuid, item_uuid):
    """
    Join an instance UUID and an item UUID to one single string.
    :param namespace_uuid: String containing UUID for namespace.
    :param item_uuid: String containing UUID for item.
    :return: String with joined UUID.
    """
    return '.'.join((namespace_uuid, item_uuid))


def join_uuids(uuid_parts):
    """
    Join a list of UUIDs to a single string.
    :param uuid_parts: Sequence of strings, each containing a UUID.
    :return: String with joined UUIDs.
    """
    return '.'.join(uuid_parts)


def split_uuid(joined_uuid):
    """
    Split an instance UUID and an item UUID into components.
    :param joined_uuid: String containing joined UUID:s.
    :return: Tuple with two UUID:s.
    """
    return tuple(joined_uuid.split('.'))
