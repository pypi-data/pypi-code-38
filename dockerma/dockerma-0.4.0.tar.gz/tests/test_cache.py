#!/usr/bin/env python
# -*- coding: utf-8
from datetime import timedelta

import mock
import pytest
import time

from dockerma.cache import FileCache, Entry

TEST_KEY = "test-key"
TEST_DATA = "test-data"
TEST_ENTRY_PATH = "test-entry-path"


class TestCache(object):
    @pytest.fixture
    def cache(self, request):
        yield FileCache(request.node.nodeid)

    @pytest.fixture
    def mock_os(self):
        with mock.patch("dockerma.cache.os") as m:
            yield m

    @pytest.fixture
    def load_entry_data(self):
        with mock.patch("dockerma.cache.open", mock.mock_open()) as _, \
                mock.patch("dockerma.cache.pickle.load") as mock_load:
            yield mock_load

    @pytest.fixture
    def save_entry_data(self):
        with mock.patch("dockerma.cache.open", mock.mock_open()) as mock_open, \
                mock.patch("dockerma.cache.pickle.dump") as mock_dump:
            yield mock_open, mock_dump

    @pytest.fixture(autouse=True)
    def get_entry_path(self, cache):
        with mock.patch.object(cache, "_get_entry_path") as m:
            m.return_value = TEST_ENTRY_PATH
            yield m

    def test_delete(self, cache, mock_os):
        mock_os.path.exists.return_value = True

        cache.delete(TEST_KEY)

        mock_os.unlink.assert_called_once_with(TEST_ENTRY_PATH)

    def test_get(self, cache, mock_os, load_entry_data):
        mock_os.path.exists.return_value = True
        load_entry_data.return_value = Entry(0, TEST_DATA)

        value = cache.get(TEST_KEY)

        assert value == TEST_DATA

    @pytest.mark.usefixtures("mock_os")
    def test_set(self, cache, save_entry_data):
        mock_open, mock_dump = save_entry_data
        cache.set(TEST_KEY, TEST_DATA)

        mock_dump.assert_called_with(Entry(mock.ANY, TEST_DATA), mock.ANY)
        mock_open.assert_called_with(TEST_ENTRY_PATH, "wb")

    def test_clean_expired(self, cache, mock_os):
        mock_os.walk.return_value = [("/root", [], ["too_old", "fresh"])]
        mock_os.path.join.side_effect = lambda *args: args[-1]

        cache._get_entry = mock.MagicMock()
        cache._delete_entry = mock.MagicMock()

        def entries(path):
            if path == "too_old":
                return Entry(time.time() - timedelta(days=1).total_seconds(), TEST_DATA)
            else:
                return Entry(time.time() + timedelta(days=1).total_seconds(), TEST_DATA)
        cache._get_entry.side_effect = entries

        cache.clean_expired()

        assert cache._delete_entry.call_args_list == [mock.call("too_old")]
