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
import pytest
import sys
import xmlrpc.client
import yaml

from lavacli import main


def test_dt_add(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "device-types", "add", "mydt"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.add",
                "args": ("mydt", None, True, False, 24, "hours"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_dt_add_1(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "device-types",
            "add",
            "mydt",
            "--description",
            "my new dt",
            "--hide",
            "--owners-only",
            "--health-frequency",
            "12",
            "--health-denominator",
            "jobs",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.add",
                "args": ("mydt", "my new dt", False, True, 12, "jobs"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_dt_aliases_add(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "aliases", "add", "mydt", "myalias"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.aliases.add",
                "args": ("mydt", "myalias"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_dt_aliases_delete(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "aliases", "delete", "mydt", "myalias"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.aliases.delete",
                "args": ("mydt", "myalias"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_dt_aliases_list(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "aliases", "list", "mydt"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.aliases.list",
                "args": ("mydt",),
                "ret": ["first alias", "second alias"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "Aliases:\n* first alias\n* second alias\n"
    )


def test_dt_aliases_list_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "aliases", "list", "mydt", "--json"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.aliases.list",
                "args": ("mydt",),
                "ret": ["first alias", "second alias"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == '["first alias", "second alias"]\n'  # nosec


def test_dt_aliases_list_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "aliases", "list", "mydt", "--yaml"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.aliases.list",
                "args": ("mydt",),
                "ret": ["first alias", "second alias"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "[first alias, second alias]\n"  # nosec


def test_dt_aliases_list_empty(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "aliases", "list", "mydt"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.aliases.list",
                "args": ("mydt",),
                "ret": [],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Aliases:\n"  # nosec


def test_dt_hc_get_before_2018_4(setup, monkeypatch, capsys):
    version = "2018.2"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "health-check", "get", "mydt"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": None, "args": (), "ret": []},
        ],
    )
    with pytest.raises(SystemExit):
        main()
    assert (  # nosec
        capsys.readouterr()[1]
        == """usage: lavacli device-types [-h] {add,aliases,list,show,template,update} ...
lavacli device-types: error: argument sub_sub_command: invalid choice: 'health-check' (choose from 'add', 'aliases', 'list', 'show', 'template', 'update')
"""
    )


def test_dt_hc_set_before_2018_4(setup, monkeypatch, capsys):
    version = "2018.2"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "health-check", "set", "mydt"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": None, "args": (), "ret": []},
        ],
    )
    with pytest.raises(SystemExit):
        main()
    assert (  # nosec
        capsys.readouterr()[1]
        == """usage: lavacli device-types [-h] {add,aliases,list,show,template,update} ...
lavacli device-types: error: argument sub_sub_command: invalid choice: 'health-check' (choose from 'add', 'aliases', 'list', 'show', 'template', 'update')
"""
    )


def test_dt_hc_get_after_2018_4(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "health-check", "get", "mydt"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.get_health_check",
                "args": ("mydt",),
                "ret": "definition.yaml",
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "definition.yaml\n"  # nosec


def test_dt_hc_set_after_2018_4(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    with (tmpdir / "hc.yaml").open("w") as f_hc:
        f_hc.write("definition")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "device-types",
            "health-check",
            "set",
            "mydt",
            str(tmpdir / "hc.yaml"),
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.set_health_check",
                "args": ("mydt", "definition"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_dt_list(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "device-types", "list"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.list",
                "args": (False,),
                "ret": [
                    {"name": "bbb", "devices": 0, "installed": True, "template": True},
                    {"name": "qemu", "devices": 3, "installed": True, "template": True},
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Device-Types:\n* bbb (0)\n* qemu (3)\n"  # nosec


def test_dt_list_all(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "device-types", "list", "--all"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.list",
                "args": (True,),
                "ret": [
                    {"name": "bbb", "devices": 0, "installed": False, "template": True},
                    {"name": "qemu", "devices": 3, "installed": True, "template": True},
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Device-Types:\n* bbb (0)\n* qemu (3)\n"  # nosec


def test_dt_list_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "device-types", "list", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.list",
                "args": (False,),
                "ret": [
                    {"name": "bbb", "devices": 0, "installed": True, "template": True},
                    {"name": "qemu", "devices": 3, "installed": True, "template": True},
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == [  # nosec
        {"name": "bbb", "devices": 0, "installed": True, "template": True},
        {"name": "qemu", "devices": 3, "installed": True, "template": True},
    ]


def test_dt_list_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "device-types", "list", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.list",
                "args": (False,),
                "ret": [
                    {"name": "bbb", "devices": 0, "installed": True, "template": True},
                    {"name": "qemu", "devices": 3, "installed": True, "template": True},
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """- {devices: 0, installed: true, name: bbb, template: true}
- {devices: 3, installed: true, name: qemu, template: true}
"""
    )


def test_dt_show(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "device-types", "show", "qemu"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.show",
                "args": ("qemu",),
                "ret": {
                    "name": "qemu",
                    "description": None,
                    "display": True,
                    "owners_only": False,
                    "health_disabled": False,
                    "aliases": ["kvm"],
                    "devices": ["qemu01", "qemu02"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """name            : qemu
description     : None
display         : True
owners only     : False
health disabled : False
aliases         : ['kvm']
devices         : ['qemu01', 'qemu02']
"""
    )


def test_dt_show_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "show", "qemu", "--json"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.show",
                "args": ("qemu",),
                "ret": {
                    "name": "qemu",
                    "description": None,
                    "display": True,
                    "owners_only": False,
                    "health_disabled": False,
                    "aliases": ["kvm"],
                    "devices": ["qemu01", "qemu02"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == {  # nosec
        "name": "qemu",
        "description": None,
        "display": True,
        "owners_only": False,
        "health_disabled": False,
        "aliases": ["kvm"],
        "devices": ["qemu01", "qemu02"],
    }


def test_dt_show_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "show", "qemu", "--yaml"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.show",
                "args": ("qemu",),
                "ret": {
                    "name": "qemu",
                    "description": None,
                    "display": True,
                    "owners_only": False,
                    "health_disabled": False,
                    "aliases": ["kvm"],
                    "devices": ["qemu01", "qemu02"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """aliases: [kvm]
description: null
devices: [qemu01, qemu02]
display: true
health_disabled: false
name: qemu
owners_only: false
"""
    )


def test_dt_template_get(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "template", "get", "bbb"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.get_template",
                "args": ("bbb",),
                "ret": "template content",
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "template content\n"  # nosec


def test_dt_template_set(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    with (tmpdir / "template.jinja2").open("w") as f_hc:
        f_hc.write("template definition")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "device-types",
            "template",
            "set",
            "bbb",
            str(tmpdir / "template.jinja2"),
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.set_template",
                "args": ("bbb", "template definition"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_dt_update(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "device-types", "update", "bbb", "--description", "hello"],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.update",
                "args": ("bbb", "hello", None, None, None, None, None),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_dt_update_1(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "device-types", "update", "bbb", "--hide"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.update",
                "args": ("bbb", None, False, None, None, None, None),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_dt_update_2(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "device-types",
            "update",
            "bbb",
            "--public",
            "--health-denominator",
            "hours",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.update",
                "args": ("bbb", None, None, False, None, "hours", None),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_dt_update_3(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "device-types",
            "update",
            "bbb",
            "--health-frequency",
            "12",
            "--health-active",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.device_types.update",
                "args": ("bbb", None, None, None, 12, None, False),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec
