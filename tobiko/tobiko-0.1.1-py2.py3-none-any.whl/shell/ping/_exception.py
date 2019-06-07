# Copyright (c) 2019 Red Hat, Inc.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import tobiko


class PingException(tobiko.TobikoException):
    """Base ping command exception"""


class PingError(PingException):
    """Base ping error"""
    message = "{details!s}"


class LocalPingError(PingError):
    """Raised when local error happens"""


class SendToPingError(PingError):
    """Raised when sendto error happens"""


class UnknowHostError(PingError):
    """Raised when unable to resolve host name"""


class BadAddressPingError(PingError):
    """Raised when passing wrong address to ping command"""
    message = "bad address ({address!r})"


class PingFailed(PingError, tobiko.FailureException):
    """Raised when ping timeout expires before reaching expected message count

    """
    message = ("timeout of {timeout} seconds expired after counting only "
               "{count} out of expected {expected_count} ICMP messages of "
               "type {message_type!r}")
