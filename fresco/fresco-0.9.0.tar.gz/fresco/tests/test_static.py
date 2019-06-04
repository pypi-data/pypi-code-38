from __future__ import absolute_import

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
import sys
import os
import re
from calendar import timegm
from email.utils import formatdate, parsedate
from mock import Mock
from tempfile import mkstemp
from fresco import FrescoApp
from fresco.static import serve_static_file


class TestServeStaticFile():

    def setup(self):

        fh, tmpname = mkstemp()
        self.tmpname = tmpname
        self.mtime = int(os.path.getmtime(self.tmpname))
        os.close(fh)

    def teardown(self):
        os.unlink(self.tmpname)

    def parse_lmh(self, last_modified):
        return timegm(parsedate(last_modified))

    def make_ims(self, since, tz=0):
        return {'HTTP_IF_MODIFIED_SINCE': formatdate(since, tz)}

    def test_sets_last_modified_header(self):
        with FrescoApp().requestcontext():
            response = serve_static_file(self.tmpname)
            response.content_iterator.close()

        last_modified = response.get_header('Last-Modified')
        assert self.parse_lmh(last_modified) == self.mtime

    def test_full_response_when_if_modified_before_mtime(self):
        with FrescoApp().requestcontext(**self.make_ims(0)):
            response = serve_static_file(self.tmpname)
            response.content_iterator.close()

        last_modified = response.get_header('Last-Modified')
        assert response.status_code == 200
        assert self.parse_lmh(last_modified) == self.mtime

    def test_304_when_if_modified_after_mtime(self):
        with FrescoApp().requestcontext(**self.make_ims(self.mtime + 1)):
            response = serve_static_file(self.tmpname)
        assert response.status_code == 304

    def test_304_when_if_modified_after_mtime_with_tz1(self):
        with FrescoApp().requestcontext(**self.make_ims(self.mtime + 1, +1)):
            response = serve_static_file(self.tmpname)
        assert response.status_code == 304

    def test_304_when_if_modified_after_mtime_with_tz2(self):
        with FrescoApp().requestcontext(**self.make_ims(self.mtime + 1, -1)):
            response = serve_static_file(self.tmpname)
        assert response.status_code == 304

    def test_it_doesnt_fail_with_an_out_of_range_modified_since_value1(self):
        year = sys.maxsize
        with FrescoApp().requestcontext(
                HTTP_IF_MODIFIED_SINCE='"Wed, 09 Feb %s 04:46:40 GMT"' % year):
            response = serve_static_file(self.tmpname)
        assert response.status_code == 400

    def test_it_doesnt_fail_with_an_out_of_range_modified_since_value2(self):
        with FrescoApp().requestcontext(
                HTTP_IF_MODIFIED_SINCE='"Wed, 01 Feb -2001 04:46:40 GMT"'):
            response = serve_static_file(self.tmpname)
        assert response.status_code == 400

    def test_last_modified_format_is_correct(self):
        with FrescoApp().requestcontext():
            response = serve_static_file(self.tmpname)
            response.content_iterator.close()

        assert re.match(r'^\w{3}, \d{1,2} \w{3} \d{4} \d\d:\d\d:\d\d GMT',
                        response.get_header('last-modified'))

    def test_filewrapper_used_if_present(self):
        with FrescoApp().requestcontext() as c:
            file_wrapper = Mock(return_value=[])
            c.request.environ['wsgi.file_wrapper'] = file_wrapper
            serve_static_file(self.tmpname)

        assert file_wrapper.call_count == 1

    def test_it_returns_not_found(self):
        with FrescoApp().requestcontext():
            response = serve_static_file(self.tmpname + 'x')
        assert response.status_code == 404

    def test_it_returns_forbidden(self):
        with FrescoApp().requestcontext():
            os.chmod(self.tmpname, 0)
            response = serve_static_file(self.tmpname)
        assert response.status_code == 403
