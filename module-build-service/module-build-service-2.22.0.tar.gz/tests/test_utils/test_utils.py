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

import io
import tempfile
import hashlib
from os import path, mkdir
from shutil import copyfile, rmtree
from datetime import datetime
from werkzeug.datastructures import FileStorage
from mock import patch
from module_build_service.utils.general import load_mmd_file, mmd_to_str
import module_build_service.utils
import module_build_service.scm
from module_build_service import models, conf
from module_build_service.errors import ProgrammingError, ValidationError, UnprocessableEntity
from tests import (
    reuse_component_init_data,
    db,
    reuse_shared_userspace_init_data,
    clean_database,
    init_data,
    scheduler_init_data,
    make_module,
)
import mock
import koji
import pytest
import module_build_service.scheduler.handlers.components
from module_build_service.builder.base import GenericBuilder
from module_build_service.builder.KojiModuleBuilder import KojiModuleBuilder
from module_build_service import Modulemd
from tests import app

BASE_DIR = path.abspath(path.dirname(__file__))


class FakeSCM(object):
    def __init__(self, mocked_scm, name, mmd_filename, commit=None):
        self.mocked_scm = mocked_scm
        self.name = name
        self.commit = commit
        self.mmd_filename = mmd_filename
        self.sourcedir = None

        self.mocked_scm.return_value.checkout = self.checkout
        self.mocked_scm.return_value.name = self.name
        self.mocked_scm.return_value.branch = "master"
        self.mocked_scm.return_value.get_latest = self.get_latest
        self.mocked_scm.return_value.commit = self.commit
        self.mocked_scm.return_value.repository_root = "https://src.stg.fedoraproject.org/modules/"
        self.mocked_scm.return_value.sourcedir = self.sourcedir
        self.mocked_scm.return_value.get_module_yaml = self.get_module_yaml
        self.mocked_scm.return_value.is_full_commit_hash.return_value = commit and len(commit) == 40
        self.mocked_scm.return_value.get_full_commit_hash.return_value = self.get_full_commit_hash

    def checkout(self, temp_dir):
        self.sourcedir = path.join(temp_dir, self.name)
        mkdir(self.sourcedir)
        base_dir = path.abspath(path.dirname(__file__))
        copyfile(
            path.join(base_dir, "..", "staged_data", self.mmd_filename), self.get_module_yaml())

        return self.sourcedir

    def get_latest(self, ref="master"):
        return self.commit if self.commit else ref

    def get_module_yaml(self):
        return path.join(self.sourcedir, self.name + ".yaml")

    def get_full_commit_hash(self, commit_hash=None):
        if not commit_hash:
            commit_hash = self.commit
        sha1_hash = hashlib.sha1("random").hexdigest()
        return commit_hash + sha1_hash[len(commit_hash):]


class TestUtilsComponentReuse:
    def setup_method(self, test_method):
        reuse_component_init_data()

    def teardown_method(self, test_method):
        clean_database()

    @pytest.mark.parametrize(
        "changed_component", ["perl-List-Compare", "perl-Tangerine", "tangerine", None]
    )
    def test_get_reusable_component_different_component(self, changed_component):
        second_module_build = models.ModuleBuild.query.filter_by(id=3).one()
        if changed_component:
            mmd = second_module_build.mmd()
            mmd.get_rpm_component("tangerine").set_ref("00ea1da4192a2030f9ae023de3b3143ed647bbab")
            second_module_build.modulemd = mmd_to_str(mmd)
            second_module_changed_component = models.ComponentBuild.query.filter_by(
                package=changed_component, module_id=3).one()
            second_module_changed_component.ref = "00ea1da4192a2030f9ae023de3b3143ed647bbab"
            db.session.add(second_module_changed_component)
            db.session.commit()

        plc_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "perl-List-Compare")
        pt_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "perl-Tangerine")
        tangerine_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "tangerine")

        if changed_component == "perl-List-Compare":
            # perl-Tangerine can be reused even though a component in its batch has changed
            assert plc_rv is None
            assert pt_rv.package == "perl-Tangerine"
            assert tangerine_rv is None
        elif changed_component == "perl-Tangerine":
            # perl-List-Compare can be reused even though a component in its batch has changed
            assert plc_rv.package == "perl-List-Compare"
            assert pt_rv is None
            assert tangerine_rv is None
        elif changed_component == "tangerine":
            # perl-List-Compare and perl-Tangerine can be reused since they are in an earlier
            # buildorder than tangerine
            assert plc_rv.package == "perl-List-Compare"
            assert pt_rv.package == "perl-Tangerine"
            assert tangerine_rv is None
        elif changed_component is None:
            # Nothing has changed so everthing can be used
            assert plc_rv.package == "perl-List-Compare"
            assert pt_rv.package == "perl-Tangerine"
            assert tangerine_rv.package == "tangerine"

    def test_get_reusable_component_different_rpm_macros(self):
        second_module_build = models.ModuleBuild.query.filter_by(id=3).one()
        mmd = second_module_build.mmd()
        buildopts = Modulemd.Buildopts()
        buildopts.set_rpm_macros("%my_macro 1")
        mmd.set_buildopts(buildopts)
        second_module_build.modulemd = mmd_to_str(mmd)
        db.session.commit()

        plc_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "perl-List-Compare")
        assert plc_rv is None

        pt_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "perl-Tangerine")
        assert pt_rv is None

    @pytest.mark.parametrize("set_current_arch", [True, False])
    @pytest.mark.parametrize("set_database_arch", [True, False])
    def test_get_reusable_component_different_arches(self, set_database_arch, set_current_arch):
        second_module_build = models.ModuleBuild.query.filter_by(id=3).one()
        if set_current_arch:  # set architecture for current build
            mmd = second_module_build.mmd()
            component = mmd.get_rpm_component("tangerine")
            component.reset_arches()
            component.add_restricted_arch("i686")
            second_module_build.modulemd = mmd_to_str(mmd)
        if set_database_arch:  # set architecture for build in database
            second_module_changed_component = models.ComponentBuild.query.filter_by(
                package="tangerine", module_id=2).one()
            mmd = second_module_changed_component.module_build.mmd()
            component = mmd.get_rpm_component("tangerine")
            component.reset_arches()
            component.add_restricted_arch("i686")
            second_module_changed_component.module_build.modulemd = mmd_to_str(mmd)
            db.session.add(second_module_changed_component)
            db.session.commit()

        tangerine = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "tangerine")
        assert bool(tangerine is None) != bool(set_current_arch == set_database_arch)

    @pytest.mark.parametrize("rebuild_strategy", models.ModuleBuild.rebuild_strategies.keys())
    def test_get_reusable_component_different_buildrequires_hash(self, rebuild_strategy):
        first_module_build = models.ModuleBuild.query.filter_by(id=2).one()
        first_module_build.rebuild_strategy = rebuild_strategy
        second_module_build = models.ModuleBuild.query.filter_by(id=3).one()
        mmd = second_module_build.mmd()
        xmd = mmd.get_xmd()
        xmd["mbs"]["buildrequires"]["platform"]["ref"] = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        mmd.set_xmd(xmd)
        second_module_build.modulemd = mmd_to_str(mmd)
        second_module_build.ref_build_context = "37c6c57bedf4305ef41249c1794760b5cb8fad17"
        second_module_build.rebuild_strategy = rebuild_strategy
        db.session.commit()

        plc_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "perl-List-Compare")
        pt_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "perl-Tangerine")
        tangerine_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "tangerine")

        if rebuild_strategy == "only-changed":
            assert plc_rv is not None
            assert pt_rv is not None
            assert tangerine_rv is not None
        else:
            assert plc_rv is None
            assert pt_rv is None
            assert tangerine_rv is None

    @pytest.mark.parametrize("rebuild_strategy", models.ModuleBuild.rebuild_strategies.keys())
    def test_get_reusable_component_different_buildrequires_stream(self, rebuild_strategy):
        first_module_build = models.ModuleBuild.query.filter_by(id=2).one()
        first_module_build.rebuild_strategy = rebuild_strategy
        second_module_build = models.ModuleBuild.query.filter_by(id=3).one()
        mmd = second_module_build.mmd()
        xmd = mmd.get_xmd()
        xmd["mbs"]["buildrequires"]["platform"]["stream"] = "different"
        mmd.set_xmd(xmd)
        second_module_build.modulemd = mmd_to_str(mmd)
        second_module_build.build_context = "37c6c57bedf4305ef41249c1794760b5cb8fad17"
        second_module_build.rebuild_strategy = rebuild_strategy
        db.session.commit()

        plc_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "perl-List-Compare")
        pt_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "perl-Tangerine")
        tangerine_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "tangerine")

        assert plc_rv is None
        assert pt_rv is None
        assert tangerine_rv is None

    def test_get_reusable_component_different_buildrequires(self):
        second_module_build = models.ModuleBuild.query.filter_by(id=3).one()
        mmd = second_module_build.mmd()
        mmd.get_dependencies()[0].add_buildtime_stream("some_module", "master")
        xmd = mmd.get_xmd()
        xmd["mbs"]["buildrequires"] = {
            "some_module": {
                "ref": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
                "stream": "master",
                "version": "20170123140147",
            }
        }
        mmd.set_xmd(xmd)
        second_module_build.modulemd = mmd_to_str(mmd)
        second_module_build.ref_build_context = "37c6c57bedf4305ef41249c1794760b5cb8fad17"
        db.session.commit()

        plc_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "perl-List-Compare")
        assert plc_rv is None

        pt_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "perl-Tangerine")
        assert pt_rv is None

        tangerine_rv = module_build_service.utils.get_reusable_component(
            db.session, second_module_build, "tangerine")
        assert tangerine_rv is None

    @patch("module_build_service.utils.submit.submit_module_build")
    def test_submit_module_build_from_yaml_with_skiptests(self, mock_submit):
        """
        Tests local module build from a yaml file with the skiptests option

        Args:
            mock_submit (MagickMock): mocked function submit_module_build, which we then
                inspect if it was called with correct arguments
        """
        module_dir = tempfile.mkdtemp()
        module = models.ModuleBuild.query.filter_by(id=3).one()
        mmd = module.mmd()
        modulemd_yaml = mmd_to_str(mmd)
        modulemd_file_path = path.join(module_dir, "testmodule.yaml")

        username = "test"
        stream = "dev"

        with io.open(modulemd_file_path, "w", encoding="utf-8") as fd:
            fd.write(modulemd_yaml)

        with open(modulemd_file_path, "rb") as fd:
            handle = FileStorage(fd)
            module_build_service.utils.submit_module_build_from_yaml(
                username, handle, {}, stream=stream, skiptests=True)
            mock_submit_args = mock_submit.call_args[0]
            username_arg = mock_submit_args[0]
            mmd_arg = mock_submit_args[1]
            assert mmd_arg.get_stream_name() == stream
            assert "\n\n%__spec_check_pre exit 0\n" in mmd_arg.get_buildopts().get_rpm_macros()
            assert username_arg == username
        rmtree(module_dir)


