from photons_messages_generator.generate import generate

from delfick_error import DelfickErrorTestMixin
from contextlib import contextmanager
from unittest import TestCase
from ruamel.yaml import YAML
from textwrap import dedent
import tempfile
import difflib
import shutil
import os

@contextmanager
def a_temp_file(mode='w'):
    filename = None
    tmpfile = None
    try:
        tmpfile = tempfile.NamedTemporaryFile(delete=False, mode=mode)
        filename = tmpfile.name
        yield tmpfile
    finally:
        if tmpfile is not None:
            tmpfile.close()
        if filename and os.path.exists(filename):
            os.remove(filename)

@contextmanager
def a_temp_dir():
    directory = None
    try:
        directory = tempfile.mkdtemp()
        yield directory
    finally:
        if os.path.exists(directory):
            shutil.rmtree(directory)

class Output:
    def __init__(self, directory):
        self.directory = directory

    def assertFileContents(self, path_parts, content):
        if isinstance(path_parts, str):
            path_parts = [path_parts]

        filename = os.path.join(self.directory, *path_parts)
        if not os.path.exists(filename):
            assert False, f"Expected {filename} to exist"

        with open(filename) as fle:
            lines = fle.readlines()

            with a_temp_file() as f:
                f.write(dedent(content).lstrip())
                f.flush()
                with open(f.name, 'r') as fr:
                    want = fr.readlines()

            if lines != want:
                diff = "".join(difflib.unified_diff(lines, want, fromfile="generated", tofile="want"))
                assert False, f"Expected content to be the same\n{diff}"

class TestCase(TestCase, DelfickErrorTestMixin):
    @contextmanager
    def generate(self, src, adjustments):
        with a_temp_dir() as directory:
            src = YAML(typ='safe').load(src)
            adjustments = YAML(typ='safe').load(adjustments) or {}

            if "output" not in adjustments:
                adjustments["output"] = [
                      {"create": "enums", "dest": "enums.py"}
                    , {"create": "fields", "dest": "fields.py"}
                    , {"create": "packets", "dest": "messages.py", "options": {"include": "*"}}
                    ]

            generate(src, adjustments, directory)
            yield Output(directory)
