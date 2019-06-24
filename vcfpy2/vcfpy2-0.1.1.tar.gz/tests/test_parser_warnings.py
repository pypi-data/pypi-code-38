#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Created by Roberto Preste
"""Test that the public API classes are available from the ``vcfpy`` package
"""

import io
import textwrap

import pytest

from vcfpy2 import exceptions
from vcfpy2 import header
from vcfpy2 import parser


# HeaderChecker ---------------------------------------------------------------


def test_header_checker_missing_fileformat():
    # construct Header
    lines = [header.HeaderLine("key", "value")]
    hdr = header.Header(lines=lines, samples=header.SamplesInfos(["NA001"]))
    # setup HeaderChecker
    stream = io.StringIO()
    checker = parser.HeaderChecker()
    # execute
    with pytest.raises(exceptions.InvalidHeaderException):
        checker.run(hdr)


def test_header_checker_unknown_vcf_version():
    # construct Header
    lines = [header.HeaderLine("fileformat", "VCFv4.4")]
    hdr = header.Header(lines=lines, samples=header.SamplesInfos(["NA001"]))
    # setup HeaderChecker
    stream = io.StringIO()
    checker = parser.HeaderChecker()
    # execute
    checker.run(hdr)
    # check result
    EXPECTED = textwrap.dedent(
        r"""
    """
    ).lstrip()
    assert stream.getvalue() == EXPECTED


def test_header_checker_known_vcf_version():
    # construct Header
    lines = [header.HeaderLine("fileformat", "VCFv4.3")]
    hdr = header.Header(lines=lines, samples=header.SamplesInfos(["NA001"]))
    # setup HeaderChecker
    stream = io.StringIO()
    checker = parser.HeaderChecker()
    # execute
    checker.run(hdr)
    # check result
    EXPECTED = ""
    assert stream.getvalue() == EXPECTED
