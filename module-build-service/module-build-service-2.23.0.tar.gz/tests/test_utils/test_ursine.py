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
from mock import patch, Mock

from module_build_service import conf
from module_build_service.utils import ursine
from tests import make_module, clean_database


class TestFindModuleKojiTags:
    """Test ursine.find_module_koji_tags"""

    @patch.object(conf, "koji_tag_prefixes", new=["module"])
    def test_find_out_all_module_koji_tags(self):
        session = Mock()
        session.getFullInheritance.return_value = [
            {"name": "module-tag1-s-v-c"},
            {"name": "module-tag2-s-v-c"},
            {"name": "tag-1"},
        ]

        expected_tags = ["module-tag1-s-v-c", "module-tag2-s-v-c"]

        tags = ursine.find_module_koji_tags(session, "tag-a-build")
        assert expected_tags == tags

    @patch.object(conf, "koji_tag_prefixes", new=["module"])
    def test_return_empty_if_no_module_koji_tags(self):
        session = Mock()
        session.getFullInheritance.return_value = [{"name": "tag-1"}, {"name": "tag-2"}]

        tags = ursine.find_module_koji_tags(session, "tag-a-build")
        assert [] == tags


class TestFindUrsineRootTags:
    """Test ursine.find_build_tags_from_external_repos"""

    def setup_method(self):
        self.koji_session = Mock()
        self.koji_session.getTag.side_effect = \
            lambda name: None if name == "X-build" else {"name": name}

    def test_find_build_tags(self):
        with patch.object(
            conf, "koji_external_repo_url_prefix", new="http://example.com/brewroot/"
        ):
            tags = ursine.find_build_tags_from_external_repos(
                self.koji_session,
                [
                    {
                        "external_repo_name": "tag-1-external-repo",
                        "url": "http://example.com/brewroot/repos/tag-1-build/latest/$arch/",
                    },
                    {
                        "external_repo_name": "tag-2-external-repo",
                        "url": "http://example.com/brewroot/repos/tag-2-build/latest/$arch/",
                    },
                ],
            )

            assert ["tag-1-build", "tag-2-build"] == tags

    def test_return_emtpy_if_no_match_external_repo_url(self):
        with patch.object(
            conf, "koji_external_repo_url_prefix", new="http://example.com/brewroot/"
        ):
            tags = ursine.find_build_tags_from_external_repos(
                self.koji_session,
                [
                    {
                        "external_repo_name": "tag-1-external-repo",
                        "url": "https://another-site.org/repos/tag-1-build/latest/$arch/",
                    },
                    {
                        "external_repo_name": "tag-2-external-repo",
                        "url": "https://another-site.org/repos/tag-2-build/latest/$arch/",
                    },
                ],
            )

            assert [] == tags

    def test_some_tag_is_not_koji_tag(self):
        with patch.object(
            conf, "koji_external_repo_url_prefix", new="http://example.com/brewroot/"
        ):
            tags = ursine.find_build_tags_from_external_repos(
                self.koji_session,
                [
                    {
                        "external_repo_name": "tag-1-external-repo",
                        "url": "http://example.com/brewroot/repos/tag-1-build/latest/$arch/",
                    },
                    {
                        "external_repo_name": "tag-2-external-repo",
                        "url": "http://example.com/brewroot/repos/X-build/latest/$arch/",
                    },
                ],
            )

            assert ["tag-1-build"] == tags