class TestUtils:
    def setup_method(self, test_method):
        clean_database()

    def teardown_method(self, test_method):
        clean_database()

    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_get_build_arches(self, ClientSession):
        session = ClientSession.return_value
        session.getTag.return_value = {"arches": "ppc64le"}
        mmd = load_mmd_file(path.join(BASE_DIR, "..", "staged_data", "formatted_testmodule.yaml"))
        r = module_build_service.utils.get_build_arches(mmd, conf)
        assert r == ["ppc64le"]

    @patch(
        "module_build_service.config.Config.allowed_privileged_module_names",
        new_callable=mock.PropertyMock,
        return_value=["testmodule"],
    )
    def test_get_build_arches_koji_tag_arches(self, cfg):
        mmd = load_mmd_file(path.join(BASE_DIR, "..", "staged_data", "formatted_testmodule.yaml"))
        xmd = mmd.get_xmd()
        xmd["mbs"]["koji_tag_arches"] = ["ppc64", "ppc64le"]
        mmd.set_xmd(xmd)

        r = module_build_service.utils.get_build_arches(mmd, conf)
        assert r == ["ppc64", "ppc64le"]

    @patch.object(conf, "base_module_arches", new={"platform:xx": ["x86_64", "i686"]})
    def test_get_build_arches_base_module_override(self):
        mmd = load_mmd_file(path.join(BASE_DIR, "..", "staged_data", "formatted_testmodule.yaml"))
        xmd = mmd.get_xmd()
        mbs_options = xmd["mbs"] if "mbs" in xmd.keys() else {}
        mbs_options["buildrequires"] = {"platform": {"stream": "xx"}}
        xmd["mbs"] = mbs_options
        mmd.set_xmd(xmd)

        r = module_build_service.utils.get_build_arches(mmd, conf)
        assert r == ["x86_64", "i686"]

    @pytest.mark.parametrize("context", ["c1", None])
    def test_import_mmd_contexts(self, context):
        mmd = load_mmd_file(path.join(BASE_DIR, "..", "staged_data", "formatted_testmodule.yaml"))
        mmd.set_context(context)

        xmd = mmd.get_xmd()
        xmd["mbs"]["koji_tag"] = "foo"
        mmd.set_xmd(xmd)

        build, msgs = module_build_service.utils.import_mmd(db.session, mmd)

        mmd_context = build.mmd().get_context()
        if context:
            assert mmd_context == context
            assert build.context == context
        else:
            assert mmd_context == models.DEFAULT_MODULE_CONTEXT
            assert build.context == models.DEFAULT_MODULE_CONTEXT

    def test_import_mmd_multiple_dependencies(self):
        mmd = load_mmd_file(path.join(BASE_DIR, "..", "staged_data", "formatted_testmodule.yaml"))
        mmd.add_dependencies(mmd.get_dependencies()[0].copy())

        expected_error = "The imported module's dependencies list should contain just one element"
        with pytest.raises(UnprocessableEntity) as e:
            module_build_service.utils.import_mmd(db.session, mmd)
            assert str(e.value) == expected_error

    def test_import_mmd_no_xmd_buildrequires(self):
        mmd = load_mmd_file(path.join(BASE_DIR, "..", "staged_data", "formatted_testmodule.yaml"))
        xmd = mmd.get_xmd()
        del xmd["mbs"]["buildrequires"]
        mmd.set_xmd(xmd)

        expected_error = (
            "The imported module buildrequires other modules, but the metadata in the "
            'xmd["mbs"]["buildrequires"] dictionary is missing entries'
        )
        with pytest.raises(UnprocessableEntity) as e:
            module_build_service.utils.import_mmd(db.session, mmd)
            assert str(e.value) == expected_error

    def test_import_mmd_minimal_xmd_from_local_repository(self):
        mmd = load_mmd_file(path.join(BASE_DIR, "..", "staged_data", "formatted_testmodule.yaml"))
        xmd = mmd.get_xmd()
        xmd["mbs"] = {}
        xmd["mbs"]["koji_tag"] = "repofile:///etc/yum.repos.d/fedora-modular.repo"
        xmd["mbs"]["mse"] = True
        xmd["mbs"]["commit"] = "unknown"
        mmd.set_xmd(xmd)

        build, msgs = module_build_service.utils.import_mmd(db.session, mmd, False)
        assert build.name == mmd.get_module_name()

    @pytest.mark.parametrize(
        "stream, disttag_marking, error_msg",
        (
            ("f28", None, None),
            ("f28", "fedora28", None),
            ("f-28", "f28", None),
            ("f-28", None, "The stream cannot contain a dash unless disttag_marking is set"),
            ("f28", "f-28", "The disttag_marking cannot contain a dash"),
            ("f-28", "fedora-28", "The disttag_marking cannot contain a dash"),
        ),
    )
    def test_import_mmd_base_module(self, stream, disttag_marking, error_msg):
        clean_database(add_platform_module=False)
        mmd = load_mmd_file(path.join(BASE_DIR, "..", "staged_data", "platform.yaml"))
        mmd = mmd.copy(mmd.get_module_name(), stream)

        if disttag_marking:
            xmd = mmd.get_xmd()
            xmd["mbs"]["disttag_marking"] = disttag_marking
            mmd.set_xmd(xmd)

        if error_msg:
            with pytest.raises(UnprocessableEntity, match=error_msg):
                module_build_service.utils.import_mmd(db.session, mmd)
        else:
            module_build_service.utils.import_mmd(db.session, mmd)

    def test_get_rpm_release_mse(self):
        init_data(contexts=True)
        build_one = models.ModuleBuild.query.get(2)
        build_two = models.ModuleBuild.query.get(3)
        release_one = module_build_service.utils.get_rpm_release(build_one)
        release_two = module_build_service.utils.get_rpm_release(build_two)
        assert release_one == "module+2+b8645bbb"
        assert release_two == "module+2+17e35784"

    def test_get_rpm_release_platform_stream(self):
        scheduler_init_data(1)
        build_one = models.ModuleBuild.query.get(2)
        release = module_build_service.utils.get_rpm_release(build_one)
        assert release == "module+f28+2+814cfa39"

    def test_get_rpm_release_platform_stream_override(self):
        scheduler_init_data(1)

        # Set the disttag_marking override on the platform
        platform = models.ModuleBuild.query.filter_by(name="platform", stream="f28").first()
        platform_mmd = platform.mmd()
        platform_xmd = platform_mmd.get_xmd()
        platform_xmd["mbs"]["disttag_marking"] = "fedora28"
        platform_mmd.set_xmd(platform_xmd)
        platform.modulemd = mmd_to_str(platform_mmd)
        db.session.add(platform)
        db.session.commit()

        build_one = models.ModuleBuild.query.get(2)
        release = module_build_service.utils.get_rpm_release(build_one)
        assert release == "module+fedora28+2+814cfa39"

    @patch(
        "module_build_service.config.Config.allowed_privileged_module_names",
        new_callable=mock.PropertyMock,
        return_value=["build"],
    )
    def test_get_rpm_release_metadata_br_stream_override(self, mock_admmn):
        """
        Test that when a module buildrequires a module in conf.allowed_privileged_module_names,
        and that module has the xmd.mbs.disttag_marking field set, it should influence the disttag.
        """
        scheduler_init_data(1)
        mmd_path = path.abspath(
            path.join(
                __file__, path.pardir, path.pardir, "staged_data", "build_metadata_module.yaml")
        )
        metadata_mmd = module_build_service.utils.load_mmd_file(mmd_path)
        module_build_service.utils.import_mmd(db.session, metadata_mmd)

        build_one = models.ModuleBuild.query.get(2)
        mmd = build_one.mmd()
        deps = mmd.get_dependencies()[0]
        deps.add_buildtime_stream("build", "product1.2")
        xmd = mmd.get_xmd()
        xmd["mbs"]["buildrequires"]["build"] = {
            "filtered_rpms": [],
            "ref": "virtual",
            "stream": "product1.2",
            "version": "1",
            "context": "00000000",
        }
        mmd.set_xmd(xmd)
        build_one.modulemd = mmd_to_str(mmd)
        db.session.add(build_one)
        db.session.commit()

        release = module_build_service.utils.get_rpm_release(build_one)
        assert release == "module+product12+2+814cfa39"

    def test_get_rpm_release_mse_scratch(self):
        init_data(contexts=True, scratch=True)
        build_one = models.ModuleBuild.query.get(2)
        build_two = models.ModuleBuild.query.get(3)
        release_one = module_build_service.utils.get_rpm_release(build_one)
        release_two = module_build_service.utils.get_rpm_release(build_two)
        assert release_one == "scrmod+2+b8645bbb"
        assert release_two == "scrmod+2+17e35784"

    def test_get_rpm_release_platform_stream_scratch(self):
        scheduler_init_data(1, scratch=True)
        build_one = models.ModuleBuild.query.get(2)
        release = module_build_service.utils.get_rpm_release(build_one)
        assert release == "scrmod+f28+2+814cfa39"

    @patch("module_build_service.utils.submit.get_build_arches")
    def test_record_module_build_arches(self, get_build_arches):
        get_build_arches.return_value = ["x86_64", "i686"]
        scheduler_init_data(1)
        build = models.ModuleBuild.query.get(2)
        build.arches = []
        module_build_service.utils.record_module_build_arches(build.mmd(), build, db.session)

        arches = set([arch.name for arch in build.arches])
        assert arches == set(get_build_arches.return_value)

    @pytest.mark.parametrize(
        "scmurl",
        [
            (
                "https://src.stg.fedoraproject.org/modules/testmodule.git"
                "?#620ec77321b2ea7b0d67d82992dda3e1d67055b4"
            ),
            None,
        ],
    )
    @patch("module_build_service.scm.SCM")
    def test_format_mmd(self, mocked_scm, scmurl):
        mocked_scm.return_value.commit = "620ec77321b2ea7b0d67d82992dda3e1d67055b4"
        # For all the RPMs in testmodule, get_latest is called
        mocked_scm.return_value.get_latest.side_effect = [
            "4ceea43add2366d8b8c5a622a2fb563b625b9abf",
            "fbed359411a1baa08d4a88e0d12d426fbf8f602c",
        ]
        hashes_returned = {
            "master": "fbed359411a1baa08d4a88e0d12d426fbf8f602c",
            "f28": "4ceea43add2366d8b8c5a622a2fb563b625b9abf",
            "f27": "5deef23acd2367d8b8d5a621a2fc568b695bc3bd",
        }

        def mocked_get_latest(ref="master"):
            return hashes_returned[ref]

        mocked_scm.return_value.get_latest = mocked_get_latest
        mmd = load_mmd_file(path.join(BASE_DIR, "..", "staged_data", "testmodule.yaml"))
        # Modify the component branches so we can identify them later on
        mmd.get_rpm_component("perl-Tangerine").set_ref("f28")
        mmd.get_rpm_component("tangerine").set_ref("f27")
        module_build_service.utils.format_mmd(mmd, scmurl)

        # Make sure that original refs are not changed.
        mmd_pkg_refs = [
            mmd.get_rpm_component(pkg_name).get_ref()
            for pkg_name in mmd.get_rpm_component_names()
        ]
        assert set(mmd_pkg_refs) == set(hashes_returned.keys())
        deps = mmd.get_dependencies()[0]
        assert deps.get_buildtime_modules() == ["platform"]
        assert deps.get_buildtime_streams("platform") == ["f28"]
        xmd = {
            "mbs": {
                "commit": "",
                "rpms": {
                    "perl-List-Compare": {"ref": "fbed359411a1baa08d4a88e0d12d426fbf8f602c"},
                    "perl-Tangerine": {"ref": "4ceea43add2366d8b8c5a622a2fb563b625b9abf"},
                    "tangerine": {"ref": "5deef23acd2367d8b8d5a621a2fc568b695bc3bd"},
                },
                "scmurl": "",
            }
        }
        if scmurl:
            xmd["mbs"]["commit"] = "620ec77321b2ea7b0d67d82992dda3e1d67055b4"
            xmd["mbs"]["scmurl"] = scmurl
        mmd_xmd = mmd.get_xmd()
        assert mmd_xmd == xmd

    def test_get_reusable_component_shared_userspace_ordering(self):
        """
        For modules with lot of components per batch, there is big chance that
        the database will return them in different order than what we have for
        current `new_module`. In this case, reuse code should still be able to
        reuse the components.
        """
        reuse_shared_userspace_init_data()
        new_module = models.ModuleBuild.query.get(3)
        rv = module_build_service.utils.get_reusable_component(db.session, new_module, "llvm")
        assert rv.package == "llvm"

    def test_validate_koji_tag_wrong_tag_arg_during_programming(self):
        """ Test that we fail on a wrong param name (non-existing one) due to
        programming error. """

        @module_build_service.utils.validate_koji_tag("wrong_tag_arg")
        def validate_koji_tag_programming_error(good_tag_arg, other_arg):
            pass

        with pytest.raises(ProgrammingError):
            validate_koji_tag_programming_error("dummy", "other_val")

    def test_validate_koji_tag_bad_tag_value(self):
        """ Test that we fail on a bad tag value. """

        @module_build_service.utils.validate_koji_tag("tag_arg")
        def validate_koji_tag_bad_tag_value(tag_arg):
            pass

        with pytest.raises(ValidationError):
            validate_koji_tag_bad_tag_value("forbiddentagprefix-foo")

    def test_validate_koji_tag_bad_tag_value_in_list(self):
        """ Test that we fail on a list containing bad tag value. """

        @module_build_service.utils.validate_koji_tag("tag_arg")
        def validate_koji_tag_bad_tag_value_in_list(tag_arg):
            pass

        with pytest.raises(ValidationError):
            validate_koji_tag_bad_tag_value_in_list(["module-foo", "forbiddentagprefix-bar"])

    def test_validate_koji_tag_good_tag_value(self):
        """ Test that we pass on a good tag value. """

        @module_build_service.utils.validate_koji_tag("tag_arg")
        def validate_koji_tag_good_tag_value(tag_arg):
            return True

        assert validate_koji_tag_good_tag_value("module-foo") is True

    def test_validate_koji_tag_good_tag_values_in_list(self):
        """ Test that we pass on a list of good tag values. """

        @module_build_service.utils.validate_koji_tag("tag_arg")
        def validate_koji_tag_good_tag_values_in_list(tag_arg):
            return True

        assert validate_koji_tag_good_tag_values_in_list(["module-foo", "module-bar"]) is True

    def test_validate_koji_tag_good_tag_value_in_dict(self):
        """ Test that we pass on a dict arg with default key
        and a good value. """

        @module_build_service.utils.validate_koji_tag("tag_arg")
        def validate_koji_tag_good_tag_value_in_dict(tag_arg):
            return True

        assert validate_koji_tag_good_tag_value_in_dict({"name": "module-foo"}) is True

    def test_validate_koji_tag_good_tag_value_in_dict_nondefault_key(self):
        """ Test that we pass on a dict arg with non-default key
        and a good value. """

        @module_build_service.utils.validate_koji_tag("tag_arg", dict_key="nondefault")
        def validate_koji_tag_good_tag_value_in_dict_nondefault_key(tag_arg):
            return True

        assert (
            validate_koji_tag_good_tag_value_in_dict_nondefault_key({"nondefault": "module-foo"})
            is True
        )

    def test_validate_koji_tag_double_trouble_good(self):
        """ Test that we pass on a list of tags that are good. """

        expected = "foo"

        @module_build_service.utils.validate_koji_tag(["tag_arg1", "tag_arg2"])
        def validate_koji_tag_double_trouble(tag_arg1, tag_arg2):
            return expected

        actual = validate_koji_tag_double_trouble("module-1", "module-2")
        assert actual == expected

    def test_validate_koji_tag_double_trouble_bad(self):
        """ Test that we fail on a list of tags that are bad. """

        @module_build_service.utils.validate_koji_tag(["tag_arg1", "tag_arg2"])
        def validate_koji_tag_double_trouble(tag_arg1, tag_arg2):
            pass

        with pytest.raises(ValidationError):
            validate_koji_tag_double_trouble("module-1", "BADNEWS-2")

    def test_validate_koji_tag_is_None(self):
        """ Test that we fail on a tag which is None. """

        @module_build_service.utils.validate_koji_tag("tag_arg")
        def validate_koji_tag_is_None(tag_arg):
            pass

        with pytest.raises(ValidationError) as cm:
            validate_koji_tag_is_None(None)
            assert str(cm.value).endswith(" No value provided.") is True

    @patch("module_build_service.scm.SCM")
    def test_record_component_builds_duplicate_components(self, mocked_scm):
        with app.app_context():
            clean_database()
            mocked_scm.return_value.commit = "620ec77321b2ea7b0d67d82992dda3e1d67055b4"
            mocked_scm.return_value.get_latest.side_effect = [
                "4ceea43add2366d8b8c5a622a2fb563b625b9abf",
                "fbed359411a1baa08d4a88e0d12d426fbf8f602c",
            ]

            testmodule_mmd_path = path.join(BASE_DIR, "..", "staged_data", "testmodule.yaml")
            mmd = load_mmd_file(testmodule_mmd_path)
            mmd = mmd.copy("testmodule-variant", "master")
            module_build = module_build_service.models.ModuleBuild()
            module_build.name = "testmodule-variant"
            module_build.stream = "master"
            module_build.version = 20170109091357
            module_build.state = models.BUILD_STATES["init"]
            module_build.scmurl = \
                "https://src.stg.fedoraproject.org/modules/testmodule.git?#ff1ea79"
            module_build.batch = 1
            module_build.owner = "Tom Brady"
            module_build.time_submitted = datetime(2017, 2, 15, 16, 8, 18)
            module_build.time_modified = datetime(2017, 2, 15, 16, 19, 35)
            module_build.rebuild_strategy = "changed-and-after"
            module_build.modulemd = mmd_to_str(mmd)
            db.session.add(module_build)
            db.session.commit()
            # Rename the the modulemd to include
            mmd = mmd.copy("testmodule")
            # Remove perl-Tangerine and tangerine from the modulemd to include so only one
            # component conflicts
            mmd.remove_rpm_component("perl-Tangerine")
            mmd.remove_rpm_component("tangerine")

            error_msg = (
                'The included module "testmodule" in "testmodule-variant" have '
                "the following conflicting components: perl-List-Compare"
            )
            with pytest.raises(UnprocessableEntity) as e:
                module_build_service.utils.record_component_builds(
                    mmd, module_build, main_mmd=module_build.mmd())

            assert str(e.value) == error_msg

    @patch("module_build_service.scm.SCM")
    def test_record_component_builds_set_weight(self, mocked_scm):
        with app.app_context():
            clean_database()
            mocked_scm.return_value.commit = "620ec77321b2ea7b0d67d82992dda3e1d67055b4"
            mocked_scm.return_value.get_latest.side_effect = [
                "4ceea43add2366d8b8c5a622a2fb563b625b9abf",
                "fbed359411a1baa08d4a88e0d12d426fbf8f602c",
                "dbed259411a1baa08d4a88e0d12d426fbf8f6037",
            ]

            testmodule_mmd_path = path.join(BASE_DIR, "..", "staged_data", "testmodule.yaml")
            mmd = load_mmd_file(testmodule_mmd_path)
            # Set the module name and stream
            mmd = mmd.copy("testmodule", "master")
            module_build = module_build_service.models.ModuleBuild()
            module_build.name = "testmodule"
            module_build.stream = "master"
            module_build.version = 20170109091357
            module_build.state = models.BUILD_STATES["init"]
            module_build.scmurl = \
                "https://src.stg.fedoraproject.org/modules/testmodule.git?#ff1ea79"
            module_build.batch = 1
            module_build.owner = "Tom Brady"
            module_build.time_submitted = datetime(2017, 2, 15, 16, 8, 18)
            module_build.time_modified = datetime(2017, 2, 15, 16, 19, 35)
            module_build.rebuild_strategy = "changed-and-after"
            module_build.modulemd = mmd_to_str(mmd)
            db.session.add(module_build)
            db.session.commit()

            module_build_service.utils.record_component_builds(mmd, module_build)

            assert module_build.state == models.BUILD_STATES["init"]
            db.session.refresh(module_build)
            for c in module_build.component_builds:
                assert c.weight == 1.5

    @patch("module_build_service.scm.SCM")
    def test_format_mmd_arches(self, mocked_scm):
        with app.app_context():
            clean_database()
            mocked_scm.return_value.commit = "620ec77321b2ea7b0d67d82992dda3e1d67055b4"
            mocked_scm.return_value.get_latest.side_effect = [
                "4ceea43add2366d8b8c5a622a2fb563b625b9abf",
                "fbed359411a1baa08d4a88e0d12d426fbf8f602c",
                "dbed259411a1baa08d4a88e0d12d426fbf8f6037",
                "4ceea43add2366d8b8c5a622a2fb563b625b9abf",
                "fbed359411a1baa08d4a88e0d12d426fbf8f602c",
                "dbed259411a1baa08d4a88e0d12d426fbf8f6037",
            ]

            testmodule_mmd_path = path.join(BASE_DIR, "..", "staged_data", "testmodule.yaml")
            test_archs = ["powerpc", "i486"]

            mmd1 = load_mmd_file(testmodule_mmd_path)
            module_build_service.utils.format_mmd(mmd1, None)

            for pkg_name in mmd1.get_rpm_component_names():
                pkg = mmd1.get_rpm_component(pkg_name)
                assert set(pkg.get_arches()) == set(conf.arches)

            mmd2 = load_mmd_file(testmodule_mmd_path)

            for pkg_name in mmd2.get_rpm_component_names():
                pkg = mmd2.get_rpm_component(pkg_name)
                pkg.reset_arches()
                for arch in test_archs:
                    pkg.add_restricted_arch(arch)

            module_build_service.utils.format_mmd(mmd2, None)

            for pkg_name in mmd2.get_rpm_component_names():
                pkg = mmd2.get_rpm_component(pkg_name)
                assert set(pkg.get_arches()) == set(test_archs)

    @patch("module_build_service.scm.SCM")
    @patch("module_build_service.utils.submit.ThreadPool")
    def test_format_mmd_update_time_modified(self, tp, mocked_scm):
        with app.app_context():
            init_data()
            build = models.ModuleBuild.query.get(2)

            async_result = mock.MagicMock()
            async_result.ready.side_effect = [False, False, False, True]
            tp.return_value.map_async.return_value = async_result

            test_datetime = datetime(2019, 2, 14, 11, 11, 45, 42968)

            testmodule_mmd_path = path.join(BASE_DIR, "..", "staged_data", "testmodule.yaml")

            mmd1 = load_mmd_file(testmodule_mmd_path)

            with patch("module_build_service.utils.submit.datetime") as dt:
                dt.utcnow.return_value = test_datetime
                module_build_service.utils.format_mmd(mmd1, None, build, db.session)

            assert build.time_modified == test_datetime

    def test_generate_koji_tag_in_nsvc_format(self):
        name, stream, version, context = ("testmodule", "master", "20170816080815", "37c6c57")

        tag = module_build_service.utils.generate_koji_tag(name, stream, version, context)

        assert tag == "module-testmodule-master-20170816080815-37c6c57"

    def test_generate_koji_tag_in_hash_format(self):
        name, version, context = ("testmodule", "20170816080815", "37c6c57")
        stream = "this-is-a-stream-with-very-looooong-name" + "-blah" * 50
        nsvc_list = [name, stream, version, context]

        tag = module_build_service.utils.generate_koji_tag(*nsvc_list)
        expected_tag = "module-1cf457d452e54dda"
        assert tag == expected_tag

    @patch("module_build_service.utils.submit.requests")
    def test_pdc_eol_check(self, requests):
        """ Push mock pdc responses through the eol check function. """

        response = mock.Mock()
        response.json.return_value = {
            "results": [{
                "id": 347907,
                "global_component": "mariadb",
                "name": "10.1",
                "slas": [{"id": 694207, "sla": "security_fixes", "eol": "2019-12-01"}],
                "type": "module",
                "active": True,
                "critical_path": False,
            }]
        }
        requests.get.return_value = response

        is_eol = module_build_service.utils.submit._is_eol_in_pdc("mariadb", "10.1")
        assert not is_eol

        response.json.return_value["results"][0]["active"] = False

        is_eol = module_build_service.utils.submit._is_eol_in_pdc("mariadb", "10.1")
        assert is_eol

    def test_get_prefixed_version_f28(self):
        scheduler_init_data(1)
        build_one = models.ModuleBuild.query.get(2)
        v = module_build_service.utils.submit.get_prefixed_version(build_one.mmd())
        assert v == 2820180205135154

    def test_get_prefixed_version_fl701(self):
        scheduler_init_data(1)
        build_one = models.ModuleBuild.query.get(2)
        mmd = build_one.mmd()
        xmd = mmd.get_xmd()
        xmd["mbs"]["buildrequires"]["platform"]["stream"] = "fl7.0.1-beta"
        mmd.set_xmd(xmd)
        v = module_build_service.utils.submit.get_prefixed_version(mmd)
        assert v == 7000120180205135154

    @patch("module_build_service.utils.mse.generate_expanded_mmds")
    def test_submit_build_new_mse_build(self, generate_expanded_mmds):
        """
        Tests that finished build can be resubmitted in case the resubmitted
        build adds new MSE build (it means there are new expanded
        buildrequires).
        """
        build = make_module("foo:stream:0:c1", {}, {})
        assert build.state == models.BUILD_STATES["ready"]

        mmd1 = build.mmd()
        mmd2 = build.mmd()
        mmd2.set_context("c2")

        generate_expanded_mmds.return_value = [mmd1, mmd2]

        # Create a copy of mmd1 without xmd.mbs, since that will cause validate_mmd to fail
        mmd1_copy = mmd1.copy()
        mmd1_copy.set_xmd({})
        builds = module_build_service.utils.submit_module_build("foo", mmd1_copy, {})
        ret = {b.mmd().get_context(): b.state for b in builds}
        assert ret == {"c1": models.BUILD_STATES["ready"], "c2": models.BUILD_STATES["init"]}

        assert builds[0].siblings == [builds[1].id]
        assert builds[1].siblings == [builds[0].id]


