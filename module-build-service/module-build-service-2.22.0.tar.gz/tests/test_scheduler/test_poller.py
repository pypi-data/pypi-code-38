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

import pytest
from mock import patch
from module_build_service import models, conf
from tests import reuse_component_init_data, db, clean_database
import mock
import koji
from module_build_service.scheduler.producer import MBSProducer
from module_build_service.messaging import KojiTagChange
import six.moves.queue as queue
from datetime import datetime, timedelta


@patch(
    "module_build_service.builder.GenericBuilder.default_buildroot_groups",
    return_value={"build": [], "srpm-build": []},
)
@patch("module_build_service.scheduler.consumer.get_global_consumer")
@patch("module_build_service.builder.GenericBuilder.create_from_module")
class TestPoller:
    def setup_method(self, test_method):
        reuse_component_init_data()

        self.p_read_config = patch(
            "koji.read_config",
            return_value={
                "authtype": "kerberos",
                "timeout": 60,
                "server": "http://koji.example.com/",
            },
        )
        self.mock_read_config = self.p_read_config.start()

    def teardown_method(self, test_method):
        self.p_read_config.stop()
        clean_database()

    @pytest.mark.parametrize("fresh", [True, False])
    @patch("module_build_service.utils.batches.start_build_component")
    def test_process_paused_module_builds(
        self, start_build_component, create_builder, global_consumer, dbg, fresh
    ):
        """
        Tests general use-case of process_paused_module_builds.
        """
        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        builder = mock.MagicMock()
        create_builder.return_value = builder

        # Change the batch to 2, so the module build is in state where
        # it is not building anything, but the state is "build".
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 2
        # If fresh is set, then we simulate that activity just occurred 2 minutes ago on the build
        if fresh:
            module_build.time_modified = datetime.utcnow() - timedelta(minutes=2)
        else:
            module_build.time_modified = datetime.utcnow() - timedelta(days=5)
        db.session.commit()

        # Poll :)
        hub = mock.MagicMock()
        poller = MBSProducer(hub)
        poller.poll()

        # Refresh our module_build object.
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        db.session.refresh(module_build)

        # If fresh is set, we expect the poller to not touch the module build since it's been less
        # than 10 minutes of inactivity
        if fresh:
            expected_state = None
            expected_build_calls = 0
        else:
            expected_state = koji.BUILD_STATES["BUILDING"]
            expected_build_calls = 2

        components = module_build.current_batch()
        for component in components:
            assert component.state == expected_state

        assert len(start_build_component.mock_calls) == expected_build_calls

    @patch.dict("sys.modules", krbV=mock.MagicMock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_trigger_new_repo_when_failed(
        self, ClientSession, create_builder, global_consumer, dbg
    ):
        """
        Tests that we call koji_sesion.newRepo when newRepo task failed.
        """
        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        koji_session = ClientSession.return_value
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["FAILED"]}
        koji_session.newRepo.return_value = 123456

        builder = mock.MagicMock()
        builder.buildroot_ready.return_value = False
        create_builder.return_value = builder

        # Change the batch to 2, so the module build is in state where
        # it is not building anything, but the state is "build".
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 2
        module_build.new_repo_task_id = 123456
        db.session.commit()

        hub = mock.MagicMock()
        poller = MBSProducer(hub)
        poller.poll()

        koji_session.newRepo.assert_called_once_with(
            "module-testmodule-master-20170219191323-c40c156c-build")

    @patch.dict("sys.modules", krbV=mock.MagicMock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_trigger_new_repo_when_succeeded(
        self, ClientSession, create_builder, global_consumer, dbg
    ):
        """
        Tests that we do not call koji_sesion.newRepo when newRepo task
        succeeded.
        """
        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        koji_session = ClientSession.return_value
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456

        builder = mock.MagicMock()
        builder.buildroot_ready.return_value = False
        create_builder.return_value = builder

        # Change the batch to 2, so the module build is in state where
        # it is not building anything, but the state is "build".
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 2
        module_build.new_repo_task_id = 123456
        db.session.commit()

        hub = mock.MagicMock()
        poller = MBSProducer(hub)
        poller.poll()

        # Refresh our module_build object.
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        db.session.refresh(module_build)

        assert not koji_session.newRepo.called
        assert module_build.new_repo_task_id == 0

    def test_process_paused_module_builds_waiting_for_repo(
        self, create_builder, global_consumer, dbg
    ):
        """
        Tests that process_paused_module_builds does not start new batch
        when we are waiting for repo.
        """
        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        builder = mock.MagicMock()
        create_builder.return_value = builder

        # Change the batch to 2, so the module build is in state where
        # it is not building anything, but the state is "build".
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 2
        module_build.new_repo_task_id = 123456
        db.session.commit()

        # Poll :)
        hub = mock.MagicMock()
        poller = MBSProducer(hub)
        poller.poll()

        # Refresh our module_build object.
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        db.session.refresh(module_build)

        # Components should not be in building state
        components = module_build.current_batch()
        for component in components:
            assert component.state is None

    @patch.dict("sys.modules", krbV=mock.MagicMock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_old_build_targets_are_not_associated_with_any_module_builds(
        self, ClientSession, create_builder, global_consumer, dbg
    ):
        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        koji_session = ClientSession.return_value
        # No created module build has any of these tags.
        koji_session.getBuildTargets.return_value = [
            {"dest_tag_name": "module-xxx-1"},
            {"dest_tag_name": "module-yyy-2"},
        ]

        hub = mock.MagicMock()
        poller = MBSProducer(hub)
        poller.delete_old_koji_targets(conf, db.session)

        koji_session.deleteBuildTarget.assert_not_called()

    @patch.dict("sys.modules", krbV=mock.MagicMock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_dont_delete_base_module_build_target(
        self, ClientSession, create_builder, global_consumer, dbg
    ):
        module_build = models.ModuleBuild.query.filter_by(id=3).one()

        koji_session = ClientSession.return_value
        # No created module build has any of these tags.
        koji_session.getBuildTargets.return_value = [{"dest_tag_name": module_build.koji_tag}]

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        # If module build's name is one of base module names, build target
        # should not be deleted.
        with patch.object(conf, "base_module_names", new=[module_build.name]):

            hub = mock.MagicMock()
            poller = MBSProducer(hub)
            poller.delete_old_koji_targets(conf, db.session)

            koji_session.deleteBuildTarget.assert_not_called()

    @patch.dict("sys.modules", krbV=mock.MagicMock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_dont_delete_build_target_for_unfinished_module_builds(
        self, ClientSession, create_builder, global_consumer, dbg
    ):
        module_build = models.ModuleBuild.query.filter_by(id=3).one()

        koji_session = ClientSession.return_value
        # No created module build has any of these tags.
        koji_session.getBuildTargets.return_value = [{"dest_tag_name": module_build.koji_tag}]

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        # Each time when a module build is in one of these state, build target
        # should not be deleted.
        for state in ["init", "wait", "build"]:
            module_build.state = state
            db.session.commit()

            hub = mock.MagicMock()
            poller = MBSProducer(hub)
            poller.delete_old_koji_targets(conf, db.session)

            koji_session.deleteBuildTarget.assert_not_called()

    @patch.dict("sys.modules", krbV=mock.MagicMock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_only_delete_build_target_with_allowed_koji_tag_prefix(
        self, ClientSession, create_builder, global_consumer, dbg
    ):
        module_build_2 = models.ModuleBuild.query.filter_by(id=2).one()
        module_build_3 = models.ModuleBuild.query.filter_by(id=3).one()

        # Only module build 1's build target should be deleted.
        module_build_2.koji_tag = "module-tag1"
        module_build_2.state = models.BUILD_STATES["done"]
        # Ensure to exceed the koji_target_delete_time easily later for deletion
        module_build_2.time_completed = datetime.utcnow() - timedelta(hours=24)
        module_build_3.koji_tag = "f28"
        db.session.commit()
        db.session.refresh(module_build_2)
        db.session.refresh(module_build_3)

        koji_session = ClientSession.return_value
        # No created module build has any of these tags.
        koji_session.getBuildTargets.return_value = [
            {"id": 1, "dest_tag_name": module_build_2.koji_tag, "name": module_build_2.koji_tag},
            {"id": 2, "dest_tag_name": module_build_3.koji_tag, "name": module_build_3.koji_tag},
        ]

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        with patch.object(conf, "koji_tag_prefixes", new=["module", "another-prefix"]):
            with patch.object(conf, "koji_target_delete_time", new=60):
                hub = mock.MagicMock()
                poller = MBSProducer(hub)
                poller.delete_old_koji_targets(conf, db.session)

            koji_session.deleteBuildTarget.assert_called_once_with(1)
            koji_session.krb_login.assert_called_once()

    @patch.dict("sys.modules", krbV=mock.MagicMock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_cant_delete_build_target_if_not_reach_delete_time(
        self, ClientSession, create_builder, global_consumer, dbg
    ):
        module_build_2 = models.ModuleBuild.query.filter_by(id=2).one()

        # Only module build 1's build target should be deleted.
        module_build_2.koji_tag = "module-tag1"
        module_build_2.state = models.BUILD_STATES["done"]
        # Ensure to exceed the koji_target_delete_time easily later for deletion
        module_build_2.time_completed = datetime.utcnow() - timedelta(minutes=5)
        db.session.commit()
        db.session.refresh(module_build_2)

        koji_session = ClientSession.return_value
        # No created module build has any of these tags.
        koji_session.getBuildTargets.return_value = [
            {"id": 1, "dest_tag_name": module_build_2.koji_tag, "name": module_build_2.koji_tag}
        ]

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        with patch.object(conf, "koji_tag_prefixes", new=["module"]):
            # Use default koji_target_delete_time in config. That time is long
            # enough for test.
            hub = mock.MagicMock()
            poller = MBSProducer(hub)
            poller.delete_old_koji_targets(conf, db.session)

            koji_session.deleteBuildTarget.assert_not_called()

    @pytest.mark.parametrize("state", ["init", "wait"])
    def test_process_waiting_module_build(self, create_builder, global_consumer, dbg, state):
        """ Test that processing old waiting module builds works. """

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        hub = mock.MagicMock()
        poller = MBSProducer(hub)

        # Change the batch to 2, so the module build is in state where
        # it is not building anything, but the state is "build".
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.state = models.BUILD_STATES[state]
        original = datetime.utcnow() - timedelta(minutes=11)
        module_build.time_modified = original
        db.session.commit()
        db.session.refresh(module_build)

        # Ensure the queue is empty before we start.
        assert consumer.incoming.qsize() == 0

        # Poll :)
        poller.process_waiting_module_builds(db.session)

        assert consumer.incoming.qsize() == 1
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        # ensure the time_modified was changed.
        assert module_build.time_modified > original

    @pytest.mark.parametrize("state", ["init", "wait"])
    def test_process_waiting_module_build_not_old_enough(
        self, create_builder, global_consumer, dbg, state
    ):
        """ Test that we do not process young waiting builds. """

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        hub = mock.MagicMock()
        poller = MBSProducer(hub)

        # Change the batch to 2, so the module build is in state where
        # it is not building anything, but the state is "build".
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.state = models.BUILD_STATES[state]
        original = datetime.utcnow() - timedelta(minutes=9)
        module_build.time_modified = original
        db.session.commit()
        db.session.refresh(module_build)

        # Ensure the queue is empty before we start.
        assert consumer.incoming.qsize() == 0

        # Poll :)
        poller.process_waiting_module_builds(db.session)

        # Ensure we did *not* process the 9 minute-old build.
        assert consumer.incoming.qsize() == 0

    def test_process_waiting_module_build_none_found(self, create_builder, global_consumer, dbg):
        """ Test nothing happens when no module builds are waiting. """

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer

        hub = mock.MagicMock()
        poller = MBSProducer(hub)

        # Ensure the queue is empty before we start.
        assert consumer.incoming.qsize() == 0

        # Poll :)
        poller.process_waiting_module_builds(db.session)

        # Ensure we did *not* process any of the non-waiting builds.
        assert consumer.incoming.qsize() == 0

    def test_cleanup_stale_failed_builds(self, create_builder, global_consumer, dbg):
        """ Test that one of the two module builds gets to the garbage state when running
        cleanup_stale_failed_builds.
        """
        builder = mock.MagicMock()
        create_builder.return_value = builder
        module_build_one = models.ModuleBuild.query.get(2)
        module_build_two = models.ModuleBuild.query.get(3)
        module_build_one.state = models.BUILD_STATES["failed"]
        module_build_one.time_modified = datetime.utcnow() - timedelta(
            days=conf.cleanup_failed_builds_time + 1)
        module_build_two.time_modified = datetime.utcnow()
        module_build_two.state = models.BUILD_STATES["failed"]
        failed_component = models.ComponentBuild.query.filter_by(
            package="tangerine", module_id=3).one()
        failed_component.state = koji.BUILD_STATES["FAILED"]
        failed_component.tagged = False
        failed_component.tagged_in_final = False
        db.session.add(failed_component)
        db.session.add(module_build_one)
        db.session.add(module_build_two)
        db.session.commit()

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer
        hub = mock.MagicMock()
        poller = MBSProducer(hub)

        # Ensure the queue is empty before we start
        assert consumer.incoming.qsize() == 0
        poller.cleanup_stale_failed_builds(conf, db.session)
        db.session.refresh(module_build_two)
        # Make sure module_build_one was transitioned to garbage
        assert module_build_one.state == models.BUILD_STATES["garbage"]
        state_reason = (
            "The module was garbage collected since it has failed over {0} day(s) ago"
            .format(conf.cleanup_failed_builds_time)
        )
        assert module_build_one.state_reason == state_reason
        # Make sure all the components are marked as untagged in the database
        for component in module_build_one.component_builds:
            assert not component.tagged
            assert not component.tagged_in_final
        # Make sure module_build_two stayed the same
        assert module_build_two.state == models.BUILD_STATES["failed"]
        # Make sure the builds were untagged
        builder.untag_artifacts.assert_called_once_with([
            "perl-Tangerine-0.23-1.module+0+d027b723",
            "perl-List-Compare-0.53-5.module+0+d027b723",
            "tangerine-0.22-3.module+0+d027b723",
            "module-build-macros-0.1-1.module+0+d027b723",
        ])

    def test_cleanup_stale_failed_builds_no_components(self, create_builder, global_consumer, dbg):
        """ Test that a module build without any components built gets to the garbage state when
        running cleanup_stale_failed_builds.
        """
        module_build_one = models.ModuleBuild.query.get(1)
        module_build_two = models.ModuleBuild.query.get(2)
        module_build_one.state = models.BUILD_STATES["failed"]
        module_build_one.time_modified = datetime.utcnow()
        module_build_two.state = models.BUILD_STATES["failed"]
        module_build_two.time_modified = datetime.utcnow() - timedelta(
            days=conf.cleanup_failed_builds_time + 1)
        module_build_two.koji_tag = None
        module_build_two.cg_build_koji_tag = None
        for c in module_build_two.component_builds:
            c.state = None
            db.session.add(c)
        db.session.add(module_build_one)
        db.session.add(module_build_two)
        db.session.commit()

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer
        hub = mock.MagicMock()
        poller = MBSProducer(hub)

        # Ensure the queue is empty before we start
        assert consumer.incoming.qsize() == 0
        poller.cleanup_stale_failed_builds(conf, db.session)
        db.session.refresh(module_build_two)
        # Make sure module_build_two was transitioned to garbage
        assert module_build_two.state == models.BUILD_STATES["garbage"]
        state_reason = (
            "The module was garbage collected since it has failed over {0} day(s) ago"
            .format(conf.cleanup_failed_builds_time)
        )
        assert module_build_two.state_reason == state_reason
        # Make sure module_build_one stayed the same
        assert module_build_one.state == models.BUILD_STATES["failed"]
        # Make sure that the builder was never instantiated
        create_builder.assert_not_called()

    @pytest.mark.parametrize(
        "test_state", [models.BUILD_STATES[state] for state in conf.cleanup_stuck_builds_states]
    )
    def test_cancel_stuck_module_builds(self, create_builder, global_consumer, dbg, test_state):

        module_build1 = models.ModuleBuild.query.get(1)
        module_build1.state = test_state
        under_thresh = conf.cleanup_stuck_builds_time - 1
        module_build1.time_modified = datetime.utcnow() - timedelta(
            days=under_thresh, hours=23, minutes=59)

        module_build2 = models.ModuleBuild.query.get(2)
        module_build2.state = test_state
        module_build2.time_modified = datetime.utcnow() - timedelta(
            days=conf.cleanup_stuck_builds_time)

        module_build2 = models.ModuleBuild.query.get(3)
        module_build2.state = test_state
        module_build2.time_modified = datetime.utcnow()

        db.session.commit()

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer
        hub = mock.MagicMock()
        poller = MBSProducer(hub)

        assert consumer.incoming.qsize() == 0

        poller.cancel_stuck_module_builds(conf, db.session)

        module = models.ModuleBuild.query.filter_by(state=4).all()
        assert len(module) == 1
        assert module[0].id == 2

    @pytest.mark.parametrize("tagged", (True, False))
    @pytest.mark.parametrize("tagged_in_final", (True, False))
    @pytest.mark.parametrize("btime", (True, False))
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_sync_koji_build_tags(
        self, ClientSession, create_builder, global_consumer, dbg, tagged, tagged_in_final, btime
    ):
        module_build_2 = models.ModuleBuild.query.filter_by(id=2).one()

        # Only module build 1's build target should be deleted.
        module_build_2.koji_tag = "module-tag1"
        module_build_2.state = models.BUILD_STATES["build"]
        if btime:
            module_build_2.time_modified = datetime.utcnow() - timedelta(minutes=12)
        c = module_build_2.current_batch()[0]
        c.state = koji.BUILD_STATES["COMPLETE"]
        c.tagged_in_final = False
        c.tagged = False
        db.session.commit()
        db.session.refresh(module_build_2)

        koji_session = ClientSession.return_value
        # No created module build has any of these tags.
        ret = []

        if btime:
            if tagged:
                ret.append({"id": 1, "name": module_build_2.koji_tag + "-build"})
            if tagged_in_final:
                ret.append({"id": 2, "name": module_build_2.koji_tag})
        koji_session.listTags.return_value = ret

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer
        hub = mock.MagicMock()
        poller = MBSProducer(hub)

        assert consumer.incoming.qsize() == 0
        poller.sync_koji_build_tags(conf, db.session)
        assert consumer.incoming.qsize() == len(ret)

        expected_msg_tags = []
        if btime:
            if tagged:
                expected_msg_tags.append(module_build_2.koji_tag + "-build")
            if tagged_in_final:
                expected_msg_tags.append(module_build_2.koji_tag)

        assert len(expected_msg_tags) == consumer.incoming.qsize()

        for i in range(consumer.incoming.qsize()):
            msg = consumer.incoming.get()
            assert isinstance(msg, KojiTagChange)
            assert msg.artifact == c.package
            assert msg.nvr == c.nvr
            assert msg.tag in expected_msg_tags

    @pytest.mark.parametrize("greenwave_result", [True, False])
    @patch("module_build_service.utils.greenwave.Greenwave.check_gating")
    def test_poll_greenwave(self, mock_gw, create_builder, global_consumer, dbg, greenwave_result):

        module_build1 = models.ModuleBuild.query.get(1)
        module_build1.state = models.BUILD_STATES["ready"]

        module_build2 = models.ModuleBuild.query.get(2)
        module_build2.state = models.BUILD_STATES["done"]

        module_build2 = models.ModuleBuild.query.get(3)
        module_build2.state = models.BUILD_STATES["init"]

        db.session.commit()

        consumer = mock.MagicMock()
        consumer.incoming = queue.Queue()
        global_consumer.return_value = consumer
        hub = mock.MagicMock()
        poller = MBSProducer(hub)

        assert consumer.incoming.qsize() == 0

        mock_gw.return_value = greenwave_result

        poller.poll_greenwave(conf, db.session)

        mock_gw.assert_called_once()
        module = models.ModuleBuild.query.filter_by(state=models.BUILD_STATES["ready"]).all()

        if greenwave_result:
            assert len(module) == 2
            assert set([m.id for m in module]) == {1, 2}
        else:
            assert len(module) == 1
            assert set([m.id for m in module]) == {1}
