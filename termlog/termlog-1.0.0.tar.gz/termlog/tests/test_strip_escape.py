from dataclasses import dataclass

import pytest


@dataclass
class StripEscapeData:
    input: str = ''
    output: str = ''


@pytest.mark.parametrize('test_data', [
    StripEscapeData('\x1b[31ma\x1b[0m', 'a'),
    StripEscapeData('b', 'b'),
    StripEscapeData('\033[32mc\033[0m', 'c'),
    StripEscapeData('', ''),
    StripEscapeData('\033[33m\033[0m', ''),
    StripEscapeData('\x1b[38;5;245ma\x1b[39m', 'a'),
    StripEscapeData(
        input='''{"data": "available=\u001b[31mNone\u001b[0m download=\u001b[35mNone\u001b[0m clean=\u001b[33mNone\u001b[0m verbose=\u001b[32m1\u001b[0m", "timestamp": "2019-02-22 22:57:04.459103", "available": null, "download": null, "clean": null, "verbose": 1}''',
        output='''{"data": "available=None download=None clean=None verbose=1", "timestamp": "2019-02-22 22:57:04.459103", "available": null, "download": null, "clean": null, "verbose": 1}''',
        ),
    StripEscapeData(
        input='''{"data": "Remote: \u001b[32mrecommendations/audience_similarity/v4/panel=aus/external/start_yyyymmdd=20150801/end_yyyymmdd=20181129/series_map_yyyymmdd=20181129/_SUCCESS\u001b[0m", "timestamp": "2019-02-25 19:46:46.988875"}''',
        output='''{"data": "Remote: recommendations/audience_similarity/v4/panel=aus/external/start_yyyymmdd=20150801/end_yyyymmdd=20181129/series_map_yyyymmdd=20181129/_SUCCESS", "timestamp": "2019-02-25 19:46:46.988875"}''',
        )
    ])
def test_strip_escape(test_data):
    from ..message import strip_escape

    value = strip_escape(test_data.input)
    assert value == test_data.output
