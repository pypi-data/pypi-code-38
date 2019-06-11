#! /usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function

import io
import sys
import time

from uhammer._utils import (capture, with_progressbar,
                            with_simple_progress_report)

# Copyright © 2018 Uwe Schmitt <uwe.schmitt@id.ethz.ch>,

if sys.version_info.major == 2:
    StringIO = io.BytesIO
else:
    StringIO = io.StringIO


def test_simple_progress_report(capsys, regtest):

    N = 10
    values = []
    for value in with_simple_progress_report(N, range(N), 0):
        values.append(value)
        time.sleep(.01)

    assert values == list(range(N))
    out, err = capsys.readouterr()
    assert err == ""
    regtest.write(out)
    assert len(out.strip().split("\n")) == 10


def test_progress_bar():
    N = 10
    values = []
    for value in with_progressbar(N, range(N)):
        values.append(value)
        time.sleep(.01)
    assert values == list(range(N))
    # don't test output here, would need to capture fid 1


def test_capture_false(regtest, tmpdir):
    stream = StringIO()
    sys.stdout = sys.stderr = stream

    with capture(path=None, show_output=True):
        print(1)
        print(2, file=sys.stderr)

    assert stream.getvalue() == "1\n2\n"

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def test_capture_true(regtest, tmpdir):

    stream = StringIO()
    sys.stdout = sys.stderr = stream

    with capture(path=None, show_output=False):
        print(1)
        print(2, file=sys.stderr)

    assert stream.getvalue() == ""

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def test_capture_to_file(regtest, tmpdir):

    capture_file_path = tmpdir.join("out.txt").strpath

    with capture(path=capture_file_path, show_output=False):
        print(1)
        print(2, file=sys.stderr)

    assert open(capture_file_path).read() == "1\n2\n"
