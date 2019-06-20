import pytest
import argparse
from toolbox.cli import KeyValueAction


def test_key_value():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', action=KeyValueAction)
    parser.add_argument('file')
    args = parser.parse_args('-e name=bob -e age=5 file.py'.split())
    assert len(args.env) == 2
    assert args.env == {"name": "bob", "age": "5"}
    assert args.file == "file.py"
