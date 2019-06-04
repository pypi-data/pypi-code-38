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
import time
import xmlrpc.client
import yaml

from lavacli import main


def test_devices_add_before_2018_1(setup, monkeypatch, capsys):
    version = "2017.12"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "devices",
            "add",
            "qemu01",
            "--type",
            "qemu",
            "--worker",
            "worker01",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.add",
                "args": (
                    "qemu01",
                    "qemu",
                    "worker01",
                    None,
                    None,
                    True,
                    None,
                    None,
                    None,
                ),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_add_1_before_2018_1(setup, monkeypatch, capsys):
    version = "2017.12"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "devices",
            "add",
            "qemu01",
            "--type",
            "qemu",
            "--worker",
            "worker01",
            "--status",
            "IDLE",
            "--health",
            "PASS",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.add",
                "args": (
                    "qemu01",
                    "qemu",
                    "worker01",
                    None,
                    None,
                    True,
                    "IDLE",
                    "PASS",
                    None,
                ),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_add_2_before_2018_1(setup, monkeypatch, capsys):
    version = "2017.12"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "devices",
            "add",
            "qemu01",
            "--type",
            "qemu",
            "--worker",
            "worker01",
            "--user",
            "self",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.add",
                "args": (
                    "qemu01",
                    "qemu",
                    "worker01",
                    "self",
                    None,
                    True,
                    None,
                    None,
                    None,
                ),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_add_after_2018_1(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "devices",
            "add",
            "qemu01",
            "--type",
            "qemu",
            "--worker",
            "worker01",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.add",
                "args": ("qemu01", "qemu", "worker01", None, None, True, None, None),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_add_1_after_2018_1(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "devices",
            "add",
            "qemu01",
            "--type",
            "qemu",
            "--worker",
            "worker01",
            "--health",
            "GOOD",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.add",
                "args": ("qemu01", "qemu", "worker01", None, None, True, "GOOD", None),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_add_2_after_2018_1(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "devices",
            "add",
            "qemu01",
            "--type",
            "qemu",
            "--worker",
            "worker01",
            "--user",
            "me",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.add",
                "args": ("qemu01", "qemu", "worker01", "me", None, True, None, None),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_dict_get(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "dict", "get", "qemu01"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("qemu01", False, None),
                "ret": "yaml_dict",
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "yaml_dict\n"  # nosec


def test_devices_dict_get_render_field(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "devices", "dict", "get", "--render", "qemu01", "hello.0.world"],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("qemu01", True, None),
                "ret": yaml.dump({"hello": [{"world": "as usual"}, "my"]}),
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "as usual\n"  # nosec


def test_devices_dict_get_render_field_out_of_range(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "devices", "dict", "get", "--render", "qemu01", "hello.2.world"],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("qemu01", True, None),
                "ret": yaml.dump({"hello": [{"world": "as usual"}, "my"]}),
            },
        ],
    )
    assert main() == 1  # nosec
    assert capsys.readouterr()[0] == "list index out of range (2 vs 2)\n"  # nosec


def test_devices_dict_get_render_field_missing(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "devices", "dict", "get", "--render", "qemu01", "hello.0.worl"],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("qemu01", True, None),
                "ret": yaml.dump({"hello": [{"world": "as usual"}, "my"]}),
            },
        ],
    )
    assert main() == 1  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "Unknow key 'worl' for '{'world': 'as usual'}'\n"
    )


def test_devices_dict_get_render_field_missing_1(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "devices", "dict", "get", "--render", "qemu01", "hello.0.world.0"],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("qemu01", True, None),
                "ret": yaml.dump({"hello": [{"world": "as usual"}, "my"]}),
            },
        ],
    )
    assert main() == 1  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "Unable to lookup inside 'as usual' for '0'\n"
    )


def test_devices_dict_get_render_field_missing_2(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "devices",
            "dict",
            "get",
            "--render",
            "qemu01",
            "hello.0.world.missing",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("qemu01", True, None),
                "ret": yaml.dump({"hello": [{"world": "as usual"}, "my"]}),
            },
        ],
    )
    assert main() == 1  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "Unable to lookup inside 'as usual' for 'missing'\n"
    )


