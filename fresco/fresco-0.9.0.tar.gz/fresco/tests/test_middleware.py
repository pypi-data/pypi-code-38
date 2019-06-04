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

from fresco import FrescoApp, context, GET, Response
from fresco.middleware import XForwarded


class TestXForwarded(object):

    def get_app(self, *args, **kwargs):
        app = FrescoApp()

        @app.route('/', GET)
        def view():
            request = context.request
            return Response([request.url, request.environ['REMOTE_ADDR']])
        app.add_middleware(XForwarded, *args, **kwargs)
        return app

    def test_forwards_x_forwarded_for(self):

        app = self.get_app()
        with app.requestcontext('/',
                                REMOTE_ADDR='127.0.0.1',
                                HTTP_X_FORWARDED_FOR='1.2.3.4'):
            url, addr = app.view().content_iterator
            assert addr == b'1.2.3.4'

    def test_forwards_x_forwarded_host(self):

        app = self.get_app()
        with app.requestcontext('/',
                                REMOTE_ADDR='127.0.0.1',
                                HTTP_X_FORWARDED_HOST='frontendserver'):
            url, addr = app.view().content_iterator
        assert url == b'http://frontendserver/'

    def test_forwards_x_forwarded_ssl(self):

        app = self.get_app()
        with app.requestcontext('/',
                                REMOTE_ADDR='127.0.0.1',
                                HTTP_X_FORWARDED_SSL='on',
                                HTTP_X_FORWARDED_HOST='localhost'):
            url, addr = app.view().content_iterator
            assert url == b'https://localhost/'

    def test_forwards_x_forwarded_proto(self):

        app = self.get_app()
        with app.requestcontext('/',
                                REMOTE_ADDR='127.0.0.1',
                                HTTP_X_FORWARDED_PROTO='https',
                                HTTP_X_FORWARDED_HOST='localhost'):
            url, addr = app.view().content_iterator
            assert url == b'https://localhost/'

    def test_reports_first_trusted_ip(self):
        app = self.get_app(trusted=['127.0.0.1', '3.3.3.3'])
        with app.requestcontext('/',
                                REMOTE_ADDR='127.0.0.1',
                                HTTP_X_FORWARDED_FOR='1.1.1.1, '
                                                     '2.2.2.2, 3.3.3.3'):
            url, addr = app.view().content_iterator
            assert addr == b'2.2.2.2'

    def test_reports_first_listed_ip_as_remote_addr_when_untrusted(self):
        app = self.get_app()
        with app.requestcontext('/',
                                REMOTE_ADDR='127.0.0.1',
                                HTTP_X_FORWARDED_FOR='1.1.1.1, 2.2.2.2'):
            url, addr = app.view().content_iterator
            assert addr == b'1.1.1.1'
