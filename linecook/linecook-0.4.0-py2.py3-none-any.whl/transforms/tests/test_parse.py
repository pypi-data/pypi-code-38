# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from linecook.transforms import parse


class TestJsonFromQS:

    def test_single_values(self):
        to_json = parse.json_from_qs()
        assert json.loads(to_json("a=1&b=2")) == {"a": "1", "b": "2"}

    def test_single_values_no_flattening(self):
        to_json = parse.json_from_qs(flatten=False)
        assert json.loads(to_json("a=1&b=2")) == {"a": ["1"], "b": ["2"]}

    def test_values_list(self):
        to_json = parse.json_from_qs()
        assert to_json("a=1&a=2") == '{"a": ["1", "2"]}'
