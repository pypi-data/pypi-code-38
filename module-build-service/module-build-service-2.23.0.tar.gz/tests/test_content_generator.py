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
# Written by Stanislav Ochotnicky <sochotnicky@redhat.com>
#            Jan Kaluza <jkaluza@redhat.com>

import io
import pytest
import json

import os
from os import path

import module_build_service.messaging
import module_build_service.scheduler.handlers.repos  # noqa
from module_build_service import models, conf, build_logs, Modulemd
from module_build_service.utils.general import mmd_to_str

from mock import patch, Mock, call, mock_open
import kobo.rpmlib

from tests import init_data
from tests.test_views.test_views import FakeSCM

import koji

from module_build_service.builder.KojiContentGenerator import KojiContentGenerator

GET_USER_RV = {
    "id": 3686,
    "krb_principal": "mszyslak@FEDORAPROJECT.ORG",
    "name": "Moe Szyslak",
    "status": 0,
    "usertype": 0,
}


class TestBuild:
    def setup_method(self, test_method):
        init_data(1, contexts=True)
        module = models.ModuleBuild.query.filter_by(id=2).one()
        module.cg_build_koji_tag = "f27-module-candidate"
        self.cg = KojiContentGenerator(module, conf)

        self.p_read_config = patch(
            "koji.read_config",
            return_value={
                "authtype": "kerberos",
                "timeout": 60,
                "server": "http://koji.example.com/",
            },
        )
        self.mock_read_config = self.p_read_config.start()

        # Ensure that there is no build log from other tests
        try:
            file_path = build_logs.path(self.cg.module)
            os.remove(file_path)
        except OSError:
            pass

    def teardown_method(self, test_method):
        self.p_read_config.stop()

        # Necessary to restart the twisted reactor for the next test.
        import sys

        del sys.modules["twisted.internet.reactor"]
        del sys.modules["moksha.hub.reactor"]
        del sys.modules["moksha.hub"]
        import moksha.hub.reactor  # noqa

        try:
            file_path = build_logs.path(self.cg.module)
            os.remove(file_path)
        except OSError:
            pass

    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    @patch("subprocess.Popen")
    @patch("module_build_service.builder.KojiContentGenerator.Modulemd")
    @patch("pkg_resources.get_distribution")
    @patch("platform.linux_distribution")
    @patch("platform.machine")
    @patch(
        "module_build_service.builder.KojiContentGenerator.KojiContentGenerator._koji_rpms_in_tag"
    )
    @pytest.mark.parametrize("devel", (False, True))
    def test_get_generator_json(
        self, rpms_in_tag, machine, distro, pkg_res, mock_Modulemd, popen, ClientSession, devel
    ):
        """ Test generation of content generator json """
        mock_Modulemd.get_version.return_value = "2.3.1"
        koji_session = ClientSession.return_value
        koji_session.getUser.return_value = GET_USER_RV
        koji_session.getTag.return_value = {"arches": ""}
        distro.return_value = ("Fedora", "25", "Twenty Five")
        machine.return_value = "i686"
        pkg_res.return_value = Mock()
        pkg_res.return_value.version = "current-tested-version"
        rpm_mock = Mock()
        rpm_out = (
            b"rpm-name;1.0;r1;x86_64;(none);sigmd5:1;sigpgp:p;siggpg:g\n"
            b"rpm-name-2;2.0;r2;i686;1;sigmd5:2;sigpgp:p2;siggpg:g2"
        )
        attrs = {"communicate.return_value": (rpm_out, "error"), "wait.return_value": 0}
        rpm_mock.configure_mock(**attrs)
        popen.return_value = rpm_mock

        tests_dir = path.abspath(path.dirname(__file__))
        rpm_in_tag_path = path.join(tests_dir, "test_get_generator_json_rpms_in_tag.json")
        with open(rpm_in_tag_path) as rpms_in_tag_file:
            rpms_in_tag.return_value = json.load(rpms_in_tag_file)

        expected_output_path = path.join(
            tests_dir, "test_get_generator_json_expected_output_with_log.json")
        with open(expected_output_path) as expected_output_file:
            expected_output = json.load(expected_output_file)

        # create the build.log
        build_logs.start(self.cg.module)
        build_logs.stop(self.cg.module)

        self.cg.devel = devel
        self.cg._load_koji_tag(koji_session)
        file_dir = self.cg._prepare_file_directory()
        ret = self.cg._get_content_generator_metadata(file_dir)
        rpms_in_tag.assert_called_once()
        if not devel:
            assert expected_output == ret
        else:
            # For devel, only check that the name has -devel suffix.
            assert ret["build"]["name"] == "nginx-devel"
            assert ret["build"]["extra"]["typeinfo"]["module"]["name"] == "nginx-devel"

        # Ensure an anonymous Koji session works
        koji_session.krb_login.assert_not_called()

    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    @patch("subprocess.Popen")
    @patch("module_build_service.builder.KojiContentGenerator.Modulemd")
    @patch("pkg_resources.get_distribution")
    @patch("platform.linux_distribution")
    @patch("platform.machine")
    @patch(
        "module_build_service.builder.KojiContentGenerator.KojiContentGenerator._koji_rpms_in_tag"
    )
    def test_get_generator_json_no_log(
        self, rpms_in_tag, machine, distro, pkg_res, mock_Modulemd, popen, ClientSession
    ):
        """ Test generation of content generator json """
        mock_Modulemd.get_version.return_value = "2.3.1"
        koji_session = ClientSession.return_value
        koji_session.getUser.return_value = GET_USER_RV
        koji_session.getTag.return_value = {"arches": ""}
        distro.return_value = ("Fedora", "25", "Twenty Five")
        machine.return_value = "i686"
        pkg_res.return_value = Mock()
        pkg_res.return_value.version = "current-tested-version"
        rpm_mock = Mock()
        rpm_out = (
            b"rpm-name;1.0;r1;x86_64;(none);sigmd5:1;sigpgp:p;siggpg:g\n"
            b"rpm-name-2;2.0;r2;i686;1;sigmd5:2;sigpgp:p2;siggpg:g2"
        )
        attrs = {"communicate.return_value": (rpm_out, "error"), "wait.return_value": 0}
        rpm_mock.configure_mock(**attrs)
        popen.return_value = rpm_mock

        tests_dir = path.abspath(path.dirname(__file__))
        rpm_in_tag_path = path.join(tests_dir, "test_get_generator_json_rpms_in_tag.json")
        with open(rpm_in_tag_path) as rpms_in_tag_file:
            rpms_in_tag.return_value = json.load(rpms_in_tag_file)

        expected_output_path = path.join(tests_dir, "test_get_generator_json_expected_output.json")
        with open(expected_output_path) as expected_output_file:
            expected_output = json.load(expected_output_file)
        self.cg._load_koji_tag(koji_session)
        file_dir = self.cg._prepare_file_directory()
        ret = self.cg._get_content_generator_metadata(file_dir)
        rpms_in_tag.assert_called_once()
        assert expected_output == ret

        # Anonymous koji session should work well.
        koji_session.krb_login.assert_not_called()

    def test_prepare_file_directory(self):
        """ Test preparation of directory with output files """
        dir_path = self.cg._prepare_file_directory()
        with io.open(path.join(dir_path, "modulemd.txt"), encoding="utf-8") as mmd:
            assert len(mmd.read()) == 1160

    def test_prepare_file_directory_per_arch_mmds(self):
        """ Test preparation of directory with output files """
        self.cg.arches = ["x86_64", "i686"]
        dir_path = self.cg._prepare_file_directory()
        with io.open(path.join(dir_path, "modulemd.txt"), encoding="utf-8") as mmd:
            assert len(mmd.read()) == 1160

        with io.open(path.join(dir_path, "modulemd.x86_64.txt"), encoding="utf-8") as mmd:
            assert len(mmd.read()) == 256

        with io.open(path.join(dir_path, "modulemd.i686.txt"), encoding="utf-8") as mmd:
            assert len(mmd.read()) == 254

    @patch.dict("sys.modules", krbV=Mock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_tag_cg_build(self, ClientSession):
        """ Test that the CG build is tagged. """
        koji_session = ClientSession.return_value
        koji_session.getUser.return_value = GET_USER_RV
        koji_session.getTag.return_value = {"id": 123}

        self.cg._tag_cg_build()

        koji_session.getTag.assert_called_once_with(self.cg.module.cg_build_koji_tag)
        koji_session.tagBuild.assert_called_once_with(123, "nginx-0-2.10e50d06")

        # tagBuild requires logging into a session in advance.
        koji_session.krb_login.assert_called_once()

    @patch.dict("sys.modules", krbV=Mock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_tag_cg_build_fallback_to_default_tag(self, ClientSession):
        """ Test that the CG build is tagged to default tag. """
        koji_session = ClientSession.return_value
        koji_session.getUser.return_value = GET_USER_RV
        koji_session.getTag.side_effect = [{}, {"id": 123}]

        self.cg._tag_cg_build()

        assert koji_session.getTag.mock_calls == [
            call(self.cg.module.cg_build_koji_tag),
            call(conf.koji_cg_default_build_tag),
        ]
        koji_session.tagBuild.assert_called_once_with(123, "nginx-0-2.10e50d06")

        # tagBuild requires logging into a session in advance.
        koji_session.krb_login.assert_called_once()

    @patch.dict("sys.modules", krbV=Mock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_tag_cg_build_no_tag_set(self, ClientSession):
        """ Test that the CG build is not tagged when no tag set. """
        koji_session = ClientSession.return_value
        koji_session.getUser.return_value = GET_USER_RV
        koji_session.getTag.side_effect = [{}, {"id": 123}]

        self.cg.module.cg_build_koji_tag = None
        self.cg._tag_cg_build()

        koji_session.tagBuild.assert_not_called()
        # tagBuild requires logging into a session in advance.
        koji_session.krb_login.assert_called_once()

    @patch.dict("sys.modules", krbV=Mock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_tag_cg_build_no_tag_available(self, ClientSession):
        """ Test that the CG build is not tagged when no tag available. """
        koji_session = ClientSession.return_value
        koji_session.getUser.return_value = GET_USER_RV
        koji_session.getTag.side_effect = [{}, {}]

        self.cg._tag_cg_build()

        koji_session.tagBuild.assert_not_called()
        # tagBuild requires logging into a session in advance.
        koji_session.krb_login.assert_called_once()

    @patch("module_build_service.builder.KojiContentGenerator.open", create=True)
    def test_get_arch_mmd_output(self, patched_open):
        patched_open.return_value = mock_open(read_data=self.cg.mmd.encode("utf-8")).return_value
        ret = self.cg._get_arch_mmd_output("./fake-dir", "x86_64")
        assert ret == {
            "arch": "x86_64",
            "buildroot_id": 1,
            "checksum": "aed2e2774c82cbc19fe9555f70cafd79",
            "checksum_type": "md5",
            "components": [],
            "extra": {"typeinfo": {"module": {}}},
            "filename": "modulemd.x86_64.txt",
            "filesize": 1162,
            "type": "file",
        }

    @patch("module_build_service.builder.KojiContentGenerator.open", create=True)
    def test_get_arch_mmd_output_components(self, patched_open):
        mmd = self.cg.module.mmd()
        mmd.add_rpm_artifact("dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64")
        mmd_data = mmd_to_str(mmd).encode("utf-8")

        patched_open.return_value = mock_open(read_data=mmd_data).return_value

        self.cg.rpms = [
            {
                "name": "dhcp",
                "version": "4.3.5",
                "release": "5.module_2118aef6",
                "arch": "x86_64",
                "epoch": "12",
                "payloadhash": "hash",
            }
        ]

        self.cg.rpms_dict = {
            "dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64": {
                "name": "dhcp",
                "version": "4.3.5",
                "release": "5.module_2118aef6",
                "arch": "x86_64",
                "epoch": "12",
                "payloadhash": "hash",
            }
        }

        ret = self.cg._get_arch_mmd_output("./fake-dir", "x86_64")
        assert ret == {
            "arch": "x86_64",
            "buildroot_id": 1,
            "checksum": "5fbad2ef9b6c5496bdce4368ca3182d6",
            "checksum_type": "md5",
            "components": [
                {
                    u"arch": "x86_64",
                    u"epoch": "12",
                    u"name": "dhcp",
                    u"release": "5.module_2118aef6",
                    u"sigmd5": "hash",
                    u"type": u"rpm",
                    u"version": "4.3.5",
                }
            ],
            "extra": {"typeinfo": {"module": {}}},
            "filename": "modulemd.x86_64.txt",
            "filesize": 316,
            "type": "file",
        }

    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_koji_rpms_in_tag(self, ClientSession):
        koji_session = ClientSession.return_value
        koji_session.getUser.return_value = GET_USER_RV
        koji_session.getTag.return_value = {"arches": "x86_64"}

        rpms = [
            {
                "id": 1,
                "arch": "src",
                "epoch": None,
                "build_id": 875991,
                "name": "module-build-macros",
                "release": "1.module_92011fe6",
                "version": "0.1",
            },
            {
                "id": 2,
                "arch": "noarch",
                "epoch": None,
                "build_id": 875991,
                "name": "module-build-macros",
                "release": "1.module_92011fe6",
                "version": "0.1",
            },
            {
                "id": 3,
                "arch": "src",
                "epoch": 3,
                "build_id": 875636,
                "name": "ed",
                "release": "2.module_bd6e0eb1",
                "version": "1.14.1",
            },
            {
                "id": 4,
                "arch": "x86_64",
                "epoch": 3,
                "build_id": 875636,
                "name": "ed",
                "release": "2.module_bd6e0eb1",
                "version": "1.14.1",
            },
        ]

        builds = [
            {
                "build_id": 875636,
                "epoch": 3,
                "name": "ed",
                "release": "2.module_bd6e0eb1",
                "version": "1.14.1",
                "nvr": "ed-2.module_bd6e0eb1-1.14.1",
            },
            {
                "build_id": 875991,
                "epoch": None,
                "name": "module-build-macros",
                "release": "1.module_92011fe6",
                "version": "0.1",
                "nvr": "module-build-macros-0.1-1.module_92011fe6",
            },
        ]

        koji_session.listTaggedRPMS.return_value = (rpms, builds)
        koji_session.multiCall.side_effect = [
            # getRPMHeaders response
            [
                [{"excludearch": ["x86_64"], "exclusivearch": [], "license": "MIT"}],
                [{"excludearch": [], "exclusivearch": ["x86_64"], "license": "GPL"}],
                [{"license": "MIT"}],
                [{"license": "GPL"}],
            ]
        ]

        rpms = self.cg._koji_rpms_in_tag("tag")
        for rpm in rpms:
            # We want to mainly check the excludearch and exclusivearch code.
            if rpm["name"] == "module-build-macros":
                assert rpm["srpm_nevra"] == "module-build-macros-0:0.1-1.module_92011fe6.src"
                assert rpm["excludearch"] == ["x86_64"]
                assert rpm["license"] == "MIT"
            else:
                assert rpm["srpm_nevra"] == "ed-3:1.14.1-2.module_bd6e0eb1.src"
                assert rpm["exclusivearch"] == ["x86_64"]
                assert rpm["license"] == "GPL"

        # Listing tagged RPMs does not require to log into a session
        koji_session.krb_login.assert_not_called()

    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_koji_rpms_in_tag_empty_tag(self, ClientSession):
        koji_session = ClientSession.return_value
        koji_session.getUser.return_value = GET_USER_RV
        koji_session.getTag.return_value = {"arches": "x86_64"}
        koji_session.listTaggedRPMS.return_value = ([], [])
        koji_session.multiCall.side_effect = [[], [], [], []]

        rpms = self.cg._koji_rpms_in_tag("tag")
        assert rpms == []
        koji_session.multiCall.assert_not_called()

    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_koji_rpms_in_tag_empty_headers(self, ClientSession):
        koji_session = ClientSession.return_value
        koji_session.getUser.return_value = GET_USER_RV
        koji_session.getTag.return_value = {"arches": "x86_64"}

        rpms = [
            {
                "id": 1,
                "arch": "src",
                "epoch": None,
                "build_id": 875991,
                "name": "module-build-macros",
                "release": "1.module_92011fe6",
                "version": "0.1",
            },
            {
                "id": 2,
                "arch": "noarch",
                "epoch": None,
                "build_id": 875991,
                "name": "module-build-macros",
                "release": "1.module_92011fe6",
                "version": "0.1",
            },
        ]

        builds = [
            {
                "build_id": 875991,
                "epoch": None,
                "name": "module-build-macros",
                "release": "1.module_92011fe6",
                "version": "0.1",
                "nvr": "module-build-macros-0.1-1.module_92011fe6",
            }
        ]

        koji_session.listTaggedRPMS.return_value = (rpms, builds)

        koji_session.multiCall.side_effect = [
            # getRPMHeaders response
            [[{}], [{}]]
        ]

        with pytest.raises(RuntimeError) as cm:
            self.cg._koji_rpms_in_tag("tag")
        assert str(cm.value) == ("No RPM headers received from Koji for RPM module-build-macros")

        koji_session.multiCall.side_effect = [
            # getRPMHeaders response
            [[{"something": "x"}], [{}]]
        ]

        with pytest.raises(RuntimeError) as cm:
            self.cg._koji_rpms_in_tag("tag")
        assert str(cm.value) == (
            "No RPM 'license' header received from Koji for RPM module-build-macros"
        )

    def _add_test_rpm(
        self,
        nevra,
        srpm_nevra,
        multilib=None,
        koji_srpm_nevra=None,
        excludearch=None,
        exclusivearch=None,
        license=None,
    ):
        """
        Helper method to add test RPM to ModuleBuild used by KojiContentGenerator
        and also to Koji tag used to generate the Content Generator build.

        :param str nevra: NEVRA of the RPM to add.
        :param str srpm_nevra: NEVRA of SRPM the added RPM is built from.
        :param list multilib: List of architecture for which the multilib should be turned on.
        :param str koji_srpm_nevra: If set, overrides the `srpm_nevra` in Koji tag. This is
            needed to test the case when the built "src" package has different name than
            the package in Koji. This is for example case of software collections where
            the name in `srpm_nevra` is "httpd" but `koji_srpm_nevra` name
            would be "httpd24-httpd".
        :param list excludearch: List of architectures this package is excluded from.
        :param list exclusivearch: List of architectures this package is exclusive for.
        :param str license: License of this RPM.
        """
        srpm_name = kobo.rpmlib.parse_nvra(srpm_nevra)["name"]

        parsed_nevra = kobo.rpmlib.parse_nvra(nevra)
        parsed_nevra["payloadhash"] = "hash"
        if koji_srpm_nevra:
            parsed_nevra["srpm_nevra"] = koji_srpm_nevra
            parsed_nevra["srpm_name"] = kobo.rpmlib.parse_nvra(koji_srpm_nevra)["name"]
        else:
            parsed_nevra["srpm_nevra"] = srpm_nevra
            parsed_nevra["srpm_name"] = srpm_name
        parsed_nevra["excludearch"] = excludearch or []
        parsed_nevra["exclusivearch"] = exclusivearch or []
        parsed_nevra["license"] = license or ""
        self.cg.rpms.append(parsed_nevra)
        self.cg.rpms_dict[nevra] = parsed_nevra

        mmd = self.cg.module.mmd()
        if srpm_name not in mmd.get_rpm_component_names():
            component = Modulemd.ComponentRpm.new(srpm_name)
            component.set_rationale("foo")

            if multilib:
                for arch in multilib:
                    component.add_multilib_arch(arch)

            mmd.add_component(component)
            self.cg.module.modulemd = mmd_to_str(mmd)
            self.cg.modulemd = mmd_to_str(mmd)

    @pytest.mark.parametrize("devel", (False, True))
    def test_fill_in_rpms_list(self, devel):
        self._add_test_rpm(
            "dhcp-12:4.3.5-5.module_2118aef6.src", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.i686", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.s390x", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.x86_64",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.i686",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.s390x",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )

        self.cg.devel = devel
        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        if not devel:
            # Only x86_64 packages should be filled in, because we requested x86_64 arch.
            assert set(mmd.get_rpm_artifacts()) == set([
                "dhcp-12:4.3.5-5.module_2118aef6.src",
                "dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64",
                "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
                "perl-Tangerine-12:4.3.5-5.module_2118aef6.x86_64",
            ])
        else:
            # The i686 packages are filtered out in normal packages, because multilib
            # is not enabled for them - therefore we want to include them in -devel.
            assert set(mmd.get_rpm_artifacts()) == set([
                "dhcp-libs-12:4.3.5-5.module_2118aef6.i686",
                "perl-Tangerine-12:4.3.5-5.module_2118aef6.i686",
            ])

    def test_fill_in_rpms_exclusivearch(self):
        self._add_test_rpm(
            "dhcp-12:4.3.5-5.module_2118aef6.src", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.noarch",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
            exclusivearch=["x86_64"],
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.noarch",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            exclusivearch=["ppc64le"],
        )

        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        # Only dhcp-libs should be filled in, because perl-Tangerine has different
        # exclusivearch.
        assert set(mmd.get_rpm_artifacts()) == set(
            ["dhcp-12:4.3.5-5.module_2118aef6.src", "dhcp-libs-12:4.3.5-5.module_2118aef6.noarch"])

    def test_fill_in_rpms_excludearch(self):
        self._add_test_rpm(
            "dhcp-12:4.3.5-5.module_2118aef6.src", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.noarch",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
            excludearch=["x86_64"],
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.noarch",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            excludearch=["ppc64le"],
        )

        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        # Only perl-Tangerine should be filled in, because dhcp-libs is excluded from x86_64.
        assert set(mmd.get_rpm_artifacts()) == set([
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.noarch",
        ])

    @pytest.mark.parametrize("devel", (False, True))
    def test_fill_in_rpms_rpm_whitelist(self, devel):
        self._add_test_rpm(
            "python27-dhcp-12:4.3.5-5.module_2118aef6.src",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
            koji_srpm_nevra="python27-dhcp-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "python27-dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
            koji_srpm_nevra="python27-dhcp-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "python27-dhcp-libs-12:4.3.5-5.module_2118aef6.i686",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
            koji_srpm_nevra="python27-dhcp-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "foo-perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            koji_srpm_nevra="foo-perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "foo-perl-Tangerine-12:4.3.5-5.module_2118aef6.x86_64",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            koji_srpm_nevra="foo-perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "foo-perl-Tangerine-12:4.3.5-5.module_2118aef6.i686",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            koji_srpm_nevra="foo-perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )

        self.cg.devel = devel
        mmd = self.cg.module.mmd()
        opts = mmd.get_buildopts()
        if not opts:
            opts = Modulemd.Buildopts()
        opts.add_rpm_to_whitelist("python27-dhcp")
        mmd.set_buildopts(opts)

        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        if not devel:
            # Only x86_64 dhcp-libs should be filled in, because only python27-dhcp is whitelisted
            # srpm name.
            assert set(mmd.get_rpm_artifacts()) == set([
                "python27-dhcp-12:4.3.5-5.module_2118aef6.src",
                "python27-dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64",
            ])
        else:
            assert set(mmd.get_rpm_artifacts()) == set([
                "python27-dhcp-libs-12:4.3.5-5.module_2118aef6.i686",
                "foo-perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
                "foo-perl-Tangerine-12:4.3.5-5.module_2118aef6.x86_64",
                "foo-perl-Tangerine-12:4.3.5-5.module_2118aef6.i686",
            ])

    @pytest.mark.parametrize("devel", (False, True))
    def test_fill_in_rpms_list_filters(self, devel):
        self._add_test_rpm(
            "dhcp-12:4.3.5-5.module_2118aef6.src", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "dhcp-libs-debuginfo-12:4.3.5-5.module_2118aef6.x86_64",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "dhcp-libs-debugsource-12:4.3.5-5.module_2118aef6.x86_64",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.i686", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "dhcp-libs-debuginfo-12:4.3.5-5.module_2118aef6.i686",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "dhcp-libs-debugsource-12:4.3.5-5.module_2118aef6.i686",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.x86_64",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-debuginfo-12:4.3.5-5.module_2118aef6.x86_64",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-debugsource-12:4.3.5-5.module_2118aef6.x86_64",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.i686",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-debuginfo-12:4.3.5-5.module_2118aef6.i686",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-debugsource-12:4.3.5-5.module_2118aef6.i686",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )

        self.cg.devel = devel
        mmd = self.cg.module.mmd()
        for rpm in mmd.get_rpm_filters():
            mmd.remove_rpm_filter(rpm)
        mmd.add_rpm_filter("dhcp-libs")

        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        if not devel:
            # Only x86_64 perl-Tangerine should be filled in, because dhcp-libs is filtered out.
            assert set(mmd.get_rpm_artifacts()) == set([
                "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
                "perl-Tangerine-12:4.3.5-5.module_2118aef6.x86_64",
                "perl-Tangerine-debuginfo-12:4.3.5-5.module_2118aef6.x86_64",
                "perl-Tangerine-debugsource-12:4.3.5-5.module_2118aef6.x86_64",
            ])
        else:
            assert set(mmd.get_rpm_artifacts()) == set([
                "dhcp-12:4.3.5-5.module_2118aef6.src",
                "dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64",
                "dhcp-libs-debuginfo-12:4.3.5-5.module_2118aef6.x86_64",
                "dhcp-libs-debugsource-12:4.3.5-5.module_2118aef6.x86_64",
                "dhcp-libs-12:4.3.5-5.module_2118aef6.i686",
                "dhcp-libs-debuginfo-12:4.3.5-5.module_2118aef6.i686",
                "dhcp-libs-debugsource-12:4.3.5-5.module_2118aef6.i686",
                "perl-Tangerine-12:4.3.5-5.module_2118aef6.i686",
                "perl-Tangerine-debuginfo-12:4.3.5-5.module_2118aef6.i686",
                "perl-Tangerine-debugsource-12:4.3.5-5.module_2118aef6.i686",
            ])

    @pytest.mark.parametrize("devel", (False, True))
    def test_fill_in_rpms_list_multilib(self, devel):
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.src",
            "dhcp-libs-12:4.3.5-5.module_2118aef6.src",
            multilib=["x86_64"],
        )
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64",
            "dhcp-libs-12:4.3.5-5.module_2118aef6.src",
            multilib=["x86_64"],
        )
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.i686",
            "dhcp-libs-12:4.3.5-5.module_2118aef6.src",
            multilib=["x86_64"],
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            multilib=["ppc64le"],
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.x86_64",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            multilib=["ppc64le"],
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.i686",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            multilib=["ppc64le"],
        )

        self.cg.devel = devel
        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        if not devel:
            # Only i686 package for dhcp-libs should be added, because perl-Tangerine does not have
            # multilib set.
            assert set(mmd.get_rpm_artifacts()) == set([
                "dhcp-libs-12:4.3.5-5.module_2118aef6.src",
                "dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64",
                "dhcp-libs-12:4.3.5-5.module_2118aef6.i686",
                "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
                "perl-Tangerine-12:4.3.5-5.module_2118aef6.x86_64",
            ])
        else:
            assert set(mmd.get_rpm_artifacts()) == set(
                ["perl-Tangerine-12:4.3.5-5.module_2118aef6.i686"])

    @pytest.mark.parametrize(
        "licenses, expected",
        ((["GPL", "MIT"], ["GPL", "MIT"]), (["GPL", ""], ["GPL"]), (["GPL", "GPL"], ["GPL"])),
    )
    def test_fill_in_rpms_list_license(self, licenses, expected):
        self._add_test_rpm(
            "dhcp-12:4.3.5-5.module_2118aef6.src", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.x86_64",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
            license=licenses[0],
        )
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.i686", "dhcp-12:4.3.5-5.module_2118aef6.src")
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.x86_64",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
            license=licenses[1],
        )
        self._add_test_rpm(
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.i686",
            "perl-Tangerine-12:4.3.5-5.module_2118aef6.src",
        )

        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        # Only x86_64 packages should be filled in, because we requested x86_64 arch.
        assert set(mmd.get_content_licenses()) == set(expected)

    @pytest.mark.parametrize("devel", (False, True))
    def test_fill_in_rpms_list_noarch_filtering_not_influenced_by_multilib(self, devel):
        # A build has ExcludeArch: i686 (because it only works on 64 bit arches).
        # A noarch package is built there, and this noarch packages should be
        # included in x86_64 repo.
        self._add_test_rpm(
            "dhcp-libs-12:4.3.5-5.module_2118aef6.noarch",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
            excludearch=["i686"],
        )
        self._add_test_rpm(
            "dhcp-12:4.3.5-5.module_2118aef6.src",
            "dhcp-12:4.3.5-5.module_2118aef6.src",
            excludearch=["i686"],
        )

        self.cg.devel = devel
        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        if not devel:
            # Only i686 package for dhcp-libs should be added, because perl-Tangerine does not have
            # multilib set. The "dhcp" SRPM should be also included.
            assert set(mmd.get_rpm_artifacts()) == set([
                "dhcp-libs-12:4.3.5-5.module_2118aef6.noarch",
                "dhcp-12:4.3.5-5.module_2118aef6.src",
            ])
        else:
            assert set(mmd.get_rpm_artifacts()) == set([])

    def test_sanitize_mmd(self):
        mmd = self.cg.module.mmd()
        component = Modulemd.ComponentRpm.new("foo")
        component.set_rationale("foo")
        component.set_repository("http://private.tld/foo.git")
        component.set_cache("http://private.tld/cache")
        mmd.add_component(component)
        mmd.set_xmd({"mbs": {"buildrequires": []}})
        mmd = self.cg._sanitize_mmd(mmd)

        for pkg_name in mmd.get_rpm_component_names():
            pkg = mmd.get_rpm_component(pkg_name)
            assert pkg.get_repository() is None
            assert pkg.get_cache() is None

        assert "mbs" not in mmd.get_xmd().keys()

    @patch("module_build_service.builder.KojiContentGenerator.SCM")
    def test_prepare_file_directory_modulemd_src(self, mocked_scm):
        FakeSCM(
            mocked_scm,
            "testmodule",
            "testmodule_init.yaml",
            "620ec77321b2ea7b0d67d82992dda3e1d67055b4",
        )
        mmd = self.cg.module.mmd()
        mmd.set_xmd({"mbs": {"commit": "foo", "scmurl": "git://localhost/modules/foo.git#master"}})
        self.cg.module.modulemd = mmd_to_str(mmd)
        file_dir = self.cg._prepare_file_directory()
        with io.open(path.join(file_dir, "modulemd.src.txt"), encoding="utf-8") as mmd:
            assert len(mmd.read()) == 1339

    def test_finalize_mmd_devel(self):
        self.cg.devel = True
        mmd = self.cg.module.mmd()
        new_mmd = module_build_service.utils.load_mmd(self.cg._finalize_mmd("x86_64"))

        # Check that -devel suffix is set.
        assert new_mmd.get_module_name().endswith("-devel")

        # Check that -devel requires non-devel.
        for dep in new_mmd.get_dependencies():
            requires = []
            for name in dep.get_runtime_modules():
                for stream in dep.get_runtime_streams(name):
                    requires.append("%s:%s" % (name, stream))
            assert "%s:%s" % (mmd.get_module_name(), mmd.get_stream_name()) in requires

    @patch.dict("sys.modules", krbV=Mock())
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    @patch("module_build_service.builder.KojiContentGenerator.KojiContentGenerator._tag_cg_build")
    @patch("module_build_service.builder.KojiContentGenerator.KojiContentGenerator._load_koji_tag")
    def test_koji_cg_koji_import(self, tag_loader, tagger, cl_session):
        """ Tests whether build is still tagged even if there's an exception in CGImport """
        cl_session.return_value.CGImport = Mock(
            side_effect=koji.GenericError("Build already exists asdv"))
        self.cg.koji_import()
        tagger.assert_called()

    def test_fill_in_rpms_list_debuginfo_deps(self):
        """
        Tests that -debuginfo RPM required by other -debuginfo RPM is included in a RPM list.

        The python3-pymongo has matching python3-pymongo-debuginfo RPM which requires
        python-pymongo-debuginfo RPM. All of them should appear in RPM list
        """
        self._add_test_rpm(
            "python-pymongo-debuginfo-3.6.1-9.module+f29.1.0+2993+d789589b.x86_64",
            "python-pymongo-3.6.1-9.module+f29.1.0+2993+d789589b.src")

        self._add_test_rpm(
            "python3-pymongo-debuginfo-3.6.1-9.module+f29.1.0+2993+d789589b.x86_64",
            "python-pymongo-3.6.1-9.module+f29.1.0+2993+d789589b.src")

        self._add_test_rpm(
            "python3-pymongo-3.6.1-9.module+f29.1.0+2993+d789589b.x86_64",
            "python-pymongo-3.6.1-9.module+f29.1.0+2993+d789589b.src")

        self._add_test_rpm(
            "python-pymongo-3.6.1-9.module+f29.1.0+2993+d789589b.src",
            "python-pymongo-3.6.1-9.module+f29.1.0+2993+d789589b.src")

        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        assert set(mmd.get_rpm_artifacts()) == set([
            'python-pymongo-debuginfo-3.6.1-9.module+f29.1.0+2993+d789589b.x86_64',
            'python3-pymongo-debuginfo-3.6.1-9.module+f29.1.0+2993+d789589b.x86_64',
            'python-pymongo-3.6.1-9.module+f29.1.0+2993+d789589b.src',
            'python3-pymongo-3.6.1-9.module+f29.1.0+2993+d789589b.x86_64'])

    def test_fill_in_rpms_list_debuginfo_deps_psycopg2(self):
        """
        Tests that -debuginfo RPM required by other -debuginfo RPM is included in a RPM list
        with the psycopg2 RPM test-case, because psycopg2 RPMs are built in kind of special
        way...
        """
        self._add_test_rpm(
            "python2-psycopg2-debuginfo-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python2-psycopg2-debug-debuginfo-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python-psycopg2-debugsource-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python-psycopg2-debuginfo-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python2-psycopg2-tests-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python2-psycopg2-debug-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python2-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        assert set(mmd.get_rpm_artifacts()) == set([
            "python2-psycopg2-debuginfo-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python2-psycopg2-debug-debuginfo-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-debugsource-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-debuginfo-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python2-psycopg2-tests-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python2-psycopg2-debug-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python2-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src"])

    def test_fill_in_rpms_list_debugsource_for_non_srpm(self):
        self._add_test_rpm(
            "python2-psycopg2-debugsource-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python2-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        assert set(mmd.get_rpm_artifacts()) == set([
            "python2-psycopg2-debugsource-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python2-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src"])

    def test_fill_in_rpms_list_debuginfo_deps_glibc(self):
        self._add_test_rpm(
            "glibc-common-2.29.9000-16.fc31.x86_64",
            "glibc-2.29.9000-16.fc31.src")

        self._add_test_rpm(
            "glibc-2.29.9000-16.fc31.x86_64",
            "glibc-2.29.9000-16.fc31.src")

        self._add_test_rpm(
            "glibc-debuginfo-common-2.29.9000-16.fc31.x86_64",
            "glibc-2.29.9000-16.fc31.src")

        self._add_test_rpm(
            "glibc-debuginfo-2.29.9000-16.fc31.x86_64",
            "glibc-2.29.9000-16.fc31.src")

        self._add_test_rpm(
            "glibc-2.29.9000-16.fc31.src",
            "glibc-2.29.9000-16.fc31.src")

        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        assert set(mmd.get_rpm_artifacts()) == set([
            "glibc-common-2.29.9000-16.fc31.x86_64",
            "glibc-2.29.9000-16.fc31.src",
            "glibc-2.29.9000-16.fc31.x86_64",
            "glibc-debuginfo-common-2.29.9000-16.fc31.x86_64",
            "glibc-debuginfo-2.29.9000-16.fc31.x86_64"])

    def test_fill_in_rpms_list_debuginfo_deps_kernel(self):
        self._add_test_rpm(
            "kernel-debuginfo-common-aarch64-5.0.9-301.fc30.aarch64",
            "kernel-5.0.9-301.fc30.src")

        self._add_test_rpm(
            "kernel-debuginfo-5.0.9-301.fc30.aarch64",
            "kernel-5.0.9-301.fc30.src")

        self._add_test_rpm(
            "kernel-5.0.9-301.fc30.aarch64",
            "kernel-5.0.9-301.fc30.src")

        self._add_test_rpm(
            "kernel-5.0.9-301.fc30.src",
            "kernel-5.0.9-301.fc30.src")

        mmd = self.cg.module.mmd()
        mmd = self.cg._fill_in_rpms_list(mmd, "aarch64")

        assert set(mmd.get_rpm_artifacts()) == set([
            "kernel-debuginfo-common-aarch64-5.0.9-301.fc30.aarch64",
            "kernel-5.0.9-301.fc30.src",
            "kernel-debuginfo-5.0.9-301.fc30.aarch64",
            "kernel-5.0.9-301.fc30.aarch64"])

    def test_fill_in_rpms_list_debugsource_not_included(self):
        self._add_test_rpm(
            "python-psycopg2-debugsource-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python2-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.x86_64",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        self._add_test_rpm(
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src",
            "python-psycopg2-2.7.5-7.module+f29.0.0+2961+596d0223.src")

        mmd = self.cg.module.mmd()
        for rpm in mmd.get_rpm_filters():
            mmd.remove_rpm_filter(rpm)
        mmd.add_rpm_filter("python2-psycopg2")
        mmd = self.cg._fill_in_rpms_list(mmd, "x86_64")

        assert set(mmd.get_rpm_artifacts()) == set([])