class DummyModuleBuilder(GenericBuilder):
    """
    Dummy module builder
    """

    backend = "koji"
    _build_id = 0

    TAGGED_COMPONENTS = []

    @module_build_service.utils.validate_koji_tag("tag_name")
    def __init__(self, owner, module, config, tag_name, components):
        self.module_str = module
        self.tag_name = tag_name
        self.config = config

    def buildroot_connect(self, groups):
        pass

    def buildroot_prep(self):
        pass

    def buildroot_resume(self):
        pass

    def buildroot_ready(self, artifacts=None):
        return True

    def buildroot_add_dependency(self, dependencies):
        pass

    def buildroot_add_artifacts(self, artifacts, install=False):
        DummyModuleBuilder.TAGGED_COMPONENTS += artifacts

    def buildroot_add_repos(self, dependencies):
        pass

    def tag_artifacts(self, artifacts):
        pass

    def recover_orphaned_artifact(self, component_build):
        return []

    @property
    def module_build_tag(self):
        return {"name": self.tag_name + "-build"}

    def build(self, artifact_name, source):
        DummyModuleBuilder._build_id += 1
        state = koji.BUILD_STATES["COMPLETE"]
        reason = "Submitted %s to Koji" % (artifact_name)
        return DummyModuleBuilder._build_id, state, reason, None

    @staticmethod
    def get_disttag_srpm(disttag, module_build):
        # @FIXME
        return KojiModuleBuilder.get_disttag_srpm(disttag, module_build)

    def cancel_build(self, task_id):
        pass

    def list_tasks_for_components(self, component_builds=None, state="active"):
        pass

    def repo_from_tag(self, config, tag_name, arch):
        pass

    def finalize(self, succeeded=True):
        pass