class TestGetModulemdsFromUrsineContent:
    """Test ursine.get_modulemds_from_ursine_content"""

    def setup_method(self):
        clean_database(False)

    def teardown_method(self, test_method):
        clean_database()

    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_return_empty_if_no_ursine_build_tag_is_found(self, ClientSession):
        session = ClientSession.return_value

        # No module koji_tag in ursine content yet. This will result in empty
        # ursine modulemds is returned.
        session.getFullInheritance.return_value = [{"name": "tag-1.0-build"}]
        session.getExternalRepoList.return_value = [{
            "external_repo_name": "tag-1.0-external-repo",
            "url": "http://example.com/repos/tag-4-build/latest/$arch/",
        }]

        modulemds = ursine.get_modulemds_from_ursine_content("tag")
        assert [] == modulemds

    @patch.object(conf, "koji_tag_prefixes", new=["module"])
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_get_modulemds(self, ClientSession):
        session = ClientSession.return_value

        # Ensure to to get build tag for further query of ursine content.
        # For this test, the build tag is tag-4-build
        session.getExternalRepoList.return_value = [{
            "external_repo_name": "tag-1.0-external-repo",
            "url": "http://example.com/repos/tag-4-build/latest/$arch/",
        }]

        # Ensure to return module tags from ursine content of fake build tag
        # specified in above external repo's url.
        def mock_getFullInheritance(tag):
            if tag == "tag-4-build":
                return [
                    {"name": "tag-1.0-build"},
                    # Below two modules should be returned and whose modulemd
                    # should be also queried from database.
                    {"name": "module-name1-s-2020-c"},
                    {"name": "module-name2-s-2021-c"},
                ]
            raise ValueError("{} is not handled by test.".format(tag))

        session.getFullInheritance.side_effect = mock_getFullInheritance

        # Defaults to DB resolver, so create fake module builds and store them
        # into database to ensure they can be queried.
        mmd_name1s2020c = make_module(
            "name1:s:2020:c", xmd={"mbs": {"koji_tag": "module-name1-s-2020-c"}})
        mmd_name2s2021c = make_module(
            "name2:s:2021:c", xmd={"mbs": {"koji_tag": "module-name2-s-2021-c"}})

        koji_tag = "tag"  # It's ok to use arbitrary tag name.
        with patch.object(conf, "koji_external_repo_url_prefix", new="http://example.com/"):
            modulemds = ursine.get_modulemds_from_ursine_content(koji_tag)

        test_nsvcs = [item.get_nsvc() for item in modulemds]
        test_nsvcs.sort()

        expected_nsvcs = [mmd_name1s2020c.mmd().get_nsvc(), mmd_name2s2021c.mmd().get_nsvc()]
        expected_nsvcs.sort()

        session.getExternalRepoList.assert_called_once_with(koji_tag)
        assert expected_nsvcs == test_nsvcs


class TestRecordStreamCollisionModules:
    """Test ursine.record_stream_collision_modules"""

    @patch.object(conf, "base_module_names", new=["platform"])
    @patch.object(ursine, "find_stream_collision_modules")
    def test_nothing_changed_if_no_base_module_is_in_buildrequires(
        self, find_stream_collision_modules
    ):
        xmd = {"mbs": {"buildrequires": {"modulea": {"stream": "master"}}}}
        fake_mmd = make_module("name1:s:2020:c", xmd=xmd, store_to_db=False)
        original_xmd = fake_mmd.get_xmd()

        with patch.object(ursine, "log") as log:
            ursine.handle_stream_collision_modules(fake_mmd)
            assert 2 == log.info.call_count
            find_stream_collision_modules.assert_not_called()

        assert original_xmd == fake_mmd.get_xmd()

    @patch.object(conf, "base_module_names", new=["platform"])
    @patch("module_build_service.utils.ursine.get_modulemds_from_ursine_content")
    def test_mark_handled_even_if_no_modules_in_ursine_content(
        self, get_modulemds_from_ursine_content
    ):
        xmd = {
            "mbs": {
                "buildrequires": {
                    "modulea": {"stream": "master"},
                    "platform": {"stream": "master", "koji_tag": "module-rhel-8.0-build"},
                }
            }
        }
        fake_mmd = make_module("name1:s:2020:c", xmd=xmd, store_to_db=False)
        expected_xmd = fake_mmd.get_xmd()

        get_modulemds_from_ursine_content.return_value = []

        with patch.object(ursine, "log") as log:
            ursine.handle_stream_collision_modules(fake_mmd)
            assert 2 == log.info.call_count

        # Ensure stream_collision_modules is set.
        expected_xmd["mbs"]["buildrequires"]["platform"]["stream_collision_modules"] = ""
        expected_xmd["mbs"]["buildrequires"]["platform"]["ursine_rpms"] = ""
        assert expected_xmd == fake_mmd.get_xmd()

    @patch.object(conf, "base_module_names", new=["platform", "project-platform"])
    @patch("module_build_service.utils.ursine.get_modulemds_from_ursine_content")
    @patch("module_build_service.resolver.GenericResolver.create")
    @patch("module_build_service.builder.KojiModuleBuilder.KojiClientSession")
    def test_add_collision_modules(
        self, ClientSession, resolver_create, get_modulemds_from_ursine_content
    ):
        xmd = {
            "mbs": {
                "buildrequires": {
                    "modulea": {"stream": "master"},
                    "foo": {"stream": "1"},
                    "bar": {"stream": "2"},
                    "platform": {"stream": "master", "koji_tag": "module-rhel-8.0-build"},
                    "project-platform": {
                        "stream": "master",
                        "koji_tag": "module-project-1.0-build",
                    },
                }
            }
        }
        fake_mmd = make_module("name1:s:2020:c", xmd=xmd, store_to_db=False)

        def mock_get_ursine_modulemds(koji_tag):
            if koji_tag == "module-rhel-8.0-build":
                return [
                    # This is the one
                    make_module("modulea:10:20180813041838:5ea3b708", store_to_db=False),
                    make_module("moduleb:1.0:20180113042038:6ea3b105", store_to_db=False),
                ]
            if koji_tag == "module-project-1.0-build":
                return [
                    # Both of them are the collided modules
                    make_module("bar:6:20181013041838:817fa3a8", store_to_db=False),
                    make_module("foo:2:20180113041838:95f078a1", store_to_db=False),
                ]

        get_modulemds_from_ursine_content.side_effect = mock_get_ursine_modulemds

        # Mock for finding out built rpms
        def mock_get_module(name, stream, version, context, strict=True):
            return {
                "modulea:10:20180813041838:5ea3b708": {
                    "koji_tag": "module-modulea-10-20180813041838-5ea3b708"
                },
                "bar:6:20181013041838:817fa3a8": {
                    "koji_tag": "module-bar-6-20181013041838-817fa3a8"
                },
                "foo:2:20180113041838:95f078a1": {
                    "koji_tag": "module-foo-2-20180113041838-95f078a1"
                },
            }["{}:{}:{}:{}".format(name, stream, version, context)]

        resolver = resolver_create.return_value
        resolver._get_module.side_effect = mock_get_module

        def mock_listTaggedRPMS(tag, latest):
            return {
                "module-modulea-10-20180813041838-5ea3b708": [
                    [{"name": "pkg1", "version": "1.0", "release": "1.fc28", "epoch": None}]
                ],
                "module-bar-6-20181013041838-817fa3a8": [
                    [{"name": "pkg2", "version": "2.0", "release": "1.fc28", "epoch": None}]
                ],
                "module-foo-2-20180113041838-95f078a1": [
                    [{"name": "pkg3", "version": "3.0", "release": "1.fc28", "epoch": None}]
                ],
            }[tag]

        koji_session = ClientSession.return_value
        koji_session.listTaggedRPMS.side_effect = mock_listTaggedRPMS

        ursine.handle_stream_collision_modules(fake_mmd)

        xmd = fake_mmd.get_xmd()
        buildrequires = xmd["mbs"]["buildrequires"]

        modules = buildrequires["platform"]["stream_collision_modules"]
        assert ["modulea:10:20180813041838:5ea3b708"] == modules
        assert ["pkg1-0:1.0-1.fc28"] == buildrequires["platform"]["ursine_rpms"]

        modules = sorted(buildrequires["project-platform"]["stream_collision_modules"])
        expected_modules = ["bar:6:20181013041838:817fa3a8", "foo:2:20180113041838:95f078a1"]
        assert expected_modules == modules

        rpms = sorted(buildrequires["project-platform"]["ursine_rpms"])
        assert ["pkg2-0:2.0-1.fc28", "pkg3-0:3.0-1.fc28"] == rpms


