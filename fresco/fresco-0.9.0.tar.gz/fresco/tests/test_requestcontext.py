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

import pytest

from fresco import FrescoApp, GET, Response
from fresco.requestcontext import RequestContext


class TestRequestContext(object):

    def test_instantiation(self):
        """
        Can we cleanly instantiate a RequestContext object?
        """
        RequestContext()

    def test_app_populates_request_object(self):

        def view():
            from fresco.core import context
            assert context.request is not None
            return Response([''])

        app = FrescoApp()
        app.route('/', GET, view)

        with app.requestcontext('/'):
            app.view()

    def test_context_returns_correct_request_for_each_app(self):

        from time import sleep
        from threading import Thread, current_thread

        threadcount = 3
        itercount = 200
        calls = []

        def view():
            from fresco.core import context
            request_id = id(context.request)

            def generate_response():
                for i in range(itercount):
                    assert id(context.request) == request_id
                    calls.append(current_thread().ident)
                    sleep(0.0001)
                    yield str(request_id).encode('ascii')
            return Response(list(generate_response()))

        app = FrescoApp()
        app.route('/', GET, view)

        def do_request():
            with app.requestcontext('/'):
                app.view()

        threads = [Thread(target=do_request) for i in range(threadcount)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(calls) == threadcount * itercount

        # Check that threaded requests were genuinely interleaved
        for i1, i2 in zip(calls[:itercount - 1], calls[1:itercount]):
            if i1 != i2:
                break
        else:
            raise AssertionError("Output does not appear interleaved")

    def test_context_does_not_inherit_from_parent(self):
        c = RequestContext()
        c.push(foo=1)
        c.push(bar=2)
        with pytest.raises(AttributeError):
            c.foo

    def test_child_context_overrides_parent(self):
        c = RequestContext()
        c.push(foo=1)
        c.push(foo=2)
        assert c.foo == 2

    def test_pop_context_removes_keys(self):
        c = RequestContext()
        c.push(foo=1)
        c.push(foo=2)
        assert c.foo == 2
        c.pop()
        assert c.foo == 1
