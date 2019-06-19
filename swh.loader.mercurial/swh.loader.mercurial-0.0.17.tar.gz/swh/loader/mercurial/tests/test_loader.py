# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os

from unittest.mock import patch

from swh.loader.core.tests import BaseLoaderTest
from swh.storage.algos.snapshot import snapshot_get_all_branches

from .common import HgLoaderMemoryStorage, HgArchiveLoaderMemoryStorage


class BaseHgLoaderTest(BaseLoaderTest):
    """Mixin base loader test to prepare the mercurial
       repository to uncompress, load and test the results.

       This sets up

    """
    def setUp(self, loader=HgLoaderMemoryStorage,
              archive_name='the-sandbox.tgz', filename='the-sandbox',
              uncompress_archive=True):
        super().setUp(archive_name=archive_name, filename=filename,
                      prefix_tmp_folder_name='swh.loader.mercurial.',
                      start_path=os.path.dirname(__file__),
                      uncompress_archive=uncompress_archive)
        self.loader = loader()
        self.storage = self.loader.storage


class WithoutReleaseLoaderTest(BaseHgLoaderTest):
    """Load a mercurial repository without release

    """
    def test_load(self):
        """Load a repository with multiple branches results in 1 snapshot

        """
        # when
        self.loader.load(
            origin_url=self.repo_url,
            visit_date='2016-05-03 15:16:32+00',
            directory=self.destination_path)

        # then
        self.assertCountContents(2)
        self.assertCountDirectories(3)
        self.assertCountReleases(0)
        self.assertCountRevisions(58)

        tip_revision_develop = 'a9c4534552df370f43f0ef97146f393ef2f2a08c'
        tip_revision_default = '70e750bb046101fdced06f428e73fee471509c56'
        # same from rev 3 onward
        directory_hash = '180bd57623a7c2c47a8c43514a5f4d903503d0aa'
        # cf. test_loader.org for explaining from where those hashes
        # come from
        expected_revisions = {
            # revision hash | directory hash  # noqa
            'aafb69fd7496ca617f741d38c40808ff2382aabe': 'e2e117569b086ceabeeedee4acd95f35298d4553',  # noqa
            'b6932cb7f59e746899e4804f3d496126d1343615': '9cd8160c67ac4b0bc97e2e2cd918a580425167d3',  # noqa
            tip_revision_default: directory_hash,
            '18012a93d5aadc331c468dac84b524430f4abc19': directory_hash,
            'bec4c0a31b0b2502f44f34aeb9827cd090cca621': directory_hash,
            '5f4eba626c3f826820c4475d2d81410759ec911b': directory_hash,
            'dcba06661c607fe55ec67b1712d153b69f65e38c': directory_hash,
            'c77e776d22548d47a8d96463a3556172776cd59b': directory_hash,
            '61d762d65afb3150e2653d6735068241779c1fcf': directory_hash,
            '40def747398c76ceec1bd248e3a6cb2a52e22dc5': directory_hash,
            '6910964416438ca8d1698f6295871d727c4d4851': directory_hash,
            'be44d5e6cc66580f59c108f8bff5911ee91a22e4': directory_hash,
            'c4a95d5097519dedac437fddf0ef775136081241': directory_hash,
            '32eb0354a660128e205bf7c3a84b46040ef70d92': directory_hash,
            'dafa445964230e808148db043c126063ea1dc9b6': directory_hash,
            'a41e2a548ba51ee47f22baad8e88994853d3e2f5': directory_hash,
            'dc3e3ab7fe257d04769528e5e17ad9f1acb44659': directory_hash,
            'd2164061453ecb03d4347a05a77db83f706b8e15': directory_hash,
            '34192ceef239b8b72141efcc58b1d7f1676a18c9': directory_hash,
            '2652147529269778757d96e09aaf081695548218': directory_hash,
            '4d640e8064fe69b4c851dfd43915c431e80c7497': directory_hash,
            'c313df50bfcaa773dcbe038d00f8bd770ba997f8': directory_hash,
            '769db00b34b9e085dc699c8f1550c95793d0e904': directory_hash,
            '2973e5dc9568ac491b198f6b7f10c44ddc04e0a3': directory_hash,
            'be34b8c7857a6c04e41cc06b26338d8e59cb2601': directory_hash,
            '24f45e41637240b7f9e16d2791b5eacb4a406d0f': directory_hash,
            '62ff4741eac1821190f6c2cdab7c8a9d7db64ad0': directory_hash,
            'c346f6ff7f42f2a8ff867f92ab83a6721057d86c': directory_hash,
            'f2afbb94b319ef5d60823859875284afb95dcc18': directory_hash,
            '4e2dc6d6073f0b6d348f84ded52f9143b10344b9': directory_hash,
            '31cd7c5f669868651c57e3a2ba25ac45f76fa5cf': directory_hash,
            '25f5b27dfa5ed15d336188ef46bef743d88327d4': directory_hash,
            '88b80615ed8561be74a700b92883ec0374ddacb0': directory_hash,
            '5ee9ea92ed8cc1737b7670e39dab6081c64f2598': directory_hash,
            'dcddcc32740d2de0e1403e21a5c4ed837b352992': directory_hash,
            '74335db9f45a5d1c8133ff7a7db5ed7a8d4a197b': directory_hash,
            'cb36b894129ca7910bb81c457c72d69d5ff111bc': directory_hash,
            'caef0cb155eb6c55215aa59aabe04a9c702bbe6a': directory_hash,
            '5017ce0b285351da09a2029ea2cf544f79b593c7': directory_hash,
            '17a62618eb6e91a1d5d8e1246ccedae020d3b222': directory_hash,
            'a1f000fb8216838aa2a120738cc6c7fef2d1b4d8': directory_hash,
            '9f82d95bd3edfb7f18b1a21d6171170395ea44ce': directory_hash,
            'a701d39a17a9f48c61a06eee08bd9ac0b8e3838b': directory_hash,
            '4ef794980f820d44be94b2f0d53eb34d4241638c': directory_hash,
            'ddecbc16f4c916c39eacfcb2302e15a9e70a231e': directory_hash,
            '3565e7d385af0745ec208d719e469c2f58be8e94': directory_hash,
            'c875bad563a73a25c5f3379828b161b1441a7c5d': directory_hash,
            '94be9abcf9558213ff301af0ecd8223451ce991d': directory_hash,
            '1ee770fd10ea2d8c4f6e68a1dbe79378a86611e0': directory_hash,
            '553b09724bd30d9691b290e157b27a73e2d3e537': directory_hash,
            '9e912851eb64e3a1e08fbb587de7a4c897ce5a0a': directory_hash,
            '9c9e0ff08f215a5a5845ce3dbfc5b48c8050bdaf': directory_hash,
            'db9e625ba90056304897a94c92e5d27bc60f112d': directory_hash,
            '2d4a801c9a9645fcd3a9f4c06418d8393206b1f3': directory_hash,
            'e874cd5967efb1f45282e9f5ce87cc68a898a6d0': directory_hash,
            'e326a7bbb5bc00f1d8cacd6108869dedef15569c': directory_hash,
            '3ed4b85d30401fe32ae3b1d650f215a588293a9e': directory_hash,
            tip_revision_develop: directory_hash,
        }

        self.assertRevisionsContain(expected_revisions)
        self.assertCountSnapshots(1)

        expected_snapshot = {
            'id': '3b8fe58e467deb7597b12a5fd3b2c096b8c02028',
            'branches': {
                'develop': {
                    'target': tip_revision_develop,
                    'target_type': 'revision'
                },
                'default': {
                    'target': tip_revision_default,
                    'target_type': 'revision'
                },
                'HEAD': {
                    'target': 'develop',
                    'target_type': 'alias',
                }
            }
        }

        self.assertSnapshotEqual(expected_snapshot)
        self.assertEqual(self.loader.load_status(), {'status': 'eventful'})
        self.assertEqual(self.loader.visit_status(), 'full')


