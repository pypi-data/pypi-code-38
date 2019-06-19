# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import tempfile

from unittest import TestCase

from polyaxon_nginx.generate import generate_nginx_conf


class TestGenerate(TestCase):

    def test_generate_conf(self):
        tmp_dir = tempfile.mkdtemp()
        assert os.listdir(tmp_dir) == []
        generate_nginx_conf(path=tmp_dir)
        assert set(os.listdir(tmp_dir)) == {'polyaxon.base.conf', 'polyaxon.redirect.conf'}
