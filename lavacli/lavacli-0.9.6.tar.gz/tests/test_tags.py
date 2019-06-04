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


def test_tags_add(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "tags", "add", "hdd"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "scheduler.tags.add", "args": ("hdd", None), "ret": None},
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_tags_delete(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "tags", "delete", "hdd"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "scheduler.tags.delete", "args": ("hdd",), "ret": None},
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_tags_list(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "tags", "list"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.tags.list",
                "args": (),
                "ret": [
                    {"name": "hdd", "description": "drive attached"},
                    {"name": "tag1", "description": None},
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Tags:
* hdd (drive attached)
* tag1
"""
    )


def test_tags_list_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "tags", "list", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.tags.list",
                "args": (),
                "ret": [
                    {"name": "hdd", "description": "drive attached"},
                    {"name": "tag1", "description": None},
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == [  # nosec
        {"name": "hdd", "description": "drive attached"},
        {"name": "tag1", "description": None},
    ]


def test_tags_list_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "tags", "list", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.tags.list",
                "args": (),
                "ret": [
                    {"name": "hdd", "description": "drive attached"},
                    {"name": "tag1", "description": None},
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """- {description: drive attached, name: hdd}
- {description: null, name: tag1}
"""
    )


def test_tags_show(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "tags", "show", "hdd"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.tags.show",
                "args": ("hdd",),
                "ret": {
                    "name": "hdd",
                    "description": "drive attached",
                    "devices": ["aemu01", "bbb-01"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """name       : hdd
description: drive attached
devices    :
* aemu01
* bbb-01
"""
    )


def test_tags_show_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "tags", "show", "--json", "hdd"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.tags.show",
                "args": ("hdd",),
                "ret": {
                    "name": "hdd",
                    "description": "drive attached",
                    "devices": ["aemu01", "bbb-01"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == {  # nosec
        "name": "hdd",
        "description": "drive attached",
        "devices": ["aemu01", "bbb-01"],
    }


def test_tags_show_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "tags", "show", "--yaml", "hdd"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.tags.show",
                "args": ("hdd",),
                "ret": {
                    "name": "hdd",
                    "description": "drive attached",
                    "devices": ["aemu01", "bbb-01"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """description: drive attached
devices: [aemu01, bbb-01]
name: hdd
"""
    )
