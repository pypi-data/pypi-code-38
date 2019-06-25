import os
from tempfile import NamedTemporaryFile

import pytest


def test_write_no_story(cli):
    c = cli('write')
    assert c.return_code == 1
    assert 'Please specify a template' in c.out


story_params = (
    'story,expected',
    [
        ('http', 'http'),
        ('function', 'function'),
        ('if', 'if'),
        ('loop', 'for'),
    ],
)


@pytest.mark.parametrize(*story_params)
def test_write_specified_story(cli, story, expected):
    # Test bare argument.
    c = cli('write', story)
    assert expected in c.out
    assert c.return_code == 0


@pytest.mark.parametrize(*story_params)
def test_write_specified_story_with_path(cli, story, expected):
    tf = NamedTemporaryFile()

    c = cli('write', story, tf.name)
    assert expected in c.out
    assert c.return_code == 0

    # Cleanup the temporary files.
    os.remove(tf.name)


def test_help(cli):
    # Test bare argument.
    c = cli('--help')
    assert 'Commands' in c.out
    assert c.return_code == 0


@pytest.mark.skip
def test_completion(cli):
    c = cli('completion')
    assert 'complete' in c.out


def test_support(cli):
    c = cli('--support')
    assert 'argv' in c.out