class TestFindStreamCollisionModules:
    """Test ursine.find_stream_collision_modules"""

    @patch("module_build_service.utils.ursine.get_modulemds_from_ursine_content")
    def test_no_modulemds_found_from_ursine_content(self, get_modulemds_from_ursine_content):
        get_modulemds_from_ursine_content.return_value = []
        assert not ursine.find_stream_collision_modules({}, "koji_tag")

    @patch("module_build_service.utils.ursine.get_modulemds_from_ursine_content")
    def test_no_collisions_found(self, get_modulemds_from_ursine_content):
        xmd_mbs_buildrequires = {"modulea": {"stream": "master"}, "moduleb": {"stream": "10"}}
        get_modulemds_from_ursine_content.return_value = [
            make_module("moduler:1:1:c1", store_to_db=False),
            make_module("modules:2:1:c2", store_to_db=False),
            make_module("modulet:3:1:c3", store_to_db=False),
        ]
        assert [] == ursine.find_stream_collision_modules(xmd_mbs_buildrequires, "koji_tag")

    @patch("module_build_service.utils.ursine.get_modulemds_from_ursine_content")
    def test_collision_modules_are_found(self, get_modulemds_from_ursine_content):
        xmd_mbs_buildrequires = {"modulea": {"stream": "master"}, "moduleb": {"stream": "10"}}
        fake_modules = [
            make_module("moduler:1:1:c1", store_to_db=False),
            make_module("moduleb:6:1:c2", store_to_db=False),
            make_module("modulet:3:1:c3", store_to_db=False),
        ]
        get_modulemds_from_ursine_content.return_value = fake_modules

        modules = ursine.find_stream_collision_modules(xmd_mbs_buildrequires, "koji_tag")
        assert [fake_modules[1].get_nsvc()] == modules
