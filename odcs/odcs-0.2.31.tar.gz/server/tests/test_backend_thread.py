# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

from odcs.server.backend import BackendThread
from .utils import ModelsBaseTest
from mock import patch


class TestBackendThread(ModelsBaseTest):
    maxDiff = None

    def setUp(self):
        super(TestBackendThread, self).setUp()

        self.patch_do_work = patch(
            "odcs.server.backend.BackendThread.do_work", autospec=True)
        self.do_work = self.patch_do_work.start()

        self.thread = BackendThread()

    def tearDown(self):
        super(TestBackendThread, self).tearDown()

        self.patch_do_work.stop()

    @patch("odcs.server.backend.db.session.rollback")
    def test_do_work_exception(self, rollback):
        def mocked_do_work(backend_thread):
            # Stop the backend thread at first, so we won't wait for timeout.
            backend_thread.stop()
            raise ValueError("expected exception")

        self.do_work.side_effect = mocked_do_work
        self.thread._run()
        rollback.assert_called_once()
