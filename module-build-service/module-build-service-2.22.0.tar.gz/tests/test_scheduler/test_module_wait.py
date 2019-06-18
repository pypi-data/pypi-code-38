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
# Written by Ralph Bean <rbean@redhat.com>

import mock
from mock import patch
import module_build_service.messaging
import module_build_service.scheduler.handlers.modules
import os
import koji
import pytest
from tests import conf, db, app, scheduler_init_data
import module_build_service.resolver
from module_build_service import build_logs, Modulemd
from module_build_service.utils.general import load_mmd_file
from module_build_service.models import ComponentBuild, ModuleBuild

base_dir = os.path.dirname(os.path.dirname(__file__))


class TestModuleWait:
    def setup_method(self, test_method):
        self.config = conf
        self.session = mock.Mock()
        self.fn = module_build_service.scheduler.handlers.modules.wait

    def teardown_method(self, test_method):
        try:
            path = build_logs.path(1)
            os.remove(path)
        except Exception:
            pass

    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    @patch("module_build_service.models.ModuleBuild.from_module_event")
    def test_init_basic(self, from_module_event, create_builder):
        builder = mock.Mock()
        builder.get_disttag_srpm.return_value = "some srpm disttag"
        builder.build.return_value = 1234, 1, "", None
        builder.module_build_tag = {"name": "some-tag-build"}
        create_builder.return_value = builder
        mocked_module_build = mock.Mock()
        mocked_module_build.name = "foo"
        mocked_module_build.stream = "stream"
        mocked_module_build.version = "1"
        mocked_module_build.context = "1234567"
        mocked_module_build.state = 1
        mocked_module_build.id = 1
        mocked_module_build.json.return_value = {
            "name": "foo",
            "stream": "1",
            "version": 1,
            "state": "some state",
            "id": 1,
        }

        formatted_testmodule_yml_path = os.path.join(
            base_dir, "staged_data", "formatted_testmodule.yaml")
        mmd = load_mmd_file(formatted_testmodule_yml_path)
        mocked_module_build.id = 1
        mocked_module_build.mmd.return_value = mmd
        mocked_module_build.component_builds = []

        from_module_event.return_value = mocked_module_build

        msg = module_build_service.messaging.MBSModule(
            msg_id=None, module_build_id=1, module_build_state="some state")
        with patch.object(module_build_service.resolver, "system_resolver"):
            self.fn(config=self.config, session=self.session, msg=msg)

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    @patch("module_build_service.resolver.DBResolver")
    @patch("module_build_service.resolver.GenericResolver")
    def test_new_repo_called_when_macros_reused(
        self, generic_resolver, resolver, create_builder, dbg
    ):
        """
        Test that newRepo is called when module-build-macros build is reused.
        """
        with app.app_context():
            scheduler_init_data()
            koji_session = mock.MagicMock()
            koji_session.newRepo.return_value = 123456

            builder = mock.MagicMock()
            builder.koji_session = koji_session
            builder.module_build_tag = {"name": "module-123-build"}
            builder.get_disttag_srpm.return_value = "some srpm disttag"
            builder.build.return_value = (
                1234,
                koji.BUILD_STATES["COMPLETE"],
                "",
                "module-build-macros-1-1",
            )
            create_builder.return_value = builder

            resolver = mock.MagicMock()
            resolver.backend = "db"
            resolver.get_module_tag.return_value = "module-testmodule-master-20170109091357"

            with patch.object(module_build_service.resolver, "system_resolver", new=resolver):
                msg = module_build_service.messaging.MBSModule(
                    msg_id=None, module_build_id=2, module_build_state="some state")
                module_build_service.scheduler.handlers.modules.wait(
                    config=conf, session=db.session, msg=msg)
                koji_session.newRepo.assert_called_once_with("module-123-build")

            # When module-build-macros is reused, it still has to appear only
            # once in database.
            builds_count = (
                db.session.query(ComponentBuild)
                .filter_by(package="module-build-macros", module_id=2)
                .count()
            )
            assert builds_count == 1

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    @patch("module_build_service.resolver.DBResolver")
    @patch("module_build_service.resolver.GenericResolver")
    def test_new_repo_not_called_when_macros_not_reused(
        self, generic_resolver, resolver, create_builder, dbg
    ):
        """
        Test that newRepo is called everytime for module-build-macros
        """
        with app.app_context():
            scheduler_init_data()
            koji_session = mock.MagicMock()
            koji_session.newRepo.return_value = 123456

            builder = mock.MagicMock()
            builder.koji_session = koji_session
            builder.module_build_tag = {"name": "module-123-build"}
            builder.get_disttag_srpm.return_value = "some srpm disttag"
            builder.build.return_value = (
                1234,
                koji.BUILD_STATES["BUILDING"],
                "",
                "module-build-macros-1-1",
            )
            create_builder.return_value = builder

            resolver = mock.MagicMock()
            resolver.backend = "db"
            resolver.get_module_tag.return_value = "module-testmodule-master-20170109091357"

            with patch.object(module_build_service.resolver, "system_resolver", new=resolver):
                msg = module_build_service.messaging.MBSModule(
                    msg_id=None, module_build_id=2, module_build_state="some state")
                module_build_service.scheduler.handlers.modules.wait(
                    config=conf, session=db.session, msg=msg)
                assert koji_session.newRepo.called

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    @patch("module_build_service.resolver.DBResolver")
    @patch("module_build_service.resolver.GenericResolver")
    def test_set_cg_build_koji_tag_fallback_to_default(
        self, generic_resolver, resolver, create_builder, dbg
    ):
        """
        Test that build.cg_build_koji_tag fallbacks to default tag.
        """
        with app.app_context():
            base_mmd = Modulemd.ModuleStreamV2.new("base-runtime", "f27")

            scheduler_init_data()
            koji_session = mock.MagicMock()
            koji_session.newRepo.return_value = 123456

            builder = mock.MagicMock()
            builder.koji_session = koji_session
            builder.module_build_tag = {"name": "module-123-build"}
            builder.get_disttag_srpm.return_value = "some srpm disttag"
            builder.build.return_value = (
                1234,
                koji.BUILD_STATES["BUILDING"],
                "",
                "module-build-macros-1-1",
            )
            create_builder.return_value = builder

            resolver = mock.MagicMock()
            resolver.backend = "db"
            resolver.get_module_tag.return_value = "module-testmodule-master-20170109091357"
            resolver.get_module_build_dependencies.return_value = {
                "module-bootstrap-tag": [base_mmd]
            }

            with patch.object(module_build_service.resolver, "system_resolver", new=resolver):
                msg = module_build_service.messaging.MBSModule(
                    msg_id=None, module_build_id=2, module_build_state="some state")
                module_build_service.scheduler.handlers.modules.wait(
                    config=conf, session=db.session, msg=msg)
                module_build = ModuleBuild.query.filter_by(id=2).one()
                assert module_build.cg_build_koji_tag == "modular-updates-candidate"

    @pytest.mark.parametrize(
        "koji_cg_tag_build,expected_cg_koji_build_tag",
        [
            [True, "f27-modular-updates-candidate"],
            [False, None]
        ],
    )
    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    @patch("module_build_service.resolver.DBResolver")
    @patch("module_build_service.resolver.GenericResolver")
    @patch(
        "module_build_service.config.Config.base_module_names",
        new_callable=mock.PropertyMock,
        return_value=["base-runtime", "platform"],
    )
    def test_set_cg_build_koji_tag(
        self,
        cfg,
        generic_resolver,
        resolver,
        create_builder,
        dbg,
        koji_cg_tag_build,
        expected_cg_koji_build_tag,
    ):
        """
        Test that build.cg_build_koji_tag is set.
        """
        with app.app_context():
            base_mmd = Modulemd.ModuleStreamV2.new("base-runtime", "f27")

            scheduler_init_data()
            koji_session = mock.MagicMock()
            koji_session.newRepo.return_value = 123456

            builder = mock.MagicMock()
            builder.koji_session = koji_session
            builder.module_build_tag = {"name": "module-123-build"}
            builder.get_disttag_srpm.return_value = "some srpm disttag"
            builder.build.return_value = (
                1234,
                koji.BUILD_STATES["BUILDING"],
                "",
                "module-build-macros-1-1",
            )
            create_builder.return_value = builder

            resolver = mock.MagicMock()
            resolver.backend = "db"
            resolver.get_module_tag.return_value = "module-testmodule-master-20170109091357"
            resolver.get_module_build_dependencies.return_value = {
                "module-bootstrap-tag": [base_mmd]
            }

            with patch.object(
                module_build_service.scheduler.handlers.modules.conf,
                "koji_cg_tag_build",
                new=koji_cg_tag_build,
            ):
                with patch.object(module_build_service.resolver, "system_resolver", new=resolver):
                    msg = module_build_service.messaging.MBSModule(
                        msg_id=None, module_build_id=2, module_build_state="some state"
                    )
                    module_build_service.scheduler.handlers.modules.wait(
                        config=conf, session=db.session, msg=msg
                    )
                    module_build = ModuleBuild.query.filter_by(id=2).one()
                    assert module_build.cg_build_koji_tag == expected_cg_koji_build_tag
