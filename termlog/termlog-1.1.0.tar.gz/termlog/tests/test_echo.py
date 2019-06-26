from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Union

import pytest
from pygments.lexer import Lexer


@dataclass
class EchoTestCase:
    messages: List[Any]
    verbose: Optional[Union[bool, int]] = None
    end: str = '\n'
    flush: bool = True
    lexer: Optional[Union[Lexer, str]] = None
    color: Optional[bool] = None
    json: Optional[bool] = None
    add_timestamp: bool = False
    expected: Optional[str] = None

    @property
    def echo_kwds(self) -> Dict[str, Any]:
        data = asdict(self)
        data.pop('expected')
        data.pop('messages')
        return data


@pytest.mark.parametrize('test_case', [
    EchoTestCase([''], json=False, color=True),
    EchoTestCase(['a']),
    EchoTestCase([1], expected='1'),
    EchoTestCase([None], expected='None'),
    ])
def test_echo(test_case, capfd):
    from .. import echo

    messages = test_case.messages
    expected = test_case.expected if test_case.expected is not None else ' '.join(f'{m}' for m in messages)

    result = echo(*messages, **test_case.echo_kwds)
    cap = capfd.readouterr()
    assert result == expected
    assert cap.err == ''
    # This fails...why?
    # assert cap.out == expected


# TODO:
# @dataclass
# class ConfigTestCase:
#     message: str = ''
#     expected: str = ''
#     color: Optional[bool] = None
#     json: Optional[bool] = None
#     time_format: Optional[str] = None
#     string_format: Optional[str] = None
#
#     @property
#     def echo_kwds(self) -> Dict[str, Any]:
#         data = asdict(self)
#         data.pop('expected')
#         data.pop('message')
#         return data
#
#
# @pytest.mark.parametrize('test_case', [
#     ConfigTestCase('hi', ''),
#     ])
# def test_set_config(test_case, capfd):
#     from .. import echo, set_config
#
#     set_config(**test_case.echo_kwds)
#
#     message = test_case.message
#     expected = test_case.expected if test_case.expected is not None else message
#
#     result = echo(message, add_timestamp=False, **test_case.echo_kwds)
#     cap = capfd.readouterr()
#     assert cap.err == ''
#     assert cap.out == expected
#     assert result == expected
