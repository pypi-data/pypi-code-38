from __future__ import print_function
from __future__ import division

import os
import hashlib

import datetime
import pytest
from civis.compat import TemporaryDirectory
from .conftest import mock

from ..caching import FileIDCache


@pytest.mark.parametrize("day_offset", [20, 1])
@mock.patch('civiscompute.caching.civis.io')
@mock.patch('civiscompute.caching.civis.APIClient')
def test_cache(client_mock, civisio_mock, day_offset):
    """Make sure the file ID cache works."""

    with TemporaryDirectory() as dirname:
        test_name1 = os.path.join(dirname, 'test1.txt')
        with open(test_name1, 'w') as fp:
            fp.write('a')

        test_name2 = os.path.join(dirname, 'test2.txt')
        with open(test_name2, 'w') as fp:
            fp.write('b')

        exp_time = str(datetime.datetime.utcnow() +
                       datetime.timedelta(days=day_offset))
        exp_time30 = str(datetime.datetime.utcnow() +
                         datetime.timedelta(days=30))

        civisio_mock.file_to_civis.side_effect = [-1, -2, -3]
        client_mock().files.get.return_value = {'expires_at': exp_time}

        # Upload once.
        fc = FileIDCache(cache_file=os.path.join(dirname, 'cache.db'))
        fid = fc.get_fileid(test_name1)
        assert fid == -1, "File ID for cache insert is wrong!"
        client_mock().files.get.assert_called_with(-1)
        assert civisio_mock.file_to_civis.call_count == 1

        fid = fc.get_fileid(test_name2)
        assert fid == -2, "File ID for cache insert is wrong!"
        client_mock().files.get.assert_called_with(-2)
        assert civisio_mock.file_to_civis.call_count == 2

        # Get it back out.
        client_mock.reset_mock()
        if day_offset < 14:
            client_mock().files.get.return_value = {'expires_at': exp_time30}
        fid = fc.get_fileid(test_name1)

        # If it is going to expire, make sure we uploaded it again
        if day_offset >= 14:
            assert fid == -1, "File ID for cache get is wrong!"
            assert civisio_mock.file_to_civis.call_count == 2
            assert client_mock().files.get.call_count == 0
        else:
            assert fid == -3, "File ID for cache get is wrong!"
            assert civisio_mock.file_to_civis.call_count == 3
            client_mock().files.get.assert_called_with(-3)


@mock.patch('civiscompute.caching.civis.io')
@mock.patch('civiscompute.caching.civis.APIClient')
def test_cache_list(client_mock, civisio_mock, capsys):
    """Make sure the file ID cache listing works."""

    with TemporaryDirectory() as dirname:
        test_name1 = os.path.join(dirname, 'test1.txt')
        with open(test_name1, 'w') as fp:
            fp.write('a')
        hash_test_name = hashlib.md5('a'.encode('utf-8')).hexdigest()

        test_name2 = os.path.join(dirname, 'test2.txt')
        with open(test_name2, 'w') as fp:
            fp.write('b')
        hash_test_name2 = hashlib.md5('b'.encode('utf-8')).hexdigest()

        exp_time = str(datetime.datetime.utcnow() +
                       datetime.timedelta(days=15))

        civisio_mock.file_to_civis.side_effect = [-1, -2]
        client_mock().files.get.return_value = {'expires_at': exp_time}

        # Upload some files.
        fc = FileIDCache(cache_file=os.path.join(dirname, 'cache.db'))
        fc.get_fileid(test_name1)
        fc.get_fileid(test_name2)

        # List the cahce and make sure that looks OK.
        fc.list()
        out, err = capsys.readouterr()
        print(out)
        lines = out.split('\n')
        assert lines[0].strip() == \
            ("file id                   hash                             "
             "expiration date                  name"), (
             "File cache list header is wrong!")

        items = lines[1].strip().split()
        assert items[0] == str(-1), "file id is wrong for cache listing!"
        assert items[1] == hash_test_name, "hash is wrong for cache listing!"
        assert ' '.join(items[2:4]) == exp_time, (
            "expiration time is wrong for cache listing!")
        assert items[4] == test_name1, "name is wrong for cache listing!"

        items = lines[2].strip().split()
        assert items[0] == str(-2), "file id is wrong for cache listing!"
        assert items[1] == hash_test_name2, "hash is wrong for cache listing!"
        assert ' '.join(items[2:4]) == exp_time, (
            "expiration time is wrong for cache listing!")
        assert items[4] == test_name2, "name is wrong for cache listing!"
