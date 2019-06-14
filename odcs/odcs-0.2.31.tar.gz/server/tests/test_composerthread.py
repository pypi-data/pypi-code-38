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
import time
from datetime import datetime, timedelta

from mock import patch, MagicMock, call

import odcs.server
from odcs.server import db, app, conf
from odcs.server.models import Compose
from odcs.common.types import COMPOSE_STATES, COMPOSE_RESULTS, COMPOSE_FLAGS
from odcs.server.backend import ComposerThread, resolve_compose
from odcs.server.pungi import PungiSourceType

from .utils import ModelsBaseTest
from .mbs import mock_mbs

thisdir = os.path.abspath(os.path.dirname(__file__))


class TestComposerThread(ModelsBaseTest):
    maxDiff = None

    def setUp(self):
        self.client = app.test_client()
        super(TestComposerThread, self).setUp()
        self.composer = ComposerThread()

        patched_pungi_conf_path = os.path.join(thisdir, '../conf/pungi.conf')
        self.patch_pungi_conf_path = patch.object(odcs.server.conf,
                                                  'pungi_conf_path',
                                                  new=patched_pungi_conf_path)
        self.patch_pungi_conf_path.start()

        self.patch_update_cache = patch("odcs.server.backend.KojiTagCache.update_cache")
        self.update_cache = self.patch_update_cache.start()

    def tearDown(self):
        super(TestComposerThread, self).tearDown()
        self.patch_pungi_conf_path.stop()
        self.patch_update_cache.stop()

    def _wait_for_compose_state(self, id, state):
        c = None
        for i in range(20):
            db.session.expire_all()
            c = db.session.query(Compose).filter(Compose.id == id).one()
            if c.state == state:
                return c
            time.sleep(0.1)
        return c

    def _add_module_compose(self, source="testmodule-master-20170515074419",
                            flags=0):
        compose = Compose.create(
            db.session, "unknown", PungiSourceType.MODULE, source,
            COMPOSE_RESULTS["repository"], 60)
        db.session.add(compose)
        db.session.commit()

    def _add_tag_compose(self, packages=None, flags=0):
        compose = Compose.create(
            db.session, "unknown", PungiSourceType.KOJI_TAG, "f26",
            COMPOSE_RESULTS["repository"], 60, packages, flags)
        db.session.add(compose)
        db.session.commit()

    def _add_repo_composes(self):
        old_c = Compose.create(
            db.session, "me", PungiSourceType.REPO, os.path.join(thisdir, "repo"),
            COMPOSE_RESULTS["repository"], 3600, packages="ed")
        old_c.state = COMPOSE_STATES["done"]
        resolve_compose(old_c)
        c = Compose.create(
            db.session, "me", PungiSourceType.REPO, os.path.join(thisdir, "repo"),
            COMPOSE_RESULTS["repository"], 3600, packages="ed")
        db.session.add(old_c)
        db.session.add(c)
        db.session.commit()

    @mock_mbs
    @patch("odcs.server.utils.execute_cmd")
    @patch("odcs.server.backend._write_repo_file")
    def test_submit_build(self, wrf, execute_cmd):
        self._add_module_compose()
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        self.assertEqual(c.state, COMPOSE_STATES["wait"])

        self.assertEqual(self.composer.currently_generating, [])

        self.composer.do_work()
        c = self._wait_for_compose_state(1, COMPOSE_STATES["done"])
        self.assertEqual(c.state, COMPOSE_STATES["done"])
        self.assertEqual(c.result_repo_dir,
                         os.path.join(odcs.server.conf.target_dir, "latest-odcs-1-1/compose/Temporary"))
        self.assertEqual(c.result_repo_url, "http://localhost/odcs/latest-odcs-1-1/compose/Temporary")
        self.assertEqual(self.composer.currently_generating, [1])

    @mock_mbs
    @patch("odcs.server.utils.execute_cmd")
    @patch("odcs.server.backend._write_repo_file")
    def test_submit_build_module_without_release(
            self, wrf, execute_cmd):
        self._add_module_compose("testmodule-master")
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        self.assertEqual(c.state, COMPOSE_STATES["wait"])

        self.composer.do_work()
        c = self._wait_for_compose_state(1, COMPOSE_STATES["done"])
        self.assertEqual(c.state, COMPOSE_STATES["done"])
        self.assertEqual(c.result_repo_dir,
                         os.path.join(odcs.server.conf.target_dir, "latest-odcs-1-1/compose/Temporary"))
        self.assertEqual(c.result_repo_url, "http://localhost/odcs/latest-odcs-1-1/compose/Temporary")
        self.assertEqual(c.source, "testmodule:master:20170515074419")

    @mock_mbs
    @patch("odcs.server.utils.execute_cmd")
    @patch("odcs.server.backend._write_repo_file")
    def test_submit_build_colon_separator(self, wrf, execute_cmd):
        self._add_module_compose("testmodule:master:20170515074419")
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        self.assertEqual(c.state, COMPOSE_STATES["wait"])

        self.assertEqual(self.composer.currently_generating, [])

        self.composer.do_work()
        c = self._wait_for_compose_state(1, COMPOSE_STATES["done"])
        self.assertEqual(c.state, COMPOSE_STATES["done"])
        self.assertEqual(c.result_repo_dir,
                         os.path.join(odcs.server.conf.target_dir, "latest-odcs-1-1/compose/Temporary"))
        self.assertEqual(c.result_repo_url, "http://localhost/odcs/latest-odcs-1-1/compose/Temporary")
        self.assertEqual(self.composer.currently_generating, [1])

    @mock_mbs
    @patch("odcs.server.utils.execute_cmd")
    @patch("odcs.server.backend._write_repo_file")
    def test_submit_build_module_without_release_colon_separator(
            self, wrf, execute_cmd):
        self._add_module_compose("testmodule:master")
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        self.assertEqual(c.state, COMPOSE_STATES["wait"])

        self.composer.do_work()
        c = self._wait_for_compose_state(1, COMPOSE_STATES["done"])
        self.assertEqual(c.state, COMPOSE_STATES["done"])
        self.assertEqual(c.result_repo_dir,
                         os.path.join(odcs.server.conf.target_dir, "latest-odcs-1-1/compose/Temporary"))
        self.assertEqual(c.result_repo_url, "http://localhost/odcs/latest-odcs-1-1/compose/Temporary")
        self.assertEqual(c.source, "testmodule:master:20170515074419")

    @mock_mbs
    @patch("odcs.server.utils.execute_cmd")
    @patch("odcs.server.backend._write_repo_file")
    def test_submit_build_module_without_release_not_in_mbs(
            self, wrf, execute_cmd):

        self._add_module_compose("testmodule2-master")
        c = db.session.query(Compose).filter(Compose.id == 1).one()
        self.assertEqual(c.state, COMPOSE_STATES["wait"])

        self.composer.do_work()
        c = self._wait_for_compose_state(1, COMPOSE_STATES["failed"])
        self.assertEqual(c.state, COMPOSE_STATES["failed"])

    @mock_mbs
    @patch("odcs.server.backend.validate_pungi_compose")
    def test_submit_build_reuse_repo(self, mock_validate_pungi_compose):
        self._add_repo_composes()
        c = db.session.query(Compose).filter(Compose.id == 2).one()

        self.composer.do_work()
        c = self._wait_for_compose_state(2, COMPOSE_STATES["done"])
        self.assertEqual(c.reused_id, 1)
        self.assertEqual(c.state, COMPOSE_STATES["done"])
        self.assertEqual(c.result_repo_dir,
                         os.path.join(odcs.server.conf.target_dir, "latest-odcs-1-1/compose/Temporary"))
        self.assertEqual(c.result_repo_url, "http://localhost/odcs/latest-odcs-1-1/compose/Temporary")
        mock_validate_pungi_compose.assert_called_once()

    @mock_mbs
    def test_submit_build_reuse_module(self):
        self._add_module_compose()
        self._add_module_compose()
        old_c = db.session.query(Compose).filter(Compose.id == 1).one()
        old_c.state = COMPOSE_STATES["done"]
        resolve_compose(old_c)
        db.session.commit()

        self.composer.do_work()
        c = self._wait_for_compose_state(2, COMPOSE_STATES["done"])
        self.assertEqual(c.reused_id, 1)
        self.assertEqual(c.state, COMPOSE_STATES["done"])
        self.assertEqual(c.result_repo_dir,
                         os.path.join(odcs.server.conf.target_dir, "latest-odcs-1-1/compose/Temporary"))
        self.assertEqual(c.result_repo_url, "http://localhost/odcs/latest-odcs-1-1/compose/Temporary")

    @mock_mbs
    @patch("odcs.server.utils.execute_cmd")
    @patch("odcs.server.backend._write_repo_file")
    def test_submit_build_no_reuse_module(self, wrf, execute_cmd):
        self._add_module_compose()
        self._add_module_compose("testmodule-master-20170515074418")
        old_c = db.session.query(Compose).filter(Compose.id == 1).one()
        old_c.state = COMPOSE_STATES["done"]
        resolve_compose(old_c)
        db.session.commit()

        self.composer.do_work()
        c = self._wait_for_compose_state(2, COMPOSE_STATES["done"])
        self.assertEqual(c.reused_id, None)
        self.assertEqual(c.state, COMPOSE_STATES["done"])
        self.assertEqual(c.result_repo_dir,
                         os.path.join(odcs.server.conf.target_dir, "latest-odcs-2-1/compose/Temporary"))
        self.assertEqual(c.result_repo_url, "http://localhost/odcs/latest-odcs-2-1/compose/Temporary")

    @patch("odcs.server.backend.create_koji_session")
    @patch("odcs.server.backend._write_repo_file")
    def test_submit_build_no_deps(self, wrf, create_koji_session):
        """
        Checks that "no_deps" flags properly sets gather_method to nodeps.
        """
        koji_session = MagicMock()
        create_koji_session.return_value = koji_session
        koji_session.getLastEvent.return_value = {"id": 123}

        def mocked_execute_cmd(args, stdout=None, stderr=None, cwd=None, **kwargs):
            pungi_cfg = open(os.path.join(cwd, "pungi.conf"), "r").read()
            self.assertTrue(pungi_cfg.find("gather_method = 'nodeps'") != -1)

        with patch("odcs.server.utils.execute_cmd", new=mocked_execute_cmd):
            self._add_tag_compose(flags=COMPOSE_FLAGS["no_deps"])
            c = db.session.query(Compose).filter(Compose.id == 1).one()
            self.assertEqual(c.state, COMPOSE_STATES["wait"])

            self.composer.do_work()
            c = self._wait_for_compose_state(1, COMPOSE_STATES["done"])
            self.assertEqual(c.state, COMPOSE_STATES["done"])

    @patch("odcs.server.backend.create_koji_session")
    def test_submit_build_reuse_koji_tag(self, create_koji_session):
        koji_session = MagicMock()
        create_koji_session.return_value = koji_session
        koji_session.getLastEvent.return_value = {"id": 123}
        koji_session.tagChangedSinceEvent.return_value = False

        self._add_tag_compose()
        self._add_tag_compose()
        old_c = db.session.query(Compose).filter(Compose.id == 1).one()
        old_c.state = COMPOSE_STATES["done"]
        resolve_compose(old_c)
        db.session.commit()

        self.composer.do_work()
        c = self._wait_for_compose_state(2, COMPOSE_STATES["done"])
        self.assertEqual(c.reused_id, 1)
        self.assertEqual(c.state, COMPOSE_STATES["done"])
        self.assertEqual(c.result_repo_dir,
                         os.path.join(odcs.server.conf.target_dir, "latest-odcs-1-1/compose/Temporary"))
        self.assertEqual(c.result_repo_url, "http://localhost/odcs/latest-odcs-1-1/compose/Temporary")

    @patch("odcs.server.utils.execute_cmd")
    @patch("odcs.server.backend.create_koji_session")
    @patch("odcs.server.backend._write_repo_file")
    def test_submit_build_reuse_koji_tag_tags_changed(
            self, wrf, create_koji_session, execute_cmd):
        koji_session = MagicMock()
        create_koji_session.return_value = koji_session
        koji_session.getLastEvent.return_value = {"id": 123}
        koji_session.tagChangedSinceEvent.return_value = True

        self._add_tag_compose()
        self._add_tag_compose()
        old_c = db.session.query(Compose).filter(Compose.id == 1).one()
        old_c.state = COMPOSE_STATES["done"]
        resolve_compose(old_c)
        db.session.commit()

        self.composer.do_work()
        c = self._wait_for_compose_state(2, COMPOSE_STATES["done"])
        self.assertEqual(c.reused_id, None)
        self.assertEqual(c.state, COMPOSE_STATES["done"])
        self.assertEqual(c.result_repo_dir,
                         os.path.join(odcs.server.conf.target_dir, "latest-odcs-2-1/compose/Temporary"))
        self.assertEqual(c.result_repo_url, "http://localhost/odcs/latest-odcs-2-1/compose/Temporary")


