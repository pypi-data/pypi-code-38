# Copyright (c) 2018  Red Hat, Inc.
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

import os

from mock import patch, PropertyMock, Mock, call

import module_build_service.resolver as mbs_resolver
import module_build_service.utils
from module_build_service.utils.general import mmd_to_str
import module_build_service.models
import tests


base_dir = os.path.join(os.path.dirname(__file__), "..")


class TestMBSModule:
    @patch("requests.Session")
    def test_get_module_modulemds_nsvc(self, mock_session, testmodule_mmd_9c690d0e):
        """ Tests for querying a module from mbs """
        mock_res = Mock()
        mock_res.ok.return_value = True
        mock_res.json.return_value = {
            "items": [
                {
                    "name": "testmodule",
                    "stream": "master",
                    "version": "20180205135154",
                    "context": "9c690d0e",
                    "modulemd": testmodule_mmd_9c690d0e,
                }
            ],
            "meta": {"next": None},
        }

        mock_session().get.return_value = mock_res

        resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="mbs")
        module_mmds = resolver.get_module_modulemds(
            "testmodule", "master", "20180205135154", "9c690d0e", virtual_streams=["f28"]
        )
        nsvcs = set(
            m.get_nsvc()
            for m in module_mmds
        )
        expected = set(["testmodule:master:20180205135154:9c690d0e"])
        mbs_url = tests.conf.mbs_url
        expected_query = {
            "name": "testmodule",
            "stream": "master",
            "version": "20180205135154",
            "context": "9c690d0e",
            "verbose": True,
            "order_desc_by": "version",
            "page": 1,
            "per_page": 10,
            "state": "ready",
            "virtual_stream": ["f28"],
        }
        mock_session().get.assert_called_once_with(mbs_url, params=expected_query)
        assert nsvcs == expected

    @patch("requests.Session")
    def test_get_module_modulemds_partial(
        self, mock_session, testmodule_mmd_9c690d0e, testmodule_mmd_c2c572ed
    ):
        """ Test for querying MBS without the context of a module """

        version = "20180205135154"

        mock_res = Mock()
        mock_res.ok.return_value = True
        mock_res.json.return_value = {
            "items": [
                {
                    "name": "testmodule",
                    "stream": "master",
                    "version": version,
                    "context": "9c690d0e",
                    "modulemd": testmodule_mmd_9c690d0e,
                },
                {
                    "name": "testmodule",
                    "stream": "master",
                    "version": version,
                    "context": "c2c572ed",
                    "modulemd": testmodule_mmd_c2c572ed,
                },
            ],
            "meta": {"next": None},
        }

        mock_session().get.return_value = mock_res
        resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="mbs")
        ret = resolver.get_module_modulemds("testmodule", "master", version)
        nsvcs = set(
            m.get_nsvc()
            for m in ret
        )
        expected = set([
            "testmodule:master:20180205135154:9c690d0e",
            "testmodule:master:20180205135154:c2c572ed",
        ])
        mbs_url = tests.conf.mbs_url
        expected_query = {
            "name": "testmodule",
            "stream": "master",
            "version": version,
            "verbose": True,
            "order_desc_by": "version",
            "page": 1,
            "per_page": 10,
            "state": "ready",
        }
        mock_session().get.assert_called_once_with(mbs_url, params=expected_query)
        assert nsvcs == expected

    @patch("requests.Session")
    def test_get_module_build_dependencies(
        self, mock_session, platform_mmd, testmodule_mmd_9c690d0e
    ):
        """
        Tests that we return just direct build-time dependencies of testmodule.
        """
        mock_res = Mock()
        mock_res.ok.return_value = True
        mock_res.json.side_effect = [
            {
                "items": [
                    {
                        "name": "testmodule",
                        "stream": "master",
                        "version": "20180205135154",
                        "context": "9c690d0e",
                        "modulemd": testmodule_mmd_9c690d0e,
                    }
                ],
                "meta": {"next": None},
            },
            {
                "items": [
                    {
                        "name": "platform",
                        "stream": "f28",
                        "version": "3",
                        "context": "00000000",
                        "modulemd": platform_mmd,
                        "koji_tag": "module-f28-build",
                    }
                ],
                "meta": {"next": None},
            },
        ]

        mock_session().get.return_value = mock_res
        expected = set(["module-f28-build"])
        resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="mbs")
        result = resolver.get_module_build_dependencies(
            "testmodule", "master", "20180205135154", "9c690d0e").keys()

        expected_queries = [
            {
                "name": "testmodule",
                "stream": "master",
                "version": "20180205135154",
                "context": "9c690d0e",
                "verbose": True,
                "order_desc_by": "version",
                "page": 1,
                "per_page": 10,
                "state": "ready",
            },
            {
                "name": "platform",
                "stream": "f28",
                "version": "3",
                "context": "00000000",
                "verbose": True,
                "order_desc_by": "version",
                "page": 1,
                "per_page": 10,
                "state": "ready",
            },
        ]

        mbs_url = tests.conf.mbs_url
        expected_calls = [
            call(mbs_url, params=expected_queries[0]),
            call(mbs_url, params=expected_queries[1]),
        ]
        mock_session().get.mock_calls = expected_calls
        assert mock_session().get.call_count == 2
        assert set(result) == expected

    @patch("requests.Session")
    def test_get_module_build_dependencies_empty_buildrequires(
        self, mock_session, testmodule_mmd_9c690d0e
    ):

        mmd = module_build_service.utils.load_mmd(testmodule_mmd_9c690d0e)
        # Wipe out the dependencies
        for deps in mmd.get_dependencies():
            mmd.remove_dependencies(deps)
        xmd = mmd.get_xmd()
        xmd["mbs"]["buildrequires"] = {}
        mmd.set_xmd(xmd)

        mock_res = Mock()
        mock_res.ok.return_value = True
        mock_res.json.side_effect = [
            {
                "items": [
                    {
                        "name": "testmodule",
                        "stream": "master",
                        "version": "20180205135154",
                        "context": "9c690d0e",
                        "modulemd": mmd_to_str(mmd),
                        "build_deps": [],
                    }
                ],
                "meta": {"next": None},
            }
        ]

        mock_session().get.return_value = mock_res

        expected = set()

        resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="mbs")
        result = resolver.get_module_build_dependencies(
            "testmodule", "master", "20180205135154", "9c690d0e"
        ).keys()
        mbs_url = tests.conf.mbs_url
        expected_query = {
            "name": "testmodule",
            "stream": "master",
            "version": "20180205135154",
            "context": "9c690d0e",
            "verbose": True,
            "order_desc_by": "version",
            "page": 1,
            "per_page": 10,
            "state": "ready",
        }
        mock_session().get.assert_called_once_with(mbs_url, params=expected_query)
        assert set(result) == expected

    @patch("requests.Session")
    def test_resolve_profiles(self, mock_session, formatted_testmodule_mmd, platform_mmd):

        mock_res = Mock()
        mock_res.ok.return_value = True
        mock_res.json.return_value = {
            "items": [
                {
                    "name": "platform",
                    "stream": "f28",
                    "version": "3",
                    "context": "00000000",
                    "modulemd": platform_mmd,
                }
            ],
            "meta": {"next": None},
        }

        mock_session().get.return_value = mock_res
        resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="mbs")
        result = resolver.resolve_profiles(
            formatted_testmodule_mmd, ("buildroot", "srpm-buildroot")
        )
        expected = {
            "buildroot": set([
                "unzip",
                "tar",
                "cpio",
                "gawk",
                "gcc",
                "xz",
                "sed",
                "findutils",
                "util-linux",
                "bash",
                "info",
                "bzip2",
                "grep",
                "redhat-rpm-config",
                "fedora-release",
                "diffutils",
                "make",
                "patch",
                "shadow-utils",
                "coreutils",
                "which",
                "rpm-build",
                "gzip",
                "gcc-c++",
            ]),
            "srpm-buildroot": set([
                "shadow-utils",
                "redhat-rpm-config",
                "rpm-build",
                "fedora-release",
                "fedpkg-minimal",
                "gnupg2",
                "bash",
            ]),
        }

        mbs_url = tests.conf.mbs_url
        expected_query = {
            "name": "platform",
            "stream": "f28",
            "version": "3",
            "context": "00000000",
            "verbose": True,
            "order_desc_by": "version",
            "page": 1,
            "per_page": 10,
            "state": "ready",
        }

        mock_session().get.assert_called_once_with(mbs_url, params=expected_query)
        assert result == expected

    @patch(
        "module_build_service.config.Config.system", new_callable=PropertyMock, return_value="test"
    )
    @patch(
        "module_build_service.config.Config.mock_resultsdir",
        new_callable=PropertyMock,
        return_value=os.path.join(base_dir, "staged_data", "local_builds"),
    )
    def test_resolve_profiles_local_module(
        self, local_builds, conf_system, formatted_testmodule_mmd
    ):
        tests.clean_database()
        with tests.app.app_context():
            module_build_service.utils.load_local_builds(["platform"])

            resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="mbs")
            result = resolver.resolve_profiles(
                formatted_testmodule_mmd, ("buildroot", "srpm-buildroot"))
            expected = {"buildroot": set(["foo"]), "srpm-buildroot": set(["bar"])}
            assert result == expected

    def test_get_empty_buildrequired_modulemds(self):
        resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="mbs")

        with patch.object(resolver, "session") as session:
            session.get.return_value = Mock(ok=True)
            session.get.return_value.json.return_value = {"items": [], "meta": {"next": None}}

            result = resolver.get_buildrequired_modulemds("nodejs", "10", "platform:el8:1:00000000")
            assert [] == result

    def test_get_buildrequired_modulemds(self):
        resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="mbs")

        with patch.object(resolver, "session") as session:
            session.get.return_value = Mock(ok=True)
            session.get.return_value.json.return_value = {
                "items": [
                    {
                        "name": "nodejs",
                        "stream": "10",
                        "version": 1,
                        "context": "c1",
                        "modulemd": mmd_to_str(
                            tests.make_module("nodejs:10:1:c1", store_to_db=False),
                        ),
                    },
                    {
                        "name": "nodejs",
                        "stream": "10",
                        "version": 2,
                        "context": "c1",
                        "modulemd": mmd_to_str(
                            tests.make_module("nodejs:10:2:c1", store_to_db=False),
                        ),
                    },
                ],
                "meta": {"next": None},
            }

            result = resolver.get_buildrequired_modulemds("nodejs", "10", "platform:el8:1:00000000")

            assert 1 == len(result)
            mmd = result[0]
            assert "nodejs" == mmd.get_module_name()
            assert "10" == mmd.get_stream_name()
            assert 1 == mmd.get_version()
            assert "c1" == mmd.get_context()

    @patch("requests.Session")
    def test_get_module_count(self, mock_session):
        mock_res = Mock()
        mock_res.ok.return_value = True
        mock_res.json.return_value = {
            "items": [{"name": "platform", "stream": "f28", "version": "3", "context": "00000000"}],
            "meta": {"total": 5},
        }
        mock_session.return_value.get.return_value = mock_res

        resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="mbs")
        count = resolver.get_module_count(name="platform", stream="f28")

        assert count == 5
        mock_session.return_value.get.assert_called_once_with(
            "https://mbs.fedoraproject.org/module-build-service/1/module-builds/",
            params={"name": "platform", "page": 1, "per_page": 1, "short": True, "stream": "f28"},
        )

    @patch("requests.Session")
    def test_get_latest_with_virtual_stream(self, mock_session, platform_mmd):
        mock_res = Mock()
        mock_res.ok.return_value = True
        mock_res.json.return_value = {
            "items": [
                {
                    "context": "00000000",
                    "modulemd": platform_mmd,
                    "name": "platform",
                    "stream": "f28",
                    "version": "3",
                }
            ],
            "meta": {"total": 5},
        }
        mock_session.return_value.get.return_value = mock_res

        resolver = mbs_resolver.GenericResolver.create(tests.conf, backend="mbs")
        mmd = resolver.get_latest_with_virtual_stream("platform", "virtualf28")

        assert mmd.get_module_name() == "platform"
        mock_session.return_value.get.assert_called_once_with(
            "https://mbs.fedoraproject.org/module-build-service/1/module-builds/",
            params={
                "name": "platform",
                "order_desc_by": ["stream_version", "version"],
                "page": 1,
                "per_page": 1,
                "verbose": True,
                "virtual_stream": "virtualf28",
            },
        )