@patch(
    "module_build_service.builder.GenericBuilder.default_buildroot_groups",
    return_value={"build": [], "srpm-build": []},
)
class TestBatches:
    def setup_method(self, test_method):
        reuse_component_init_data()
        GenericBuilder.register_backend_class(DummyModuleBuilder)

    def teardown_method(self, test_method):
        clean_database()
        DummyModuleBuilder.TAGGED_COMPONENTS = []
        GenericBuilder.register_backend_class(KojiModuleBuilder)

    def test_start_next_batch_build_reuse(self, default_buildroot_groups):
        """
        Tests that start_next_batch_build:
           1) Increments module.batch.
           2) Can reuse all components in batch
           3) Returns proper further_work messages for reused components.
           4) Returns the fake Repo change message
           5) Handling the further_work messages lead to proper tagging of
              reused components.
        """
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 1

        builder = mock.MagicMock()
        further_work = module_build_service.utils.start_next_batch_build(
            conf, module_build, db.session, builder)

        # Batch number should increase.
        assert module_build.batch == 2

        # KojiBuildChange messages in further_work should have build_new_state
        # set to COMPLETE, but the current component build state should be set
        # to BUILDING, so KojiBuildChange message handler handles the change
        # properly.
        for msg in further_work:
            if type(msg) == module_build_service.messaging.KojiBuildChange:
                assert msg.build_new_state == koji.BUILD_STATES["COMPLETE"]
                component_build = models.ComponentBuild.from_component_event(db.session, msg)
                assert component_build.state == koji.BUILD_STATES["BUILDING"]

        # When we handle these KojiBuildChange messages, MBS should tag all
        # the components just once.
        for msg in further_work:
            if type(msg) == module_build_service.messaging.KojiBuildChange:
                module_build_service.scheduler.handlers.components.complete(conf, db.session, msg)

        # Since we have reused all the components in the batch, there should
        # be fake KojiRepoChange message.
        assert type(further_work[-1]) == module_build_service.messaging.KojiRepoChange

        # Check that packages have been tagged just once.
        assert len(DummyModuleBuilder.TAGGED_COMPONENTS) == 2

    @patch("module_build_service.utils.batches.start_build_component")
    def test_start_next_batch_build_reuse_some(self, mock_sbc, default_buildroot_groups):
        """
        Tests that start_next_batch_build:
           1) Increments module.batch.
           2) Can reuse all components in the batch that it can.
           3) Returns proper further_work messages for reused components.
           4) Builds the remaining components
           5) Handling the further_work messages lead to proper tagging of
              reused components.
        """
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 1
        plc_component = models.ComponentBuild.query.filter_by(
            module_id=3, package="perl-List-Compare").one()
        plc_component.ref = "5ceea46add2366d8b8c5a623a2fb563b625b9abd"

        builder = mock.MagicMock()
        builder.recover_orphaned_artifact.return_value = []
        further_work = module_build_service.utils.start_next_batch_build(
            conf, module_build, db.session, builder)

        # Batch number should increase.
        assert module_build.batch == 2

        # Make sure we only have one message returned for the one reused component
        assert len(further_work) == 1
        # The KojiBuildChange message in further_work should have build_new_state
        # set to COMPLETE, but the current component build state in the DB should be set
        # to BUILDING, so KojiBuildChange message handler handles the change
        # properly.
        assert further_work[0].build_new_state == koji.BUILD_STATES["COMPLETE"]
        component_build = models.ComponentBuild.from_component_event(db.session, further_work[0])
        assert component_build.state == koji.BUILD_STATES["BUILDING"]
        assert component_build.package == "perl-Tangerine"
        assert component_build.reused_component_id is not None
        # Make sure perl-List-Compare is set to the build state as well but not reused
        assert plc_component.state == koji.BUILD_STATES["BUILDING"]
        assert plc_component.reused_component_id is None
        mock_sbc.assert_called_once()

    @patch("module_build_service.utils.batches.start_build_component")
    @patch(
        "module_build_service.config.Config.rebuild_strategy",
        new_callable=mock.PropertyMock,
        return_value="all",
    )
    def test_start_next_batch_build_rebuild_strategy_all(
        self, mock_rm, mock_sbc, default_buildroot_groups
    ):
        """
        Tests that start_next_batch_build can't reuse any components in the batch because the
        rebuild method is set to "all".
        """
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.rebuild_strategy = "all"
        module_build.batch = 1

        builder = mock.MagicMock()
        builder.recover_orphaned_artifact.return_value = []
        further_work = module_build_service.utils.start_next_batch_build(
            conf, module_build, db.session, builder)

        # Batch number should increase.
        assert module_build.batch == 2
        # No component reuse messages should be returned
        assert len(further_work) == 0
        # Make sure that both components in the batch were submitted
        assert len(mock_sbc.mock_calls) == 2

    def test_start_build_component_failed_state(self, default_buildroot_groups):
        """
        Tests whether exception occured while building sets the state to failed
        """
        builder = mock.MagicMock()
        builder.build.side_effect = Exception("Something have gone terribly wrong")
        component = mock.MagicMock()

        module_build_service.utils.batches.start_build_component(builder, component)

        assert component.state == koji.BUILD_STATES["FAILED"]

    @patch("module_build_service.utils.batches.start_build_component")
    @patch(
        "module_build_service.config.Config.rebuild_strategy",
        new_callable=mock.PropertyMock,
        return_value="only-changed",
    )
    def test_start_next_batch_build_rebuild_strategy_only_changed(
        self, mock_rm, mock_sbc, default_buildroot_groups
    ):
        """
        Tests that start_next_batch_build reuses all unchanged components in the batch because the
        rebuild method is set to "only-changed". This means that one component is reused in batch
        2, and even though the other component in batch 2 changed and was rebuilt, the component
        in batch 3 can be reused.
        """
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.rebuild_strategy = "only-changed"
        module_build.batch = 1
        # perl-List-Compare changed
        plc_component = models.ComponentBuild.query.filter_by(
            module_id=3, package="perl-List-Compare").one()
        plc_component.ref = "5ceea46add2366d8b8c5a623a2fb563b625b9abd"

        builder = mock.MagicMock()
        builder.recover_orphaned_artifact.return_value = []
        further_work = module_build_service.utils.start_next_batch_build(
            conf, module_build, db.session, builder)

        # Batch number should increase
        assert module_build.batch == 2

        # Make sure we only have one message returned for the one reused component
        assert len(further_work) == 1
        # The KojiBuildChange message in further_work should have build_new_state
        # set to COMPLETE, but the current component build state in the DB should be set
        # to BUILDING, so KojiBuildChange message handler handles the change
        # properly.
        assert further_work[0].build_new_state == koji.BUILD_STATES["COMPLETE"]
        component_build = models.ComponentBuild.from_component_event(db.session, further_work[0])
        assert component_build.state == koji.BUILD_STATES["BUILDING"]
        assert component_build.package == "perl-Tangerine"
        assert component_build.reused_component_id is not None
        # Make sure perl-List-Compare is set to the build state as well but not reused
        assert plc_component.state == koji.BUILD_STATES["BUILDING"]
        assert plc_component.reused_component_id is None
        mock_sbc.assert_called_once()
        mock_sbc.reset_mock()

        # Complete the build
        plc_component.state = koji.BUILD_STATES["COMPLETE"]
        pt_component = models.ComponentBuild.query.filter_by(
            module_id=3, package="perl-Tangerine").one()
        pt_component.state = koji.BUILD_STATES["COMPLETE"]

        # Start the next build batch
        further_work = module_build_service.utils.start_next_batch_build(
            conf, module_build, db.session, builder)
        # Batch number should increase
        assert module_build.batch == 3
        # Verify that tangerine was reused even though perl-Tangerine was rebuilt in the previous
        # batch
        assert further_work[0].build_new_state == koji.BUILD_STATES["COMPLETE"]
        component_build = models.ComponentBuild.from_component_event(db.session, further_work[0])
        assert component_build.state == koji.BUILD_STATES["BUILDING"]
        assert component_build.package == "tangerine"
        assert component_build.reused_component_id is not None
        mock_sbc.assert_not_called()

    @patch("module_build_service.utils.batches.start_build_component")
    def test_start_next_batch_build_smart_scheduling(self, mock_sbc, default_buildroot_groups):
        """
        Tests that components with the longest build time will be scheduled first
        """
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 1
        pt_component = models.ComponentBuild.query.filter_by(
            module_id=3, package="perl-Tangerine").one()
        pt_component.ref = "6ceea46add2366d8b8c5a623b2fb563b625bfabe"
        plc_component = models.ComponentBuild.query.filter_by(
            module_id=3, package="perl-List-Compare").one()
        plc_component.ref = "5ceea46add2366d8b8c5a623a2fb563b625b9abd"

        # Components are by default built by component id. To find out that weight is respected,
        # we have to set bigger weight to component with lower id.
        pt_component.weight = 3 if pt_component.id < plc_component.id else 4
        plc_component.weight = 4 if pt_component.id < plc_component.id else 3

        builder = mock.MagicMock()
        builder.recover_orphaned_artifact.return_value = []
        further_work = module_build_service.utils.start_next_batch_build(
            conf, module_build, db.session, builder)

        # Batch number should increase.
        assert module_build.batch == 2

        # Make sure we don't have any messages returned since no components should be reused
        assert len(further_work) == 0
        # Make sure both components are set to the build state but not reused
        assert pt_component.state == koji.BUILD_STATES["BUILDING"]
        assert pt_component.reused_component_id is None
        assert plc_component.state == koji.BUILD_STATES["BUILDING"]
        assert plc_component.reused_component_id is None

        # Test the order of the scheduling
        expected_calls = [mock.call(builder, plc_component), mock.call(builder, pt_component)]
        assert mock_sbc.mock_calls == expected_calls

    @patch("module_build_service.utils.batches.start_build_component")
    def test_start_next_batch_continue(self, mock_sbc, default_buildroot_groups):
        """
        Tests that start_next_batch_build does not start new batch when
        there are unbuilt components in the current one.
        """
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 2

        # The component was reused when the batch first started
        building_component = module_build.current_batch()[0]
        building_component.state = koji.BUILD_STATES["BUILDING"]
        building_component.reused_component_id = 123
        db.session.commit()

        builder = mock.MagicMock()
        further_work = module_build_service.utils.start_next_batch_build(
            conf, module_build, db.session, builder)

        # Batch number should not increase.
        assert module_build.batch == 2
        # Make sure start build was called for the second component which wasn't reused
        mock_sbc.assert_called_once()
        # No further work should be returned
        assert len(further_work) == 0

    def test_start_next_batch_build_repo_building(self, default_buildroot_groups):
        """
        Test that start_next_batch_build does not start new batch when
        builder.buildroot_ready() returns False.
        """
        module_build = models.ModuleBuild.query.filter_by(id=3).one()
        module_build.batch = 1

        builder = mock.MagicMock()
        builder.buildroot_ready.return_value = False

        # Batch number should not increase.
        assert module_build.batch == 1


