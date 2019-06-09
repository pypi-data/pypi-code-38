#!/usr/bin/env python
# -*- coding: utf-8
import pytest

from dockerma.image import Image


class TestImage(object):
    @pytest.mark.parametrize("name,tag,expected", (
        ("nginx", "v1", "nginx:v1"),
        ("name", None, "name"),
        ("example", "latest", "example:latest"),
    ))
    def test_ref(self, name, tag, expected):
        assert Image(None, name, tag).ref == expected
