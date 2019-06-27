# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from unittest import TestCase

from polyaxon_nginx.schemas.main import get_main_config


class TestBaseSchemas(TestCase):

    def test_base_config(self):
        expected = """
upstream polyaxon {
  server unix:/polyaxon/web/polyaxon.sock;
}

server {
    include polyaxon/polyaxon.base.conf;
}
"""
        assert get_main_config() == expected
