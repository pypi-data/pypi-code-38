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
from __future__ import absolute_import

from fresco.util.common import object_or_404
from fresco.exceptions import NotFound
import pytest


class TestObjectOr404(object):

    def test_it_returns_the_object(self):
        ob = object()
        assert object_or_404(ob) is ob

    def test_it_raises_NotFound(self):
        with pytest.raises(NotFound):
            object_or_404(None)

    def test_it_raises_custom_exception(self):
        class Foo(Exception):
            pass
        with pytest.raises(Foo):
            object_or_404(None, exception=Foo)
