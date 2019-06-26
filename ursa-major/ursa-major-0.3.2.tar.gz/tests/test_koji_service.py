# -*- coding: utf-8 -*-
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
#
# Written by Chenxiong Qi <cqi@redhat.com>
#            Qixiang Wan <qwan@redhat.com>

import mock
import unittest

from ursa_major.koji_service import KojiService


class KojiServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.koji_profile = mock.Mock()
        with mock.patch('ursa_major.koji_service.koji') as koji:
            koji.krb_login = mock.Mock()
            koji.get_profile_module = mock.Mock(
                return_value=mock.Mock(
                    config=mock.Mock(
                        server='koji.example.com',
                        weburl='koji.example.com',
                        authtype='kerberos',
                        krb_rdns=False,
                        cert=''),
                )
            )
            self.koji_profile = koji.get_profile_module.return_value
            self.koji = KojiService('dummy-koji')
            self.koji.koji_proxy.logged_in = False

    def test_krb_login(self):
        self.koji.koji_module.config.keytab = 'testkeytab'
        self.koji.koji_module.config.principal = 'testprincipal'
        self.assertEqual(self.koji.koji_module.config.krb_rdns, False)
        self.koji.login()
        self.koji.koji_proxy.krb_login.assert_called_with('testprincipal',
                                                          'testkeytab')

    def test_get_inheritance_data(self):
        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(),
            getInheritanceData=mock.Mock(),
        )
        self.koji.get_inheritance_data(1)
        self.koji.koji_proxy.getInheritanceData.assert_called()
        self.koji.koji_proxy.getFullInheritance.assert_not_called()

    def test_get_full_inheritance_data(self):
        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(),
            getInheritanceData=mock.Mock(),
        )
        self.koji.get_inheritance_data(1, full=True)
        self.koji.koji_proxy.getInheritanceData.assert_not_called()
        self.koji.koji_proxy.getFullInheritance.assert_called()

    def test_find_build_tags_with_only_one_child(self):
        getTag_data = {
            'f28-build': {'name': 'f28-build', 'id': 3},
            'module-testmodule': {'name': 'module-testmodule', 'id': 13},
        }
        getBuildTargets_data = {
            3: [{'id': 100, 'name': 'f28-buildroot'}],
            13: [],
        }
        getFullInheritance_data = {
            3: [],
            13: [
                {'currdepth': 1,
                 'filter': [],
                 'intransitive': False,
                 'maxdepth': None,
                 'name': 'f28-build',
                 'nextdepth': None,
                 'noconfig': False,
                 'parent_id': 13,
                 'pkg_filter': '',
                 'priority': 60,
                 'tag_id': 3},
            ],
        }

        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(
                side_effect=lambda name: getTag_data.get(name)),
            getBuildTargets=mock.Mock(
                side_effect=lambda buildTagID: getBuildTargets_data.get(buildTagID)),
            getFullInheritance=mock.Mock(
                side_effect=lambda tag_id, reverse: getFullInheritance_data.get(tag_id)),
        )

        build_tags = self.koji.find_build_tags('module-testmodule')
        self.assertEqual(build_tags, ['f28-build'])

    def test_find_build_tags_with_none_result(self):
        getTag_data = {
            'f28-build': {'name': 'f28-build', 'id': 3},
            'module-testmodule': {'name': 'module-testmodule', 'id': 13},
        }
        getBuildTargets_data = {
            3: [],
            13: [],
        }
        getFullInheritance_data = {
            3: [],
            13: [
                {'currdepth': 1,
                 'filter': [],
                 'intransitive': False,
                 'maxdepth': None,
                 'name': 'f28-build',
                 'nextdepth': None,
                 'noconfig': False,
                 'parent_id': 13,
                 'pkg_filter': '',
                 'priority': 60,
                 'tag_id': 3},
            ],
        }

        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(
                side_effect=lambda name: getTag_data.get(name)),
            getBuildTargets=mock.Mock(
                side_effect=lambda buildTagID: getBuildTargets_data.get(buildTagID)),
            getFullInheritance=mock.Mock(
                side_effect=lambda tag_id, reverse: getFullInheritance_data.get(tag_id)),
        )

        build_tags = self.koji.find_build_tags('module-testmodule')
        self.assertEqual(build_tags, [])

    def test_find_build_tags_in_different_depths(self):
        getTag_data = {
            'f28-build': {'name': 'f28-build', 'id': 3},
            'f28-other-build': {'name': 'f28-other-build', 'id': 4},
            'f28-other-build2': {'name': 'f28-other-build2', 'id': 5},
            'f28-non-build': {'name': 'f28-non-build', 'id': 6},
            'f28-other-build3': {'name': 'f28-other-build3', 'id': 7},
            'module-testmodule': {'name': 'module-testmodule', 'id': 13},
        }
        getBuildTargets_data = {
            3: [{'id': 100, 'name': 'f28-buildroot'}],
            4: [{'id': 200, 'name': 'f28-other-buildroot'}],
            5: [{'id': 300, 'name': 'f28-other-buildroot2'}],
            6: [],
            7: [{'id': 400, 'name': 'f28-other-buildroot3'}],
            13: [],
        }
        getFullInheritance_data = {
            3: [],
            13: [
                {'currdepth': 1,
                 'filter': [],
                 'intransitive': False,
                 'maxdepth': None,
                 'name': 'f28-build',
                 'nextdepth': None,
                 'noconfig': False,
                 'parent_id': 13,
                 'pkg_filter': '',
                 'priority': 60,
                 'tag_id': 3},
                {'currdepth': 1,
                 'filter': [],
                 'intransitive': False,
                 'maxdepth': None,
                 'name': 'f28-other-build',
                 'nextdepth': None,
                 'noconfig': False,
                 'parent_id': 13,
                 'pkg_filter': '',
                 'priority': 80,
                 'tag_id': 4},
                {'currdepth': 1,
                 'filter': [],
                 'intransitive': False,
                 'maxdepth': None,
                 'name': 'f28-non-build',
                 'nextdepth': None,
                 'noconfig': False,
                 'parent_id': 13,
                 'pkg_filter': '',
                 'priority': 90,
                 'tag_id': 6},
                {'currdepth': 2,
                 'filter': [],
                 'intransitive': False,
                 'maxdepth': None,
                 'name': 'f28-other-build2',
                 'nextdepth': None,
                 'noconfig': False,
                 'parent_id': 4,
                 'pkg_filter': '',
                 'priority': 100,
                 'tag_id': 5},
                {'currdepth': 2,
                 'filter': [],
                 'intransitive': False,
                 'maxdepth': None,
                 'name': 'f28-other-build3',
                 'nextdepth': None,
                 'noconfig': False,
                 'parent_id': 6,
                 'pkg_filter': '',
                 'priority': 100,
                 'tag_id': 7},
            ],
        }

        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(
                side_effect=lambda name: getTag_data.get(name)),
            getBuildTargets=mock.Mock(
                side_effect=lambda buildTagID: getBuildTargets_data.get(buildTagID)),
            getFullInheritance=mock.Mock(
                side_effect=lambda tag_id, reverse: getFullInheritance_data.get(tag_id)),
        )

        build_tags = self.koji.find_build_tags('module-testmodule')
        self.assertEqual(build_tags, ['f28-build', 'f28-other-build', 'f28-other-build3'])

    def test_update_tag_inheritance_successfully(self):
        getTag_data = {
            'f27-build': {'name': 'f27-build', 'id': 3},
            'module-100': {'name': 'module-100', 'id': 13},
            'module-123': {'name': 'module-123', 'id': 1000},
        }
        inheritance_data = [{'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'f27-buildrequires',
                             'noconfig': False,
                             'parent_id': 4,
                             'pkg_filter': '',
                             'priority': 10},
                            {'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'f27-go-toolset-candidate',
                             'noconfig': False,
                             'parent_id': 12,
                             'pkg_filter': '',
                             'priority': 30},
                            {'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'module-100',
                             'noconfig': False,
                             'parent_id': 13,
                             'pkg_filter': '',
                             'priority': 40}]

        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(side_effect=lambda name: getTag_data.get(name)),
            getInheritanceData=mock.Mock(return_value=inheritance_data),
        )

        add_tags = [{'name': 'module-123', 'priority': 50}]
        remove_tags = [{'name': 'module-100'}]
        self.koji.update_tag_inheritance('f27-build', add_tags, remove_tags)
        module_123 = {'pkg_filter': False,
                      'intransitive': False,
                      'priority': 50,
                      'parent_id': 1000,
                      'maxdepth': None,
                      'noconfig': False}
        inheritance_data.append(module_123)
        inheritance_data[2]['delete link'] = True
        self.koji.koji_proxy.setInheritanceData.assert_called_with(
            3, inheritance_data)

    @mock.patch('ursa_major.koji_service.log')
    def test_update_tag_inheritance_with_same_priority(self, log):
        getTag_data = {
            'f27-build': {'name': 'f27-build', 'id': 3},
            'module-123': {'name': 'module-123', 'id': 1000},
        }
        inheritance_data = [{'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'f27-buildrequires',
                             'noconfig': False,
                             'parent_id': 4,
                             'pkg_filter': '',
                             'priority': 10},
                            {'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'f27-go-toolset-candidate',
                             'noconfig': False,
                             'parent_id': 12,
                             'pkg_filter': '',
                             'priority': 30}]

        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(side_effect=lambda name: getTag_data.get(name)),
            getInheritanceData=mock.Mock(return_value=inheritance_data),
        )

        add_tags = [{'name': 'module-123', 'priority': 30}]
        self.koji.update_tag_inheritance('f27-build', add_tags)

        log.warning.assert_called_with(
            ("Tag f27-build has an inheritance with the same priority 30 as "
             "tag module-123"))

        module_123 = {'pkg_filter': False,
                      'intransitive': False,
                      'priority': 50,
                      'parent_id': 1000,
                      'maxdepth': None,
                      'noconfig': False}
        inheritance_data.append(module_123)
        self.koji.koji_proxy.setInheritanceData.assert_called_with(
            3, inheritance_data)

    @mock.patch('ursa_major.koji_service.log')
    def test_update_tag_inheritance_with_same_tag_name(self, log):
        getTag_data = {
            'f27-build': {'name': 'f27-build', 'id': 3},
            'f27-buildrequires': {'name': 'f27-buildrequires', 'id': 4},
        }
        inheritance_data = [{'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'f27-buildrequires',
                             'noconfig': False,
                             'parent_id': 4,
                             'pkg_filter': '',
                             'priority': 10},
                            {'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'f27-go-toolset-candidate',
                             'noconfig': False,
                             'parent_id': 12,
                             'pkg_filter': '',
                             'priority': 30}]

        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(side_effect=lambda name: getTag_data.get(name)),
            getInheritanceData=mock.Mock(return_value=inheritance_data),
        )

        add_tags = [{'name': 'f27-buildrequires', 'priority': 50}]
        added_tags, removed_tags = self.koji.update_tag_inheritance('f27-build', add_tags)

        self.koji.koji_proxy.setInheritanceData.called_with(
            3,
            [
                {'intransitive': False,
                 'name': 'f27-buildrequires',
                 'pkg_filter': '',
                 'priority': 50,
                 'parent_id': 4,
                 'maxdepth': None,
                 'noconfig': False,
                 'child_id': 3},
                {'intransitive': False,
                 'parent_id': 12,
                 'maxdepth': None,
                 'noconfig': False,
                 'child_id': 3,
                 'pkg_filter': '',
                 'priority': 30,
                 'name': 'f27-go-toolset-candidate'}
            ]
        )
        self.assertEqual(added_tags, ['f27-buildrequires'])
        self.assertEqual(removed_tags, [])

    @mock.patch('ursa_major.koji_service.log')
    def test_update_tag_inheritance_with_removing_non_exist_tag(self, log):
        getTag_data = {
            'f27-build': {'name': 'f27-build', 'id': 3},
            'module-123': {'name': 'module-123', 'id': 1000},
        }
        inheritance_data = [{'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'f27-buildrequires',
                             'noconfig': False,
                             'parent_id': 4,
                             'pkg_filter': '',
                             'priority': 10},
                            {'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'f27-go-toolset-candidate',
                             'noconfig': False,
                             'parent_id': 12,
                             'pkg_filter': '',
                             'priority': 30}]

        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(side_effect=lambda name: getTag_data.get(name)),
            getInheritanceData=mock.Mock(return_value=inheritance_data),
        )

        add_tags = [{'name': 'module-123', 'priority': 50}]
        remove_tags = [{'name': 'non-exist-tag'}]

        with self.assertRaises(RuntimeError) as ctx:
            self.koji.update_tag_inheritance('f27-build', add_tags, remove_tags)

        self.assertIn("Tag non-exist-tag doesn't exist",
                      str(ctx.exception))
        self.koji.koji_proxy.setInheritanceData.assert_not_called()

    @mock.patch('ursa_major.koji_service.log')
    def test_update_tag_inheritance_with_removing_non_parent_tag(self, log):
        getTag_data = {
            'f27-build': {'name': 'f27-build', 'id': 3},
            'module-100': {'name': 'module-100', 'id': 13},
            'module-123': {'name': 'module-123', 'id': 1000},
        }
        inheritance_data = [{'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'f27-buildrequires',
                             'noconfig': False,
                             'parent_id': 4,
                             'pkg_filter': '',
                             'priority': 10},
                            {'child_id': 3,
                             'intransitive': False,
                             'maxdepth': None,
                             'name': 'f27-go-toolset-candidate',
                             'noconfig': False,
                             'parent_id': 12,
                             'pkg_filter': '',
                             'priority': 30}]

        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(side_effect=lambda name: getTag_data.get(name)),
            getInheritanceData=mock.Mock(return_value=inheritance_data),
        )

        add_tags = [{'name': 'module-123', 'priority': 50}]
        remove_tags = [{'name': 'module-100'}]

        with self.assertRaises(RuntimeError) as ctx:
            self.koji.update_tag_inheritance('f27-build', add_tags, remove_tags)

        self.assertIn("Tag module-100 not found in inheritance.",
                      str(ctx.exception))
        self.koji.koji_proxy.setInheritanceData.assert_not_called()

    @mock.patch('ursa_major.koji_service.wait_koji_task_finish')
    @mock.patch('ursa_major.koji_service.log')
    def test_regen_repo_without_wait_finish(self, log, wait_koji):
        getTag_data = {
            'rhel-8.0-build': {
                'name': 'rhel-8.0-build',
                'id': 100,
                'arches': [],
            },
        }

        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(side_effect=lambda name: getTag_data.get(name)),
            getBuildTargets=mock.Mock(return_value=[]),
            newRepo=mock.Mock(return_value=123),
        )

        self.koji.regen_repo('rhel-8.0-build', debuginfo=True, src=True)

        self.koji.koji_proxy.newRepo.assert_called_with(
            'rhel-8.0-build', debuginfo=True, src=True)
        log.warning.assert_has_calls(
            [mock.call('Warning: %s is not a build tag', 'rhel-8.0-build'),
             mock.call('Warning: tag %s has an empty arch list',
                       'rhel-8.0-build')],
            any_order=True)
        log.info.assert_has_calls(
            [mock.call('Regenerating repo for tag: %s', 'rhel-8.0-build'),
             mock.call('Created task: %d', 123),
             mock.call('Task info: %s',
                       'koji.example.com/taskinfo?taskID=123')],
            any_order=True)
        wait_koji.assert_not_called()

    @mock.patch('ursa_major.koji_service.log')
    def test_regen_repo_with_wait_finish(self, log):
        getTag_data = {
            'rhel-8.0-build': {
                'name': 'rhel-8.0-build',
                'id': 100,
                'arches': [],
            },
        }

        self.koji.koji_proxy = mock.Mock(
            getTag=mock.Mock(side_effect=lambda name: getTag_data.get(name)),
            getBuildTargets=mock.Mock(return_value=[]),
            newRepo=mock.Mock(return_value=123),
            getTaskInfo=mock.Mock(return_value={'state': 2}),
        )

        self.koji.regen_repo('rhel-8.0-build',
                             debuginfo=True, src=True, wait=True)

        self.koji.koji_proxy.newRepo.assert_called_with(
            'rhel-8.0-build', debuginfo=True, src=True)
        log.warning.assert_has_calls(
            [mock.call('Warning: %s is not a build tag', 'rhel-8.0-build'),
             mock.call('Warning: tag %s has an empty arch list',
                       'rhel-8.0-build')],
            any_order=True)
        self.koji.koji_proxy.getTaskInfo.called_with(123)