def test_devices_dict_get_jinja2_field(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "devices", "dict", "get", "qemu01", "hello"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("qemu01", False, None),
                "ret": "{% set hello = 'bla' %}",
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "bla\n"  # nosec


def test_devices_dict_get_jinja2_field_2(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "devices", "dict", "get", "qemu01", "hello.0.bla"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("qemu01", False, None),
                "ret": "{% set hello = [{'bla': 'something'}] %}",
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "something\n"  # nosec


def test_devices_dict_get_jinja2_field_missing(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "devices", "dict", "get", "qemu01", "world"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("qemu01", False, None),
                "ret": "{% set hello = 'bla' %}",
            },
        ],
    )
    assert main() == 1  # nosec
    assert capsys.readouterr()[0] == "Unknow field 'world'\n"  # nosec


def test_devices_dict_set(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    with (tmpdir / "dict.jinja2").open("w") as f_conf:
        f_conf.write("{% set exclusive = True %}")
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "devices", "dict", "set", "qemu01", str(tmpdir / "dict.jinja2")],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.set_dictionary",
                "args": ("qemu01", "{% set exclusive = True %}"),
                "ret": True,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_dict_set_error(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    with (tmpdir / "dict.jinja2").open("w") as f_conf:
        f_conf.write("{% set exclusive = True %}")
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "devices", "dict", "set", "qemu01", str(tmpdir / "dict.jinja2")],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.set_dictionary",
                "args": ("qemu01", "{% set exclusive = True %}"),
                "ret": False,
            },
        ],
    )
    assert main() == 1  # nosec
    assert capsys.readouterr()[0] == "Unable to set the configuration\n"  # nosec


