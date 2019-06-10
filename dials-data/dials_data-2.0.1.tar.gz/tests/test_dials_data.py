# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import dials_data
import dials_data.datasets
import dials_data.download
import mock


def test_all_datasets_can_be_parsed():
    assert dials_data.datasets.definition


def test_repository_location():
    rl = dials_data.datasets.repository_location()
    assert rl.check(dir=1)


def test_fetching_undefined_datasets_does_not_crash():
    df = dials_data.download.DataFetcher(read_only=True)
    assert df("aardvark") is False


def test_requests_for_future_datasets_can_be_intercepted():
    df = dials_data.download.DataFetcher(read_only=True)
    df.result_filter = mock.Mock()
    df.result_filter.return_value = False
    assert df("aardvark") is False
    df.result_filter.assert_called_once_with(result=False)
