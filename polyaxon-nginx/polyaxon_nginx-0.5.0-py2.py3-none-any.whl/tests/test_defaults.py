# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from unittest import TestCase

from polyaxon_nginx import settings


class TestSettings(TestCase):
    def test_default_values(self):
        assert settings.NGINX_PLUGINS == {}
        assert settings.DNS_USE_RESOLVER is False
        assert settings.DNS_CUSTOM_CLUSTER == 'cluster.local'
        assert settings.DNS_BACKEND == 'kube-dns'
        assert settings.DNS_PREFIX is None
        assert settings.NAMESPACE is None
        assert settings.LOGGING_LEVEL == 'warn'
        assert settings.TIMEOUT == 600
        assert settings.SSL_PATH == '/etc/ssl'
        assert settings.INDENT_CHAR == ' '
        assert settings.INDENT_WIDTH == 4
        assert settings.SSL_ENABLED is False
        assert settings.REPOS_PATH == '/repos'
        assert settings.DATA_PATH == '/data'
        assert settings.OUTPUTS_PATH == '/outputs'
