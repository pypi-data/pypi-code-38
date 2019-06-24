# -*- coding: UTF-8 -*-
import tempfile
import pytest
from pysenal.io.file import *
from tests import TEST_DATA_DIR


@pytest.fixture("module")
def example_lines():
    lines = ['This is an example.   ',
             'This is a different example.',
             '',
             '    Hahaha.']
    return lines


@pytest.fixture("module")
def example_json():
    data = [
        {
            "text": "This is an example.",
            "start": 0,
            "end": 19
        },
        {"text": "This is another example.",
         "start": 0,
         "end": 24
         }
    ]
    return data


@pytest.fixture("module")
def fake_filename():
    filename = 'aaaaa.txt'
    if os.path.exists(filename):
        os.remove(filename)
    return filename


def test_read_lines(example_lines, fake_filename):
    filename = TEST_DATA_DIR + 'a.txt'
    lines = read_lines(filename)
    assert lines == example_lines
    skip_lines = read_lines(filename, skip_empty=True)
    assert skip_lines == [l for l in example_lines if l]
    assert read_lines(TEST_DATA_DIR + 'a.txt.gbk', 'gbk') == ['你好', '这是一个例子。']
    assert read_lines(fake_filename, default=[]) == []
    with pytest.raises(FileNotFoundError):
        read_lines(fake_filename)


def test_read(example_lines, fake_filename):
    filename = TEST_DATA_DIR + 'a.txt'
    text = read_file(filename)
    true_text = '\n'.join(example_lines)
    assert text == true_text

    assert read_file(fake_filename, default='') == ''
    with pytest.raises(FileNotFoundError):
        read_file(fake_filename)


def test_read_json():
    read_json(TEST_DATA_DIR + 'a.json')


def test_read_jsonline(example_json, fake_filename):
    assert read_jsonline(TEST_DATA_DIR + 'a.jsonl') == example_json


def test_write_lines(example_lines):
    dirname = tempfile.gettempdir() + '/'
    filename = dirname + 'a.txt'
    if os.path.exists(filename):
        os.remove(filename)

    write_lines(filename, example_lines)
    with open(filename) as f:
        assert f.read().splitlines() == example_lines

    if os.path.exists(filename):
        os.remove(filename)


def test_text_file(example_lines):
    true_text = '\n'.join(example_lines)
    text_file = TextFile(TEST_DATA_DIR + 'a.txt')
    text = text_file.read()
    lines = text_file.read_lines()
    assert text == true_text
    assert lines == example_lines
    expected_write_text = 'New Example\n\n'
    text_file.write(expected_write_text)
    print(text_file.read())
    assert text_file.read() == expected_write_text
    written_lines = ['A', '', 'BBB\n', 'C']
    text_file.write_lines(written_lines)
    expected_write_lines = ['A', '', 'BBB', 'C']
    assert text_file.read_lines() == expected_write_lines

    text_file.write(true_text)


def test_jsonl_file_read_write(example_json):
    dirname = tempfile.gettempdir() + '/'
    filename = dirname + 'a.json'
    if os.path.exists(filename):
        os.remove(filename)
    file = JsonLineFile(filename)
    file.write_lines(example_json)
    file.close()

    assert os.path.exists(filename) is True

    file2 = JsonLineFile(filename, is_remove=True)
    assert os.path.exists(filename) is False

    with pytest.raises(FileNotFoundError):
        file2.read_lines()

    file2.write_line(example_json)
    assert os.path.exists(filename) is True
    assert len(file2.read_lines()) == 1

    file2.close()


def test_jsonl_file_append(example_json):
    dirname = tempfile.gettempdir() + '/'
    filename = dirname + 'a.json'
    if os.path.exists(filename):
        os.remove(filename)

    file = JsonLineFile(filename, is_remove=True)
    file.append_lines(example_json)
    file.append(example_json)
    file.append_line(example_json)

    assert len(file.read_lines()) == 4
