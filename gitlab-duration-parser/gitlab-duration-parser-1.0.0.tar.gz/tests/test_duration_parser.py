import pytest

from gitlab_duration_parser import parse


@pytest.mark.parametrize(('message', 'expected_duration'), [
    ('added 1mo 2w 3d 4h 5m 6s of time', 965106),
    ('added 1mo 4h of time', 590400),
    ('added 2d 3h of time', 68400),
    ('added 6s of time', 6),
    ('subtracted 1h 6s of time', -3606),
    ('subtracted 4h 30m of time', -16200),
    ('This is not a time-tracking message', 0),
])
def test_duration_parser(message, expected_duration):
    assert parse(message) == expected_duration
