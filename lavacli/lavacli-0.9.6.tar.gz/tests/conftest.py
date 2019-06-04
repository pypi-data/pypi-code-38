# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2017 Rémi Duraffort
# This file is part of lavacli.
#
# lavacli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lavacli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lavacli.  If not, see <http://www.gnu.org/licenses/>

import pytest
import xmlrpc.client
import yaml


class RecordingProxyFactory(object):
    def __new__(self, proxy_data):
        class RecordingProxy(object):
            data = proxy_data

            def __init__(self, uri, allow_none, transport):
                self.request = []

            def __call__(self, *args):
                request = ".".join(self.request)
                self.request = []
                data = self.data.pop(0)
                assert request == data["request"]  # nosec
                assert args == data["args"]  # nosec
                return data["ret"]

            def __getattr__(self, attr):
                self.request.append(attr)
                return self

        return RecordingProxy


@pytest.fixture
def setup(monkeypatch, tmpdir):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmpdir))
    with (tmpdir / "lavacli.yaml").open("w") as f_conf:
        f_conf.write(yaml.dump({"default": {"uri": "https://lava.example.com/RPC2"}}))
    monkeypatch.setattr(xmlrpc.client, "ServerProxy", RecordingProxyFactory(None))
