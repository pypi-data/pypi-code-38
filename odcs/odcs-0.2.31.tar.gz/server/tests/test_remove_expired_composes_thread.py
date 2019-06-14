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

from odcs.server import db, conf
from odcs.server.models import Compose
from odcs.common.types import COMPOSE_STATES, COMPOSE_RESULTS
from odcs.server.backend import RemoveExpiredComposesThread
from odcs.server.pungi import PungiSourceType
from datetime import datetime, timedelta

from .utils import ModelsBaseTest

import os
import mock
from mock import patch


class TestRemoveExpiredComposesThread(ModelsBaseTest):
    maxDiff = None

    def setUp(self):
        super(TestRemoveExpiredComposesThread, self).setUp()

        compose = Compose.create(
            db.session, "unknown", PungiSourceType.MODULE, "testmodule-master",
            COMPOSE_RESULTS["repository"], 60)
        db.session.add(compose)
        db.session.commit()

        self.thread = RemoveExpiredComposesThread()

    def test_does_not_remove_a_compose_which_state_is_not_done(self):
        """
        Test that we do not remove a composes on non-done state.
        """
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        c.time_to_expire = datetime.utcnow() - timedelta(seconds=-120)

        for name, state in COMPOSE_STATES.items():
            if name == "done":
                # Compose with state DONE would be removed.
                continue
            c.state = state
            db.session.add(c)
            db.session.commit()
            self.thread.do_work()
            db.session.expunge_all()
            c = db.session.query(Compose).filter(Compose.id == 1).one()
            self.assertEqual(c.state, state)

    def test_a_compose_which_state_is_done_is_removed(self):
        """
        Test that we do remove a compose in done state.
        """
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        c.time_to_expire = datetime.utcnow() - timedelta(seconds=120)
        c.state = COMPOSE_STATES["done"]
        db.session.add(c)
        db.session.commit()
        self.thread.do_work()
        db.session.expunge_all()
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        self.assertEqual(c.state, COMPOSE_STATES["removed"])
        self.assertEqual(c.state_reason, 'Compose is expired.')

    def test_a_compose_which_state_is_done_is_removed_keep_state_reason(self):
        """
        Test that we do remove a compose in done state.
        """
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        c.time_to_expire = datetime.utcnow() - timedelta(seconds=120)
        c.state = COMPOSE_STATES["done"]
        c.state_reason = "Generated successfully."
        db.session.add(c)
        db.session.commit()
        self.thread.do_work()
        db.session.expunge_all()
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        self.assertEqual(c.state, COMPOSE_STATES["removed"])
        self.assertEqual(c.state_reason, 'Generated successfully.\nCompose is expired.')

    def test_does_not_remove_a_compose_which_is_not_expired(self):
        """
        Test that we do not remove a compose if its time_to_expire has not been
        reached yet.
        """
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        c.state = COMPOSE_STATES["done"]
        db.session.add(c)
        db.session.commit()
        self.thread.do_work()
        db.session.expunge_all()
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        self.assertEqual(c.state, COMPOSE_STATES["done"])

    def _mock_glob(self, glob, dirs):
        glob_ret_values = [[], []]
        for d in dirs:
            path = os.path.join(conf.target_dir, d)
            if d.startswith("latest-"):
                glob_ret_values[0].append(path)
            else:
                glob_ret_values[1].append(path)
        glob.side_effect = glob_ret_values

    @patch("os.path.isdir")
    @patch("glob.glob")
    @patch("odcs.server.backend.RemoveExpiredComposesThread._remove_compose_dir")
    def test_remove_left_composes(self, remove_compose_dir, glob, isdir):
        isdir.return_value = True
        self._mock_glob(glob, ["latest-odcs-96-1", "odcs-96-1-20171005.n.0"])
        self.thread.do_work()
        self.assertEqual(
            remove_compose_dir.call_args_list,
            [mock.call(os.path.join(conf.target_dir, "latest-odcs-96-1")),
             mock.call(os.path.join(conf.target_dir, "odcs-96-1-20171005.n.0"))])

    @patch("os.path.isdir")
    @patch("glob.glob")
    @patch("odcs.server.backend.RemoveExpiredComposesThread._remove_compose_dir")
    def test_remove_left_composes_not_dir(
            self, remove_compose_dir, glob, isdir):
        isdir.return_value = False
        self._mock_glob(glob, ["latest-odcs-96-1"])
        self.thread.do_work()
        remove_compose_dir.assert_not_called()

    @patch("os.path.isdir")
    @patch("glob.glob")
    @patch("odcs.server.backend.RemoveExpiredComposesThread._remove_compose_dir")
    def test_remove_left_composes_wrong_dir(
            self, remove_compose_dir, glob, isdir):
        isdir.return_value = True
        self._mock_glob(glob, ["latest-odcs-", "odcs-", "odcs-abc"])
        self.thread.do_work()
        remove_compose_dir.assert_not_called()

    @patch("os.path.isdir")
    @patch("glob.glob")
    @patch("odcs.server.backend.RemoveExpiredComposesThread._remove_compose_dir")
    def test_remove_left_composes_valid_compose(
            self, remove_compose_dir, glob, isdir):
        isdir.return_value = True
        self._mock_glob(glob, ["latest-odcs-1-1", "odcs-1-1-2017.n.0"])
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        c.state = COMPOSE_STATES["done"]
        db.session.add(c)
        db.session.commit()
        self.thread.do_work()
        remove_compose_dir.assert_not_called()

    @patch("os.path.isdir")
    @patch("glob.glob")
    @patch("odcs.server.backend.RemoveExpiredComposesThread._remove_compose_dir")
    def test_remove_left_composes_expired_compose(
            self, remove_compose_dir, glob, isdir):
        isdir.return_value = True
        self._mock_glob(glob, ["latest-odcs-1-1", "odcs-1-1-2017.n.0"])
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        c.state = COMPOSE_STATES["removed"]
        db.session.add(c)
        db.session.commit()
        self.thread.do_work()
        self.assertEqual(
            remove_compose_dir.call_args_list,
            [mock.call(os.path.join(conf.target_dir, "latest-odcs-1-1")),
             mock.call(os.path.join(conf.target_dir, "odcs-1-1-2017.n.0"))])

    @patch("shutil.rmtree")
    @patch("os.unlink")
    @patch("os.path.realpath")
    @patch("os.path.exists")
    def test_remove_compose_dir_symlink(
            self, exists, realpath, unlink, rmtree):
        exists.return_value = True
        toplevel_dir = "/odcs"
        realpath.return_value = "/odcs-real"

        self.thread._remove_compose_dir(toplevel_dir)
        unlink.assert_called_once()
        rmtree.assert_called_once()

    @patch("shutil.rmtree")
    @patch("os.unlink")
    @patch("os.path.realpath")
    @patch("os.path.exists")
    def test_remove_compose_dir_broken_symlink(
            self, exists, realpath, unlink, rmtree):
        def mocked_exists(p):
            return p != "/odcs-real"
        exists.side_effect = mocked_exists
        toplevel_dir = "/odcs"
        realpath.return_value = "/odcs-real"

        self.thread._remove_compose_dir(toplevel_dir)
        unlink.assert_called_once()
        rmtree.assert_not_called()

    @patch("shutil.rmtree")
    @patch("os.unlink")
    @patch("os.path.realpath")
    @patch("os.path.exists")
    def test_remove_compose_dir_real_dir(
            self, exists, realpath, unlink, rmtree):
        exists.return_value = True
        toplevel_dir = "/odcs"
        realpath.return_value = "/odcs"

        self.thread._remove_compose_dir(toplevel_dir)
        unlink.assert_not_called()
        rmtree.assert_called_once()

    @patch("os.unlink")
    @patch("os.path.realpath")
    @patch("os.path.exists")
    @patch("odcs.server.backend.log.warning")
    def test_remove_compose_rmtree_error(
            self, log_warning, exists, realpath, unlink):
        exists.return_value = True
        toplevel_dir = "/odcs"
        realpath.return_value = "/odcs-real"

        # This must not raise an exception.
        self.thread._remove_compose_dir(toplevel_dir)
        log_warning.assert_called()