class CommonHgLoaderData:
    def assert_data_ok(self):
        # then
        self.assertCountContents(3)
        self.assertCountDirectories(3)
        self.assertCountReleases(1)
        self.assertCountRevisions(3)

        tip_release = '515c4d72e089404356d0f4b39d60f948b8999140'
        self.assertReleasesContain([tip_release])

        tip_revision_default = 'c3dbe4fbeaaa98dd961834e4007edb3efb0e2a27'
        # cf. test_loader.org for explaining from where those hashes
        # come from
        expected_revisions = {
            # revision hash | directory hash  # noqa
            '93b48d515580522a05f389bec93227fc8e43d940': '43d727f2f3f2f7cb3b098ddad1d7038464a4cee2',  # noqa
            '8dd3db5d5519e4947f035d141581d304565372d2': 'b3f85f210ff86d334575f64cb01c5bf49895b63e',  # noqa
            tip_revision_default: '8f2be433c945384c85920a8e60f2a68d2c0f20fb',
        }

        self.assertRevisionsContain(expected_revisions)
        self.assertCountSnapshots(1)

        expected_snapshot = {
            'id': 'd35668e02e2ba4321dc951cd308cf883786f918a',
            'branches': {
                'default': {
                    'target': tip_revision_default,
                    'target_type': 'revision'
                },
                '0.1': {
                    'target': tip_release,
                    'target_type': 'release'
                },
                'HEAD': {
                    'target': 'default',
                    'target_type': 'alias',
                }
            }
        }

        self.assertSnapshotEqual(expected_snapshot)
        self.assertEqual(self.loader.load_status(), {'status': 'eventful'})
        self.assertEqual(self.loader.visit_status(), 'full')


