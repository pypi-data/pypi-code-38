import io

from ioflow.corpus_processor.download_corpus_processor import (
    parse_corpus_to_offset,
    generator_fn
)


def test_parse_corpus_to_offset():
    test_input = {
        "id": "5d11c0344420bb1e20078fd9",
        "annotations": {
            "entity": [
                {
                    "start": "0",
                    "length": "3",
                    "type": "人名"
                },
                {
                    "start": "4",
                    "length": "3",
                    "type": "歌曲"
                }
            ]
        },
        "text": "周杰伦的七里香",
        "classifications": {
            "intent": "PLAY_SONG",
            "domain": "yyy"
        }
    }

    result = parse_corpus_to_offset(test_input)

    gold_result_str = "Sequence(text='周杰伦的七里香', span_set=SpanSet([Span(0, 3, '人名', value='周杰伦', normal_value=None), Span(4, 7, '歌曲', value='七里香', normal_value=None)]), id='5d11c0344420bb1e20078fd9', label='PLAY_SONG')"

    assert str(result) == gold_result_str


def test_generator_fn(mocker):
    gold_result = ['a', 'b', 'c']

    # mock open() learned from https://gist.github.com/ViktorovEugene/27d76ad2d94c88170d7b
    mocked_open = mocker.patch('builtins.open')
    mocked_open.return_value = io.StringIO('\n'.join(gold_result))

    mocked_json_loads = mocker.patch('json.loads')
    mocked_json_loads.side_effect = lambda x: x.strip()

    mocked_parse_corpus_to_offset = mocker.patch('ioflow.corpus_processor.download_corpus_processor.parse_corpus_to_offset')
    mocked_parse_corpus_to_offset.side_effect = lambda x: x

    result = generator_fn(None)

    assert list(result) == gold_result

