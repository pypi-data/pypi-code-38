#!/usr/bin/env python
# -*- coding: utf-8

from dockerma import parse_args


class TestParseArgs(object):
    def test_capture_build_command(self):
        args = ["--tls", "build", "--dummy", "path"]
        options, remaining = parse_args(args)
        assert remaining == ["--dummy"]
        assert options.tls is True
        assert options.command == "build"
