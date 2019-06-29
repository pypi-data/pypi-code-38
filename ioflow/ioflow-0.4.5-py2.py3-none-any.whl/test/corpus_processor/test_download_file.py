import io
import os

from ioflow.corpus_processor.download_file import download_file

import requests_mock


def test_download_file():
    with requests_mock.Mocker() as mocker:
        gold_result = os.urandom(1024)
        mocker.register_uri(requests_mock.ANY, requests_mock.ANY, body=io.BytesIO(gold_result))
        result = download_file("http://some.url")

        with open(result, 'rb') as fd:
            assert fd.read() == gold_result