def test_devices_list(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "list"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.list",
                "args": (False,),
                "ret": [
                    {
                        "hostname": "qemu01",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Idle",
                        "current_job": None,
                        "pipeline": True,
                    },
                    {
                        "hostname": "qemu02",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1234,
                        "pipeline": True,
                    },
                    {
                        "hostname": "bbb01",
                        "type": "bbb",
                        "health": "Maintenance",
                        "state": "Idle",
                        "current_job": None,
                        "pipeline": True,
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Devices:
* qemu01 (qemu): Idle,Good
* qemu02 (qemu): Running,Good
* bbb01 (bbb): Idle,Maintenance
"""
    )


def test_devices_list_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "list", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.list",
                "args": (False,),
                "ret": [
                    {
                        "hostname": "qemu01",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Idle",
                        "current_job": None,
                        "pipeline": True,
                    },
                    {
                        "hostname": "qemu02",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1234,
                        "pipeline": True,
                    },
                    {
                        "hostname": "bbb01",
                        "type": "bbb",
                        "health": "Maintenance",
                        "state": "Idle",
                        "current_job": None,
                        "pipeline": True,
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == [  # nosec
        {
            "hostname": "qemu01",
            "type": "qemu",
            "health": "Good",
            "state": "Idle",
            "current_job": None,
            "pipeline": True,
        },
        {
            "hostname": "qemu02",
            "type": "qemu",
            "health": "Good",
            "state": "Running",
            "current_job": 1234,
            "pipeline": True,
        },
        {
            "hostname": "bbb01",
            "type": "bbb",
            "health": "Maintenance",
            "state": "Idle",
            "current_job": None,
            "pipeline": True,
        },
    ]


def test_devices_list_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "list", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.list",
                "args": (False,),
                "ret": [
                    {
                        "hostname": "qemu01",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Idle",
                        "current_job": None,
                        "pipeline": True,
                    },
                    {
                        "hostname": "qemu02",
                        "type": "qemu",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1234,
                        "pipeline": True,
                    },
                    {
                        "hostname": "bbb01",
                        "type": "bbb",
                        "health": "Maintenance",
                        "state": "Idle",
                        "current_job": None,
                        "pipeline": True,
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """- {current_job: null, health: Good, hostname: qemu01, pipeline: true, state: Idle,
  type: qemu}
- {current_job: 1234, health: Good, hostname: qemu02, pipeline: true, state: Running,
  type: qemu}
- {current_job: null, health: Maintenance, hostname: bbb01, pipeline: true, state: Idle,
  type: bbb}
"""
    )


def test_devices_list_before_2018_1(setup, monkeypatch, capsys, tmpdir):
    version = "2017.12"
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "list"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.list",
                "args": (False,),
                "ret": [
                    {
                        "hostname": "qemu01",
                        "type": "qemu",
                        "status": "Idle",
                        "current_job": None,
                        "pipeline": True,
                    },
                    {
                        "hostname": "qemu02",
                        "type": "qemu",
                        "status": "Running",
                        "current_job": 1234,
                        "pipeline": True,
                    },
                    {
                        "hostname": "bbb01",
                        "type": "bbb",
                        "status": "Maintenance",
                        "current_job": None,
                        "pipeline": True,
                    },
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Devices:
* qemu01 (qemu): Idle
* qemu02 (qemu): Running
* bbb01 (bbb): Maintenance
"""
    )


def test_devices_maintenance(setup, monkeypatch, capsys):
    version = "2018.4"
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "maintenance", "qemu01"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.update",
                "args": ("qemu01", None, None, None, None, "MAINTENANCE", None),
                "ret": None,
            },
            {
                "request": "scheduler.devices.show",
                "args": ("qemu01",),
                "ret": {
                    "hostname": "qemu01",
                    "device_type": "qemu",
                    "health": "Good",
                    "state": "Idle",
                    "health_job": True,
                    "description": None,
                    "public": True,
                    "pipeline": True,
                    "has_device_dict": True,
                    "worker": "worker01",
                    "user": None,
                    "group": "group01",
                    "current_job": 1234,
                    "tags": ["a", "b"],
                },
            },
            {
                "request": "scheduler.jobs.show",
                "args": (1234,),
                "ret": {
                    "id": "1234",
                    "description": "basic testing",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Unknown",
                    "state": "Running",
                    "submitter": "lava-bot",
                    "submit_time": last_ping,
                    "start_time": last_ping,
                    "end_time": None,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": "",
                },
            },
            {
                "request": "scheduler.jobs.show",
                "args": (1234,),
                "ret": {
                    "id": "1234",
                    "description": "basic testing",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-bot",
                    "submit_time": last_ping,
                    "start_time": last_ping,
                    "end_time": last_ping,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": "",
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "-> waiting for job 1234\n--> waiting\n"  # nosec


def test_devices_maintenance_force(setup, monkeypatch, capsys):
    version = "2018.4"
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "devices", "maintenance", "qemu01", "--force"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.update",
                "args": ("qemu01", None, None, None, None, "MAINTENANCE", None),
                "ret": None,
            },
            {
                "request": "scheduler.devices.show",
                "args": ("qemu01",),
                "ret": {
                    "hostname": "qemu01",
                    "device_type": "qemu",
                    "health": "Good",
                    "state": "Idle",
                    "health_job": True,
                    "description": None,
                    "public": True,
                    "pipeline": True,
                    "has_device_dict": True,
                    "worker": "worker01",
                    "user": None,
                    "group": "group01",
                    "current_job": 1234,
                    "tags": ["a", "b"],
                },
            },
            {"request": "scheduler.jobs.cancel", "args": (1234,), "ret": None},
            {
                "request": "scheduler.jobs.show",
                "args": (1234,),
                "ret": {
                    "id": "1234",
                    "description": "basic testing",
                    "device": "qemu01",
                    "device_type": "qemu",
                    "health_check": False,
                    "pipeline": True,
                    "health": "Complete",
                    "state": "Finished",
                    "submitter": "lava-bot",
                    "submit_time": last_ping,
                    "start_time": last_ping,
                    "end_time": last_ping,
                    "tags": [],
                    "visibility": "Publicly visible",
                    "failure_comment": "",
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "-> waiting for job 1234\n--> canceling\n"  # nosec


def test_devices_maintenance_without_current_job(setup, monkeypatch, capsys):
    version = "2018.4"
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "devices", "maintenance", "qemu01", "--force"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.update",
                "args": ("qemu01", None, None, None, None, "MAINTENANCE", None),
                "ret": None,
            },
            {
                "request": "scheduler.devices.show",
                "args": ("qemu01",),
                "ret": {
                    "hostname": "qemu01",
                    "device_type": "qemu",
                    "health": "Good",
                    "state": "Idle",
                    "health_job": True,
                    "description": None,
                    "public": True,
                    "pipeline": True,
                    "has_device_dict": True,
                    "worker": "worker01",
                    "user": None,
                    "group": "group01",
                    "current_job": None,
                    "tags": ["a", "b"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_show(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "show", "qemu01"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.show",
                "args": ("qemu01",),
                "ret": {
                    "hostname": "qemu01",
                    "device_type": "qemu",
                    "health": "Good",
                    "state": "Idle",
                    "health_job": True,
                    "description": None,
                    "public": True,
                    "pipeline": True,
                    "has_device_dict": True,
                    "worker": "worker01",
                    "user": None,
                    "group": "group01",
                    "current_job": None,
                    "tags": ["a", "b"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """name        : qemu01
device-type : qemu
state       : Idle
health      : Good
user        : None
group       : group01
health job  : True
description : None
public      : True
pipeline    : True
device-dict : True
worker      : worker01
current job : None
tags        : ['a', 'b']
"""
    )


def test_devices_show_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "show", "qemu01", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.show",
                "args": ("qemu01",),
                "ret": {
                    "hostname": "qemu01",
                    "device_type": "qemu",
                    "health": "Good",
                    "state": "Idle",
                    "health_job": True,
                    "description": None,
                    "public": True,
                    "pipeline": True,
                    "has_device_dict": True,
                    "worker": "worker01",
                    "user": None,
                    "group": "group01",
                    "current_job": None,
                    "tags": ["a", "b"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == {  # nosec
        "hostname": "qemu01",
        "device_type": "qemu",
        "health": "Good",
        "state": "Idle",
        "health_job": True,
        "description": None,
        "public": True,
        "pipeline": True,
        "has_device_dict": True,
        "worker": "worker01",
        "user": None,
        "group": "group01",
        "current_job": None,
        "tags": ["a", "b"],
    }


def test_devices_show_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "show", "qemu01", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.show",
                "args": ("qemu01",),
                "ret": {
                    "hostname": "qemu01",
                    "device_type": "qemu",
                    "health": "Good",
                    "state": "Idle",
                    "health_job": True,
                    "description": None,
                    "public": True,
                    "pipeline": True,
                    "has_device_dict": True,
                    "worker": "worker01",
                    "user": None,
                    "group": "group01",
                    "current_job": None,
                    "tags": ["a", "b"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """current_job: null
description: null
device_type: qemu
group: group01
has_device_dict: true
health: Good
health_job: true
hostname: qemu01
pipeline: true
public: true
state: Idle
tags: [a, b]
user: null
worker: worker01
"""
    )


def test_devices_show_before_2018_1(setup, monkeypatch, capsys):
    version = "2017.12"
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "show", "qemu01"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.show",
                "args": ("qemu01",),
                "ret": {
                    "hostname": "qemu01",
                    "device_type": "qemu",
                    "status": "Idle",
                    "health_job": True,
                    "description": None,
                    "public": True,
                    "pipeline": True,
                    "has_device_dict": True,
                    "worker": "worker01",
                    "user": None,
                    "group": "group01",
                    "current_job": None,
                    "tags": ["a", "b"],
                },
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """name        : qemu01
device-type : qemu
status      : Idle
user        : None
group       : group01
health job  : True
description : None
public      : True
pipeline    : True
device-dict : True
worker      : worker01
current job : None
tags        : ['a', 'b']
"""
    )


def test_devices_tags_add(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "devices", "tags", "add", "qemu01", "hdd"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.tags.add",
                "args": ("qemu01", "hdd"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_tags_delete(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "devices", "tags", "delete", "qemu01", "hdd"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.tags.delete",
                "args": ("qemu01", "hdd"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_tags_list(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "devices", "tags", "list", "qemu01"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.tags.list",
                "args": ("qemu01",),
                "ret": ["hdd", "virt"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "Tags:\n* hdd\n* virt\n"  # nosec


def test_devices_tags_list_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "devices", "tags", "list", "--json", "qemu01"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.tags.list",
                "args": ("qemu01",),
                "ret": ["hdd", "virt"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == '["hdd", "virt"]\n'  # nosec


def test_devices_tags_list_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "devices", "tags", "list", "--yaml", "qemu01"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.tags.list",
                "args": ("qemu01",),
                "ret": ["hdd", "virt"],
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "[hdd, virt]\n"  # nosec


def test_devices_update(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "devices",
            "update",
            "qemu01",
            "--worker",
            "worker01",
            "--health",
            "UNKNOWN",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.update",
                "args": ("qemu01", "worker01", None, None, None, "UNKNOWN", None),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec


def test_devices_update_before_2018_1(setup, monkeypatch, capsys):
    version = "2017.12"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "devices",
            "update",
            "qemu01",
            "--worker",
            "worker01",
            "--status",
            "IDLE",
            "--health",
            "UNKNOWN",
        ],
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.devices.update",
                "args": (
                    "qemu01",
                    "worker01",
                    None,
                    None,
                    None,
                    "IDLE",
                    "UNKNOWN",
                    None,
                ),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == ""  # nosec