@patch(
    "module_build_service.config.Config.mock_resultsdir",
    new_callable=mock.PropertyMock,
    return_value=path.join(BASE_DIR, "..", "staged_data", "local_builds"),
)
@patch(
    "module_build_service.config.Config.system", new_callable=mock.PropertyMock, return_value="mock"
)
class TestLocalBuilds:
    def setup_method(self):
        clean_database()

    def teardown_method(self):
        clean_database()

    def test_load_local_builds_name(self, conf_system, conf_resultsdir):
        with app.app_context():
            module_build_service.utils.load_local_builds("testmodule")
            local_modules = models.ModuleBuild.local_modules(db.session)

            assert len(local_modules) == 1
            assert local_modules[0].koji_tag.endswith(
                "/module-testmodule-master-20170816080816/results")

    def test_load_local_builds_name_stream(self, conf_system, conf_resultsdir):
        with app.app_context():
            module_build_service.utils.load_local_builds("testmodule:master")
            local_modules = models.ModuleBuild.local_modules(db.session)

            assert len(local_modules) == 1
            assert local_modules[0].koji_tag.endswith(
                "/module-testmodule-master-20170816080816/results")

    def test_load_local_builds_name_stream_non_existing(self, conf_system, conf_resultsdir):
        with app.app_context():
            with pytest.raises(RuntimeError):
                module_build_service.utils.load_local_builds("testmodule:x")
                models.ModuleBuild.local_modules(db.session)

    def test_load_local_builds_name_stream_version(self, conf_system, conf_resultsdir):
        with app.app_context():
            module_build_service.utils.load_local_builds("testmodule:master:20170816080815")
            local_modules = models.ModuleBuild.local_modules(db.session)

            assert len(local_modules) == 1
            assert local_modules[0].koji_tag.endswith(
                "/module-testmodule-master-20170816080815/results")

    def test_load_local_builds_name_stream_version_non_existing(self, conf_system, conf_resultsdir):
        with app.app_context():
            with pytest.raises(RuntimeError):
                module_build_service.utils.load_local_builds("testmodule:master:123")
                models.ModuleBuild.local_modules(db.session)

    def test_load_local_builds_platform(self, conf_system, conf_resultsdir):
        with app.app_context():
            module_build_service.utils.load_local_builds("platform")
            local_modules = models.ModuleBuild.local_modules(db.session)

            assert len(local_modules) == 1
            assert local_modules[0].koji_tag.endswith("/module-platform-f28-3/results")

    def test_load_local_builds_platform_f28(self, conf_system, conf_resultsdir):
        with app.app_context():
            module_build_service.utils.load_local_builds("platform:f28")
            local_modules = models.ModuleBuild.local_modules(db.session)

            assert len(local_modules) == 1
            assert local_modules[0].koji_tag.endswith("/module-platform-f28-3/results")


