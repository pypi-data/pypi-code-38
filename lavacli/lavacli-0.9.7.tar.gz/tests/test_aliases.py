# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2018 Rémi Duraffort
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

import json
import sys
import xmlrpc.client

from lavacli import main


def test_aliases_add_before_2019_05(setup, monkeypatch, capsys):
    version = "2019.04"
    monkeypatch.setattr(sys, "argv", ["lavacli", "aliases", "add", "new_alias"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "scheduler.aliases.add", "args": ("new_alias",), "ret": None},
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_aliases_add(setup, monkeypatch, capsys):
    version = "2019.05"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "aliases", "add", "new_alias", "device-type"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.add",
                "args": ("new_alias", "device-type"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_aliases_delete(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "aliases", "delete", "new_alias"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.delete",
                "args": ("new_alias",),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_aliases_list_empty(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "aliases", "list"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "scheduler.aliases.list", "args": (), "ret": []},
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Aliases:\n"  # nosec


def test_aliases_list(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "aliases", "list"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.list",
                "args": (),
                "ret": ["first-alias", "second-alias"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "Aliases:\n* first-alias\n* second-alias\n"
    )


def test_aliases_list_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "aliases", "list", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.list",
                "args": (),
                "ret": ["first-alias", "second-alias"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == '["first-alias", "second-alias"]\n'  # nosec


def test_aliases_list_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "aliases", "list", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.list",
                "args": (),
                "ret": ["first-alias", "second-alias"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "[first-alias, second-alias]\n"  # nosec


def test_aliases_show_before_2019_05(setup, monkeypatch, capsys):
    version = "2019.04"
    monkeypatch.setattr(sys, "argv", ["lavacli", "aliases", "show", "my_alias"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.show",
                "args": ("my_alias",),
                "ret": {"name": "my_alias", "device_types": ["qemu", "kvm"]},
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == "name        : my_alias\ndevice-types:\n* qemu\n* kvm\n"
    )


def test_aliases_show(setup, monkeypatch, capsys):
    version = "2019.05"
    monkeypatch.setattr(sys, "argv", ["lavacli", "aliases", "show", "my_alias"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.show",
                "args": ("my_alias",),
                "ret": {"name": "my_alias", "device_type": "qemu"},
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "name       : my_alias\ndevice-type: qemu\n"
    )


def test_aliases_show_json_before_2019_05(setup, monkeypatch, capsys):
    version = "2019.04"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "aliases", "show", "my_alias", "--json"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.show",
                "args": ("my_alias",),
                "ret": {"name": "my_alias", "device_types": ["qemu", "kvm"]},
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == {  # nosec
        "name": "my_alias",
        "device_types": ["qemu", "kvm"],
    }


def test_aliases_show_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "aliases", "show", "kvm", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.show",
                "args": ("kvm",),
                "ret": {"name": "kvm", "device_type": "qemu"},
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == {  # nosec
        "name": "kvm",
        "device_type": "qemu",
    }


def test_aliases_show_yaml_before_2019_05(setup, monkeypatch, capsys):
    version = "2019.04"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "aliases", "show", "my_alias", "--yaml"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.show",
                "args": ("my_alias",),
                "ret": {"name": "my_alias", "device_types": ["qemu", "kvm"]},
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "device_types: [qemu, kvm]\nname: my_alias\n"
    )


def test_aliases_show_yaml(setup, monkeypatch, capsys):
    version = "2019.05"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "aliases", "show", "my_alias", "--yaml"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.aliases.show",
                "args": ("my_alias",),
                "ret": {"name": "my_alias", "device_type": "qemu"},
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "{device_type: qemu, name: my_alias}\n"  # nosec
