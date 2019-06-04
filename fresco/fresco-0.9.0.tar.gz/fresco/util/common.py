# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
#
"""
Common utilities for writing applications in fresco
"""
from __future__ import absolute_import

from fresco.exceptions import NotFound

__all__ = ['object_or_404']


def object_or_404(ob, exception=NotFound):
    """
    Return the value of ``ob`` if it is not None. Otherwise raise a NotFound
    exception.
    """
    if ob is None:
        raise exception()
    return ob


def fq_path(ob):
    """
    Return the fully qualified path of ``ob``, expected to be a function or
    method
    """
    name = getattr(ob, '__qualname__', None) or \
            getattr(ob, '__name__', None) or repr(ob)
    module = getattr(ob, '__module__', None) or ''
    return '{}.{}'.format(module, name)