class TestComposerThreadLostComposes(ModelsBaseTest):
    maxDiff = None

    def setUp(self):
        self.client = app.test_client()
        super(TestComposerThreadLostComposes, self).setUp()
        self.composer = ComposerThread()

        self.patch_generate_new_compose = patch(
            "odcs.server.backend.ComposerThread.generate_new_compose")
        self.generate_new_compose = self.patch_generate_new_compose.start()

    def tearDown(self):
        super(TestComposerThreadLostComposes, self).tearDown()
        self.patch_generate_new_compose.stop()

    def _add_test_compose(self, state):
        compose = Compose.create(
            db.session, "unknown", PungiSourceType.KOJI_TAG, "f26",
            COMPOSE_RESULTS["repository"], 60, "", 0)
        compose.state = state
        db.session.add(compose)
        db.session.commit()
        return compose

    def test_generate_lost_composes_generating_state(self):
        compose = self._add_test_compose(COMPOSE_STATES["generating"])
        self.composer.do_work()
        self.generate_new_compose.assert_called_once_with(compose)

    def test_generate_lost_composes_currently_generating(self):
        compose = self._add_test_compose(COMPOSE_STATES["generating"])
        self.composer.currently_generating.append(compose.id)
        self.composer.do_work()
        self.generate_new_compose.assert_not_called()

    def test_generate_lost_composes_all_states(self):
        for state in ["wait", "done", "removed", "failed"]:
            self._add_test_compose(COMPOSE_STATES[state])

        self.composer.generate_lost_composes()
        self.generate_new_compose.assert_not_called()

    def test_refresh_currently_generating(self):
        generating = self._add_test_compose(COMPOSE_STATES["generating"])
        done = self._add_test_compose(COMPOSE_STATES["done"])

        self.composer.currently_generating += [done.id, generating.id]
        self.composer.do_work()
        self.assertEqual(self.composer.currently_generating, [generating.id])


