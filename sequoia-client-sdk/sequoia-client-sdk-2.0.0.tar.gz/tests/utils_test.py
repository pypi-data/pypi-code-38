import json

from hamcrest import assert_that, equal_to

from sequoia import util


def test_wrap():
    result = util.wrap(json.dumps(mock_json), 'flow-instance')

    assert_that(json.loads(result)['flowInstance'], equal_to(mock_json))


def test_unwrap():
    result = util.unwrap({'flowInstance': mock_json}, 'flow-instance')

    assert_that(result, equal_to(mock_json))


mock_json = {'ref': 'aRef',
             'name': 'aName'}
