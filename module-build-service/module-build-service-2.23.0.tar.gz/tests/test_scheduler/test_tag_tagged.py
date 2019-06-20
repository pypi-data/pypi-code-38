# Copyright (c) 2016  Red Hat, Inc.
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

import mock

from mock import patch

import module_build_service.messaging
import module_build_service.scheduler.handlers.repos
import module_build_service.models
from tests import reuse_component_init_data
from tests import conf, db

import koji


class TestTagTagged:
    def setup_method(self, test_method):
        reuse_component_init_data()

    @mock.patch("module_build_service.models.ModuleBuild.from_tag_change_event")
    def test_no_matching_module(self, from_tag_change_event):
        """ Test that when a tag msg hits us and we have no match,
        that we do nothing gracefully.
        """
        from_tag_change_event.return_value = None
        msg = module_build_service.messaging.KojiTagChange(
            "no matches for this...", "2016-some-nonexistent-build", "artifact", "artifact-1.2-1")
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)

    def test_no_matching_artifact(self):
        """ Test that when a tag msg hits us and we have no match,
        that we do nothing gracefully.
        """
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "artifact",
            "artifact-1.2-1",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo(self, create_builder, koji_get_session, dbg):
        """
        Test that newRepo is called in the expected times.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.query.filter_by(id=3).one()

        # Set previous components as COMPLETE and tagged.
        module_build.batch = 1
        for c in module_build.up_to_current_batch():
            c.state = koji.BUILD_STATES["COMPLETE"]
            c.tagged = True
            c.tagged_in_final = True

        module_build.batch = 2
        for c in module_build.current_batch():
            if c.package == "perl-Tangerine":
                c.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"
            elif c.package == "perl-List-Compare":
                c.nvr = "perl-List-Compare-0.53-5.module+0+d027b723"
            c.state = koji.BUILD_STATES["COMPLETE"]
        db.session.commit()

        # Tag the first component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg
        )
        # Tag the first component to the final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg
        )

        # newRepo should not be called, because there are still components
        # to tag.
        assert not koji_session.newRepo.called

        # Tag the second component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg
        )

        # newRepo should not be called, because the component has not been
        # tagged to final tag so far.
        assert not koji_session.newRepo.called

        # Tag the first component to the final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)

        # newRepo should be called now - all components have been tagged.
        koji_session.newRepo.assert_called_once_with(
            "module-testmodule-master-20170219191323-c40c156c-build")

        # Refresh our module_build object.
        db.session.expunge(module_build)
        module_build = module_build_service.models.ModuleBuild.query.filter_by(id=3).one()

        # newRepo task_id should be stored in database, so we can check its
        # status later in poller.
        assert module_build.new_repo_task_id == 123456

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo_still_building_components(self, create_builder, koji_get_session, dbg):
        """
        Test that newRepo is called in the expected times.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 2
        component = module_build_service.models.ComponentBuild.query.filter_by(
            package="perl-Tangerine", module_id=module_build.id).one()
        component.state = koji.BUILD_STATES["BUILDING"]
        component.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"
        db.session.commit()

        # Tag the perl-List-Compare component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)
        # Tag the perl-List-Compare component to final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)

        # newRepo should not be called, because perl-List-Compare has not been
        # built yet.
        assert not koji_session.newRepo.called

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo_failed_components(self, create_builder, koji_get_session, dbg):
        """
        Test that newRepo is called in the expected times.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.query.filter_by(id=3).one()

        # Set previous components as COMPLETE and tagged.
        module_build.batch = 1
        for c in module_build.up_to_current_batch():
            c.state = koji.BUILD_STATES["COMPLETE"]
            c.tagged = True
            c.tagged_in_final = True

        module_build.batch = 2
        component = module_build_service.models.ComponentBuild.query.filter_by(
            package="perl-Tangerine", module_id=module_build.id).one()
        component.state = koji.BUILD_STATES["FAILED"]
        component.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"
        component = module_build_service.models.ComponentBuild.query.filter_by(
            package="perl-List-Compare", module_id=module_build.id).one()
        component.state = koji.BUILD_STATES["COMPLETE"]
        component.nvr = "perl-List-Compare-0.53-5.module+0+d027b723"
        db.session.commit()

        # Tag the perl-List-Compare component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg
        )
        # Tag the perl-List-Compare component to final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)

        # newRepo should be called now - all successfully built
        # components have been tagged.
        koji_session.newRepo.assert_called_once_with(
            "module-testmodule-master-20170219191323-c40c156c-build")

        # Refresh our module_build object.
        db.session.expunge(module_build)
        module_build = module_build_service.models.ModuleBuild.query.filter_by(id=3).one()

        # newRepo task_id should be stored in database, so we can check its
        # status later in poller.
        assert module_build.new_repo_task_id == 123456

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo_multiple_batches_tagged(self, create_builder, koji_get_session, dbg):
        """
        Test that newRepo is called just once and only when all components
        are tagged even if we tag components from the multiple batches in the
        same time.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 2
        mbm = module_build_service.models.ComponentBuild.query.filter_by(
            module_id=3, package="module-build-macros").one()
        mbm.tagged = False
        db.session.add(mbm)
        for c in module_build.current_batch():
            if c.package == "perl-Tangerine":
                c.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"
            elif c.package == "perl-List-Compare":
                c.nvr = "perl-List-Compare-0.53-5.module+0+d027b723"
            c.state = koji.BUILD_STATES["COMPLETE"]
        db.session.commit()

        # Tag the first component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)
        # Tag the first component to the final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)

        # newRepo should not be called, because there are still components
        # to tag.
        assert not koji_session.newRepo.called

        # Tag the second component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)
        # Tag the second component to final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)

        # newRepo should not be called, because there are still components
        # to tag.
        assert not koji_session.newRepo.called

        # Tag the component from first batch to final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "module-build-macros",
            "module-build-macros-0.1-1.module+0+b0a1d1f7",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)
        # Tag the component from first batch to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "module-build-macros",
            "module-build-macros-0.1-1.module+0+b0a1d1f7",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)

        # newRepo should be called now - all components have been tagged.
        koji_session.newRepo.assert_called_once_with(
            "module-testmodule-master-20170219191323-c40c156c-build")

        # Refresh our module_build object.
        db.session.expunge(module_build)
        module_build = module_build_service.models.ModuleBuild.query.filter_by(id=3).one()

        # newRepo task_id should be stored in database, so we can check its
        # status later in poller.
        assert module_build.new_repo_task_id == 123456

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo_build_time_only(self, create_builder, koji_get_session, dbg):
        """
        Test the component.build_time_only is respected in tag handler.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.query.filter_by(id=3).one()

        # Set previous components as COMPLETE and tagged.
        module_build.batch = 1
        for c in module_build.up_to_current_batch():
            if c.package == "module-build-macros":
                c.nvr = "module-build-macros-0.1-1.module+0+b0a1d1f7"
            c.state = koji.BUILD_STATES["COMPLETE"]
            c.tagged = True
            c.tagged_in_final = True

        module_build.batch = 2
        component = module_build_service.models.ComponentBuild.query.filter_by(
            package="perl-Tangerine", module_id=module_build.id).one()
        component.state = koji.BUILD_STATES["COMPLETE"]
        component.build_time_only = True
        component.tagged = False
        component.tagged_in_final = False
        component.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"
        component = module_build_service.models.ComponentBuild.query.filter_by(
            package="perl-List-Compare", module_id=module_build.id).one()
        component.state = koji.BUILD_STATES["COMPLETE"]
        component.nvr = "perl-List-Compare-0.53-5.module+0+d027b723"
        db.session.commit()

        # Tag the perl-Tangerine component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)
        assert not koji_session.newRepo.called
        # Tag the perl-List-Compare component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)
        # Tag the perl-List-Compare component to final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, session=db.session, msg=msg)

        # newRepo should be called now - all successfully built
        # components have been tagged.
        koji_session.newRepo.assert_called_once_with(
            "module-testmodule-master-20170219191323-c40c156c-build")

        # Refresh our module_build object.
        db.session.expunge(module_build)
        module_build = module_build_service.models.ModuleBuild.query.filter_by(id=3).one()

        # newRepo task_id should be stored in database, so we can check its
        # status later in poller.
        assert module_build.new_repo_task_id == 123456
