# Copyright 2018 Red Hat
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

import testtools


FailureException = testtools.TestCase.failureException


def fail(msg, *args, **kwargs):
    """Fail immediately current test case execution, with the given message.

    Unconditionally raises a tobiko.FailureException as in below equivalent
    code:

        raise FailureException(msg.format(*args, **kwargs))

    :param msg: string message used to create FailureException
    :param *args: positional arguments to be passed to str.format method
    :param **kwargs: key-word arguments to be passed to str.format method
    :returns: It never returns
    :raises FailureException:
    """
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    raise FailureException(msg)
