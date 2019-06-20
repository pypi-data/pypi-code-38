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


import os
from os import path
import shutil
import tempfile

from module_build_service import log, models
from module_build_service.logger import ModuleBuildLogs
from module_build_service.scheduler.consumer import MBSConsumer
from tests import init_data


class TestLogger:
    def setup_method(self, test_method):
        init_data(1)
        log.debug(test_method.__module__)
        try:
            # py2
            test_id = ".".join([
                path.splitext(path.basename(__file__))[0],
                test_method.im_class.__name__,
                test_method.im_func.__name__,
            ])
        except AttributeError:
            # py3
            test_id = ".".join([
                path.splitext(path.basename(__file__))[0],
                test_method.__self__.__class__.__name__,
                test_method.__self__.__class__.__name__,
            ])

        self.base = tempfile.mkdtemp(prefix="mbs-", suffix="-%s" % test_id)
        self.name_format = "build-{id}.log"
        print("Storing build logs in %r" % self.base)
        self.build_log = ModuleBuildLogs(self.base, self.name_format)

    def teardown_method(self, test_method):
        MBSConsumer.current_module_build_id = None
        shutil.rmtree(self.base)

    def test_module_build_logs(self):
        """
        Tests that ModuleBuildLogs is logging properly to build log file.
        """
        build = models.ModuleBuild.query.filter_by(id=2).one()

        # Initialize logging, get the build log path and remove it to
        # ensure we are not using some garbage from previous failed test.
        self.build_log.start(build)
        path = self.build_log.path(build)
        assert path[len(self.base):] == "/build-2.log"
        if os.path.exists(path):
            os.unlink(path)

        # Try logging without the MBSConsumer.current_module_build_id set.
        # No log file should be created.
        log.debug("ignore this test msg")
        log.info("ignore this test msg")
        log.warning("ignore this test msg")
        log.error("ignore this test msg")
        self.build_log.stop(build)
        assert not os.path.exists(path)

        # Try logging with current_module_build_id set to 2 and then to 2.
        # Only messages with current_module_build_id set to 2 should appear in
        # the log.
        self.build_log.start(build)
        MBSConsumer.current_module_build_id = 1
        log.debug("ignore this test msg1")
        log.info("ignore this test msg1")
        log.warning("ignore this test msg1")
        log.error("ignore this test msg1")

        MBSConsumer.current_module_build_id = 2
        log.debug("ignore this test msg2")
        log.info("ignore this test msg2")
        log.warning("ignore this test msg2")
        log.error("ignore this test msg2")

        self.build_log.stop(build)
        assert os.path.exists(path)
        with open(path, "r") as f:
            data = f.read()
            # Note that DEBUG is not present unless configured server-wide.
            for level in ["INFO", "WARNING", "ERROR"]:
                assert data.find("MBS - {0} - ignore this test msg2".format(level)) != -1

        # Try to log more messages when build_log for module 1 is stopped.
        # New messages should not appear in a log.
        MBSConsumer.current_module_build_id = 2
        log.debug("ignore this test msg3")
        log.info("ignore this test msg3")
        log.warning("ignore this test msg3")
        log.error("ignore this test msg3")
        self.build_log.stop(build)
        with open(path, "r") as f:
            data = f.read()
            assert data.find("ignore this test msg3") == -1

    def test_module_build_logs_name_format(self):
        build = models.ModuleBuild.query.filter_by(id=2).one()

        log1 = ModuleBuildLogs("/some/path", "build-{id}.log")
        assert log1.name(build) == "build-2.log"
        assert log1.path(build) == "/some/path/build-2.log"

        log2 = ModuleBuildLogs("/some/path", "build-{name}-{stream}-{version}.log")
        assert log2.name(build) == "build-nginx-1-2.log"
        assert log2.path(build) == "/some/path/build-nginx-1-2.log"
