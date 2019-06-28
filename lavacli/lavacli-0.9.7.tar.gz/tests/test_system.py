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

import sys
import time
import xmlrpc.client

from lavacli import main


def test_system_active(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "system", "active"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.workers.list",
                "args": (),
                "ret": ["worker01", "worker02"],
            },
            {
                "request": "scheduler.workers.update",
                "args": ("worker01", None, "ACTIVE"),
                "ret": None,
            },
            {
                "request": "scheduler.workers.update",
                "args": ("worker02", None, "ACTIVE"),
                "ret": None,
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Activate workers:
* worker01
* worker02
"""
    )


def test_system_api(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "system", "api"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "system.api_version", "args": (), "ret": 2},
        ],
    )

    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "2\n"  # nosec


def test_system_export(setup, monkeypatch, capsys, tmpdir):
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "system", "export", str(tmpdir / "export")]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": "2018.6"},
            {
                "request": "scheduler.aliases.list",
                "args": (),
                "ret": ["alias01", "alias02"],
            },
            {
                "request": "scheduler.aliases.show",
                "args": ("alias01",),
                "ret": {"name": "alias01", "device_types": ["qemu", "kvm"]},
            },
            {
                "request": "scheduler.aliases.show",
                "args": ("alias02",),
                "ret": {"name": "alias02", "device_types": []},
            },
            {
                "request": "scheduler.tags.list",
                "args": (),
                "ret": [
                    {"name": "hdd", "description": "drive attached"},
                    {"name": "tag1", "description": None},
                ],
            },
            {
                "request": "scheduler.workers.list",
                "args": (),
                "ret": ["worker01", "worker02"],
            },
            {
                "request": "scheduler.workers.show",
                "args": ("worker01",),
                "ret": {
                    "hostname": "worker01",
                    "description": None,
                    "state": "Idle",
                    "health": "Active",
                    "devices": ["qemu01", "bbb-01"],
                    "last_ping": last_ping,
                },
            },
            {
                "request": "scheduler.workers.show",
                "args": ("worker02",),
                "ret": {
                    "hostname": "worker01",
                    "description": None,
                    "state": "Idle",
                    "health": "Active",
                    "devices": [],
                    "last_ping": last_ping,
                },
            },
            {
                "request": "scheduler.device_types.list",
                "args": (),
                "ret": [
                    {"name": "bbb", "devices": 1, "installed": True, "template": True},
                    {"name": "qemu", "devices": 1, "installed": True, "template": True},
                ],
            },
            {
                "request": "scheduler.device_types.show",
                "args": ("bbb",),
                "ret": {
                    "name": "bbb",
                    "description": None,
                    "display": True,
                    "owners_only": False,
                    "health_disabled": False,
                    "aliases": [],
                    "devices": ["bbb-01"],
                },
            },
            {
                "request": "scheduler.device_types.get_template",
                "args": ("bbb",),
                "ret": "bbb device-type template",
            },
            {
                "request": "scheduler.device_types.show",
                "args": ("qemu",),
                "ret": {
                    "name": "qemu",
                    "description": None,
                    "display": True,
                    "owners_only": False,
                    "health_disabled": False,
                    "aliases": [],
                    "devices": ["qemu01"],
                },
            },
            {
                "request": "scheduler.device_types.get_template",
                "args": ("qemu",),
                "ret": "qemu device-type template",
            },
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
                        "hostname": "bbb-01",
                        "type": "bbb",
                        "health": "Maintenance",
                        "state": "Idle",
                        "current_job": None,
                        "pipeline": True,
                    },
                ],
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
                    "tags": [],
                },
            },
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("qemu01",),
                "ret": "qemu01 device dict",
            },
            {
                "request": "scheduler.devices.show",
                "args": ("bbb-01",),
                "ret": {
                    "hostname": "bbb-01",
                    "device_type": "bbb",
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
                    "tags": [],
                },
            },
            {
                "request": "scheduler.devices.get_dictionary",
                "args": ("bbb-01",),
                "ret": "bbb-01 device dict",
            },
        ],
    )
    assert main() == 0  # nosec
    lines = capsys.readouterr()[0].split("\n")
    assert lines[0] == "Export to %s" % str(tmpdir / "export")  # nosec
    assert (  # nosec
        "\n".join(lines[1:])
        == """Listing aliases
* alias01
* alias02
Listing tags
* hdd
* tag1
Listing workers
* worker01
* worker02
Listing device-types
* bbb
* qemu
Listing devices
* qemu01
* bbb-01
"""
    )


def test_system_maintenance(setup, monkeypatch, capsys):
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(sys, "argv", ["lavacli", "system", "maintenance"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": "2018.6"},
            {
                "request": "scheduler.workers.list",
                "args": (),
                "ret": ["worker01", "worker02"],
            },
            {
                "request": "scheduler.workers.update",
                "args": ("worker01", None, "MAINTENANCE"),
                "ret": None,
            },
            {
                "request": "scheduler.workers.update",
                "args": ("worker02", None, "MAINTENANCE"),
                "ret": None,
            },
            {
                "request": "scheduler.devices.list",
                "args": (),
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
                        "hostname": "bbb-01",
                        "type": "bbb",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1234,
                        "pipeline": True,
                    },
                    {
                        "hostname": "bbb-02",
                        "type": "bbb",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1235,
                        "pipeline": True,
                    },
                ],
            },
            {
                "request": "scheduler.jobs.show",
                "args": (1234,),
                "ret": {
                    "id": "1234",
                    "description": "basic testing",
                    "device": "bbb-01",
                    "device_type": "bbb",
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
                    "device": "bbb-01",
                    "device_type": "bbb",
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
            {
                "request": "scheduler.jobs.show",
                "args": (1235,),
                "ret": {
                    "id": "1235",
                    "description": "basic testing",
                    "device": "bbb-02",
                    "device_type": "bbb",
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
    assert (  # nosec
        capsys.readouterr()[0]
        == """Maintenance workers:
* worker01
* worker02
Wait for devices:
* qemu01
* bbb-01
--> waiting for job 1234
---> waiting
* bbb-02
--> waiting for job 1235
"""
    )


def test_system_maintenance_exclude(setup, monkeypatch, capsys):
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "system", "maintenance", "--exclude", "worker01"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": "2018.6"},
            {
                "request": "scheduler.workers.list",
                "args": (),
                "ret": ["worker01", "worker02"],
            },
            {
                "request": "scheduler.workers.update",
                "args": ("worker02", None, "MAINTENANCE"),
                "ret": None,
            },
            {
                "request": "scheduler.workers.show",
                "args": ("worker01",),
                "ret": {
                    "hostname": "worker01",
                    "description": None,
                    "state": "Idle",
                    "health": "Active",
                    "devices": ["qemu01", "bbb-02"],
                    "last_ping": last_ping,
                },
            },
            {
                "request": "scheduler.devices.list",
                "args": (),
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
                        "hostname": "bbb-01",
                        "type": "bbb",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1234,
                        "pipeline": True,
                    },
                    {
                        "hostname": "bbb-02",
                        "type": "bbb",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1235,
                        "pipeline": True,
                    },
                ],
            },
            {
                "request": "scheduler.jobs.show",
                "args": (1234,),
                "ret": {
                    "id": "1234",
                    "description": "basic testing",
                    "device": "bbb-01",
                    "device_type": "bbb",
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
                    "device": "bbb-01",
                    "device_type": "bbb",
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
    assert (  # nosec
        capsys.readouterr()[0]
        == """Maintenance workers:
* worker01 [SKIP]
* worker02
Wait for devices:
* bbb-01
--> waiting for job 1234
---> waiting
"""
    )


def test_system_maintenance_force(setup, monkeypatch, capsys):
    last_ping = xmlrpc.client.DateTime("20180128T01:01:01")

    def sleep(duration):
        assert duration == 5  # nosec

    monkeypatch.setattr(time, "sleep", sleep)
    monkeypatch.setattr(sys, "argv", ["lavacli", "system", "maintenance", "--force"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": "2018.6"},
            {
                "request": "scheduler.workers.list",
                "args": (),
                "ret": ["worker01", "worker02"],
            },
            {
                "request": "scheduler.workers.update",
                "args": ("worker01", None, "MAINTENANCE"),
                "ret": None,
            },
            {
                "request": "scheduler.workers.update",
                "args": ("worker02", None, "MAINTENANCE"),
                "ret": None,
            },
            {
                "request": "scheduler.devices.list",
                "args": (),
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
                        "hostname": "bbb-01",
                        "type": "bbb",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1234,
                        "pipeline": True,
                    },
                    {
                        "hostname": "bbb-02",
                        "type": "bbb",
                        "health": "Good",
                        "state": "Running",
                        "current_job": 1235,
                        "pipeline": True,
                    },
                ],
            },
            {"request": "scheduler.jobs.cancel", "args": (1234,), "ret": None},
            {
                "request": "scheduler.jobs.show",
                "args": (1234,),
                "ret": {
                    "id": "1234",
                    "description": "basic testing",
                    "device": "bbb-01",
                    "device_type": "bbb",
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
            {"request": "scheduler.jobs.cancel", "args": (1235,), "ret": None},
            {
                "request": "scheduler.jobs.show",
                "args": (1235,),
                "ret": {
                    "id": "1235",
                    "description": "basic testing",
                    "device": "bbb-02",
                    "device_type": "bbb",
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
    assert (  # nosec
        capsys.readouterr()[0]
        == """Maintenance workers:
* worker01
* worker02
Wait for devices:
* qemu01
* bbb-01
--> waiting for job 1234
---> canceling
* bbb-02
--> waiting for job 1235
---> canceling
"""
    )


def test_system_methods_list(setup, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["lavacli", "system", "methods", "list"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": "2018.6"},
            {
                "request": "system.listMethods",
                "args": (),
                "ret": [
                    "scheduler.job_details",
                    "scheduler.job_health",
                    "scheduler.job_list_status",
                ],
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == "scheduler.job_details\nscheduler.job_health\nscheduler.job_list_status\n"
    )


def test_system_methods_help(setup, monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "system", "methods", "help", "system.version"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": "2018.6"},
            {
                "request": "system.methodHelp",
                "args": ("system.version",),
                "ret": """Name
----
`system.version` ()

Description
-----------
Return the lava-server version string

Arguments
---------
None

Return value
------------
lava-server version string""",
            },
        ],
    )

    assert main() == 0  # nosec

    assert (  # nosec
        capsys.readouterr()[0]
        == """Name
----
`system.version` ()

Description
-----------
Return the lava-server version string

Arguments
---------
None

Return value
------------
lava-server version string
"""
    )


def test_system_methods_signature(setup, monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "system", "methods", "signature", "system.version"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": "2018.6"},
            {
                "request": "system.methodSignature",
                "args": ("system.version",),
                "ret": "undef",
            },
        ],
    )

    assert main() == 0  # nosec

    assert capsys.readouterr()[0] == "undef\n"  # nosec


def test_system_version(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "system", "version"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "system.version", "args": (), "ret": version},
        ],
    )

    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "2018.4\n"  # nosec


def test_system_whoami(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "system", "whoami"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "system.whoami", "args": (), "ret": "lava-admin"},
        ],
    )

    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "lava-admin\n"  # nosec


def test_system_whoami_anonymous(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "system", "whoami"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {"request": "system.whoami", "args": (), "ret": None},
        ],
    )

    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "<AnonymousUser>\n"  # nosec
