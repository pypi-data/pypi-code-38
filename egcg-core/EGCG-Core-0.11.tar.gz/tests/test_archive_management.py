import os
from unittest.mock import patch
from egcg_core import archive_management as am
from tests import TestEGCG


class TestArchiveManagement(TestEGCG):
    @patch('egcg_core.archive_management._get_stdout')
    def test_archive_states(self, mocked_stdout):

        mocked_stdout.return_value = 'testfile: (0x0000000d) released exists archived, archive_id:1'
        assert am.archive_states('testfile') == ['released', 'exists', 'archived']

        mocked_stdout.return_value = 'testfile: (0x00000009) exists archived, archive_id:1'
        assert am.archive_states('testfile') == ['exists', 'archived']

        mocked_stdout.return_value = 'testfile: (0x00000001) exists, archive_id:1'
        assert am.archive_states('testfile') == ['exists']

        mocked_stdout.return_value = 'testfile: (0x00000000)'
        assert am.archive_states('testfile') == []

        mocked_stdout.return_value = 'some invalid stdout'
        with self.assertRaises(am.ArchivingError) as c:
            am.archive_states('testfile')
        assert str(c.exception) == 'Could not hsm_state file testfile'

    @patch('egcg_core.archive_management._get_stdout')
    def test_release_file_from_lustre(self, mocked_stdout):
        mocked_stdout.side_effect = [
            'testfile: (0x00000009) exists archived, archive_id:1',
            '',
            'testfile: (0x0000000d) released exists archived, archive_id:1'
        ]
        assert am.release_file_from_lustre('testfile')
        assert mocked_stdout.call_count == 3
        assert mocked_stdout.call_args_list[1][0] == ('lfs hsm_release testfile',)
        mocked_stdout.reset_mock()

        mocked_stdout.side_effect = ['testfile: (0x0000000d) released exists archived, archive_id:1']
        assert am.release_file_from_lustre('testfile')
        assert mocked_stdout.call_count == 1
        mocked_stdout.reset_mock()

        mocked_stdout.side_effect = ['testfile: (0x00000009) exists, archive_id:1']
        with self.assertRaises(am.ArchivingError) as c:
            am.release_file_from_lustre('testfile')
        assert mocked_stdout.call_count == 1
        assert str(c.exception) == 'Cannot release testfile from Lustre because it is not archived to tape'

    @patch('egcg_core.archive_management._get_stdout')
    def test_register_for_archiving(self, mocked_stdout):
        mocked_stdout.side_effect = ['testfile: (0x00000001)', '', 'testfile: (0x00000009) exists, archive_id:1']
        assert am.register_for_archiving('testfile')
        assert mocked_stdout.call_count == 3
        assert mocked_stdout.call_args_list[1][0] == ('lfs hsm_archive testfile',)
        mocked_stdout.reset_mock()

        mocked_stdout.side_effect = ['testfile: (0x00000001) exists, archive_id:1']
        assert am.register_for_archiving('testfile')
        assert mocked_stdout.call_count == 1
        mocked_stdout.reset_mock()

        mocked_stdout.side_effect = [
            'testfile: (0x00000001)', '', 'testfile: (0x00000001)', 'testfile: (0x00000001)', None
        ]
        with self.assertRaises(am.ArchivingError) as c:
            am.register_for_archiving('testfile')
        assert mocked_stdout.call_count == 5
        assert mocked_stdout.call_args_list[1][0] == ('lfs hsm_archive testfile',)
        assert str(c.exception) == 'Registering testfile for archiving to tape failed'

    @patch('egcg_core.archive_management._get_stdout')
    def test_recall_from_tape(self, mocked_stdout):
        mocked_stdout.side_effect = ['testfile: (0x0000000d) released exists archived, archive_id:1', '']
        assert am.recall_from_tape('testfile')
        assert mocked_stdout.call_count == 2
        assert mocked_stdout.call_args_list[1][0] == ('lfs hsm_restore testfile',)

    @patch('egcg_core.archive_management.register_for_archiving')
    def test_archive_directory(self, mocked_register):
        assert am.archive_directory(os.path.join(self.assets_path, 'fastqs'))
        assert mocked_register.call_count == 6