class TestComposerThreadStuckWaitComposes(ModelsBaseTest):
    maxDiff = None

    def setUp(self):
        self.client = app.test_client()
        super(TestComposerThreadStuckWaitComposes, self).setUp()
        self.composer = ComposerThread()

        self.patch_generate_new_compose = patch(
            "odcs.server.backend.ComposerThread.generate_new_compose")
        self.generate_new_compose = self.patch_generate_new_compose.start()

    def tearDown(self):
        super(TestComposerThreadStuckWaitComposes, self).tearDown()
        self.patch_generate_new_compose.stop()

    def _add_test_compose(self, state, time_submitted=None,
                          source_type=PungiSourceType.KOJI_TAG):
        compose = Compose.create(
            db.session, "unknown", source_type, "f26",
            COMPOSE_RESULTS["repository"], 60, "", 0)
        compose.state = state
        if time_submitted:
            compose.time_submitted = time_submitted
        db.session.add(compose)
        db.session.commit()
        return compose

    def test_pickup_waiting_composes_generating_state(self):
        time_submitted = datetime.utcnow() - timedelta(minutes=5)
        composes = []
        for i in range(10):
            composes.append(self._add_test_compose(
                COMPOSE_STATES["wait"], time_submitted=time_submitted))
        composes = sorted(composes, key=lambda c: c.id)
        self.composer.pickup_waiting_composes()
        self.generate_new_compose.assert_has_calls([
            call(composes[0]), call(composes[1]), call(composes[2]),
            call(composes[3])])

    def test_pickup_waiting_composes_generating_state_not_old_enough(self):
        composes = []
        for i in range(10):
            composes.append(self._add_test_compose(
                COMPOSE_STATES["wait"]))
        composes = sorted(composes, key=lambda c: c.id)
        self.composer.pickup_waiting_composes()
        self.generate_new_compose.assert_not_called()

    def test_pickup_waiting_composes_generating_state_old(self):
        time_submitted = datetime.utcnow() - timedelta(days=5)
        composes = []
        for i in range(10):
            composes.append(self._add_test_compose(
                COMPOSE_STATES["wait"], time_submitted=time_submitted))
        composes = sorted(composes, key=lambda c: c.id)
        self.composer.pickup_waiting_composes()
        self.generate_new_compose.assert_not_called()

    def test_generate_lost_composes_generating_state(self):
        composes = []
        for i in range(10):
            composes.append(self._add_test_compose(COMPOSE_STATES["generating"]))
        composes = sorted(composes, key=lambda c: c.id)
        self.composer.pickup_waiting_composes()
        self.generate_new_compose.assert_not_called()

    def test_pickup_waiting_composes_no_limit_for_pulp(self):
        time_submitted = datetime.utcnow() - timedelta(minutes=5)
        composes = []
        for i in range(10):
            composes.append(self._add_test_compose(
                COMPOSE_STATES["wait"], time_submitted=time_submitted))
        for i in range(10):
            composes.append(self._add_test_compose(
                COMPOSE_STATES["wait"], time_submitted=time_submitted,
                source_type=PungiSourceType.PULP))
        composes = sorted(composes, key=lambda c: c.id)
        self.composer.pickup_waiting_composes()
        self.generate_new_compose.assert_has_calls([
            call(composes[0]), call(composes[1]), call(composes[2]),
            call(composes[3]), call(composes[10]), call(composes[11]),
            call(composes[12]), call(composes[13]), call(composes[14]),
            call(composes[15]), call(composes[16]), call(composes[17]),
            call(composes[18]), call(composes[19])])

    def test_fail_lost_generating_composes(self):
        t = datetime.utcnow() - timedelta(seconds=2 * conf.pungi_timeout)

        time_submitted = t - timedelta(minutes=5)
        compose_to_fail = self._add_test_compose(
            COMPOSE_STATES["generating"], time_submitted=time_submitted)

        time_submitted = t + timedelta(minutes=5)
        compose_to_keep = self._add_test_compose(
            COMPOSE_STATES["generating"], time_submitted=time_submitted)

        self.composer.fail_lost_generating_composes()
        db.session.commit()
        db.session.expire_all()

        self.assertEqual(compose_to_fail.state, COMPOSE_STATES["failed"])
        self.assertEqual(compose_to_keep.state, COMPOSE_STATES["generating"])