class WithReleaseLoaderTest(BaseHgLoaderTest, CommonHgLoaderData):
    """Load a mercurial repository with release

    """
    def setUp(self):
        super().setUp(archive_name='hello.tgz', filename='hello')

    def test_load(self):
        """Load a repository with tags results in 1 snapshot

        """
        # when
        self.loader.load(
            origin_url=self.repo_url,
            visit_date='2016-05-03 15:16:32+00',
            directory=self.destination_path)

        self.assert_data_ok()


class ArchiveLoaderTest(BaseHgLoaderTest, CommonHgLoaderData):
    """Load a mercurial repository archive with release

    """
    def setUp(self):
        super().setUp(loader=HgArchiveLoaderMemoryStorage,
                      archive_name='hello.tgz', filename='hello',
                      uncompress_archive=False)

    def test_load(self):
        """Load a mercurial repository archive with tags results in 1 snapshot

        """
        # when
        self.loader.load(
            origin_url=self.repo_url,
            visit_date='2016-05-03 15:16:32+00',
            archive_path=self.destination_path)

        self.assert_data_ok()

    @patch('swh.loader.mercurial.archive_extract.patoolib')
    def test_load_with_failure(self, mock_patoo):
        mock_patoo.side_effect = ValueError

        # when
        r = self.loader.load(
            origin_url=self.repo_url,
            visit_date='2016-05-03 15:16:32+00',
            archive_path=self.destination_path)

        self.assertEqual(r, {'status': 'failed'})
        self.assertCountContents(0)
        self.assertCountDirectories(0)
        self.assertCountRevisions(0)
        self.assertCountReleases(0)
        self.assertCountSnapshots(0)


class WithTransplantLoaderTest(BaseHgLoaderTest):
    """Load a mercurial repository where transplant operations
    have been used.

    """
    def setUp(self):
        super().setUp(archive_name='transplant.tgz', filename='transplant')

    def test_load(self):
        # load hg repository
        self.loader.load(
            origin_url=self.repo_url,
            visit_date='2019-05-23 12:06:00+00',
            directory=self.destination_path)

        # collect swh revisions
        origin_url = self.storage.origin_get([
            {'type': 'hg', 'url': self.repo_url}])[0]['url']
        visit = self.storage.origin_visit_get_latest(
            origin_url, require_snapshot=True)
        revisions = []
        snapshot = snapshot_get_all_branches(self.storage, visit['snapshot'])
        for branch in snapshot['branches'].values():
            if branch['target_type'] != 'revision':
                continue
            revisions.append(branch['target'])

        # extract original changesets info and the transplant sources
        hg_changesets = set()
        transplant_sources = set()
        for rev in self.storage.revision_log(revisions):
            hg_changesets.add(rev['metadata']['node'])
            for k, v in rev['metadata']['extra_headers']:
                if k == 'transplant_source':
                    transplant_sources.add(v)

        # check extracted data are valid
        self.assertTrue(len(hg_changesets) > 0)
        self.assertTrue(len(transplant_sources) > 0)
        self.assertTrue(transplant_sources.issubset(hg_changesets))