class TestOfflineLocalBuilds:
    def setup_method(self):
        clean_database()

    def teardown_method(self):
        clean_database()

    def test_import_fake_base_module(self):
        module_build_service.utils.import_fake_base_module("platform:foo:1:000000")
        module_build = models.ModuleBuild.get_build_from_nsvc(
            db.session, "platform", "foo", 1, "000000")
        assert module_build

        mmd = module_build.mmd()
        xmd = mmd.get_xmd()
        assert xmd == {
            "mbs": {
                "buildrequires": {},
                "commit": "ref_000000",
                "koji_tag": "repofile://",
                "mse": "true",
                "requires": {},
            }
        }

        assert set(mmd.get_profile_names()) == set(["buildroot", "srpm-buildroot"])

    @patch("module_build_service.utils.general.open", create=True, new_callable=mock.mock_open)
    def test_import_builds_from_local_dnf_repos(self, patched_open):
        with patch("dnf.Base") as dnf_base:
            repo = mock.MagicMock()
            repo.repofile = "/etc/yum.repos.d/foo.repo"
            tm_path = path.join(BASE_DIR, "..", "staged_data", "formatted_testmodule.yaml")
            mmd = load_mmd_file(tm_path)
            repo.get_metadata_content.return_value = mmd_to_str(mmd)
            base = dnf_base.return_value
            base.repos = {"reponame": repo}
            patched_open.return_value.readlines.return_value = ("FOO=bar", "PLATFORM_ID=platform:x")

            module_build_service.utils.import_builds_from_local_dnf_repos()

            base.read_all_repos.assert_called_once()
            repo.load.assert_called_once()
            repo.get_metadata_content.assert_called_once_with("modules")

            module_build = models.ModuleBuild.get_build_from_nsvc(
                db.session, "testmodule", "master", 20180205135154, "9c690d0e")
            assert module_build
            assert module_build.koji_tag == "repofile:///etc/yum.repos.d/foo.repo"

            module_build = models.ModuleBuild.get_build_from_nsvc(
                db.session, "platform", "x", 1, "000000")
            assert module_build

    def test_import_builds_from_local_dnf_repos_platform_id(self):
        with patch("dnf.Base"):
            module_build_service.utils.import_builds_from_local_dnf_repos(platform_id="platform:y")

            module_build = models.ModuleBuild.get_build_from_nsvc(
                db.session, "platform", "y", 1, "000000")
            assert module_build
