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
import zmq

from lavacli import main


class DummySocket(object):
    data = []
    url = "tcp://lava.example.com:5500"

    def setsockopt(self, key, value):
        assert key == zmq.SUBSCRIBE  # nosec
        assert value == b""  # nosec

    def connect(self, url):
        assert url == self.url  # nosec

    def recv_multipart(self):
        return self.data.pop(0)


class DummyContext(object):
    def socket(self, sock_type):
        assert sock_type == zmq.SUB  # nosec
        return DummySocket()


def test_events_listen(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "events", "listen"])
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    DummySocket.data = [
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Idle",
                    "health": "Good",
                }
            ),
        ),
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Running",
                    "health": "Good",
                    "job": "1234",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1234",
                    "device": "bbb-01",
                    "state": "Running",
                    "health": "Unknown",
                    "description": "a nice job",
                }
            ),
        ),
        ("invalid message"),
        (
            "v.l.o.worker",
            "uuid",
            "2018-01-31",
            "admin",
            json.dumps(
                {"hostname": "worker-01", "state": "Active", "health": "Maintenance"}
            ),
        ),
        (
            "v.l.o.event",
            "uuid",
            "2018-01-31",
            "lavaserver",
            json.dumps({"message": "hello from the job", "job": "1245"}),
        ),
    ]
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5500",
            },
        ],
    )
    assert main() == 1  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Listening to tcp://lava.example.com:5500
\033[1;30m2018-01-29\033[0m \033[1;37mv.l.o.device\033[0m \033[32mlava-health\033[0m - [bbb-01] <bbb> state=Idle health=Good
\033[1;30m2018-01-29\033[0m \033[1;37mv.l.o.device\033[0m \033[32mlava-health\033[0m - [bbb-01] <bbb> state=Running health=Good for 1234
\033[1;30m2018-01-30\033[0m \033[1;37mv.l.o.testjob\033[0m \033[32mlava-health\033[0m - [1234] <bbb-01> state=Running health=Unknown (a nice job)
Invalid message: invalid message
\033[1;30m2018-01-31\033[0m \033[1;37mv.l.o.worker\033[0m \033[32madmin\033[0m - [worker-01] state=Active health=Maintenance
\033[1;30m2018-01-31\033[0m \033[1;37mv.l.o.event\033[0m \033[32mlavaserver\033[0m - [1245] message=hello from the job
Unknown error: pop from empty list
"""
    )


def test_events_listen_before_2018_1(setup, monkeypatch, capsys, tmpdir):
    version = "2017.12"
    monkeypatch.setattr(sys, "argv", ["lavacli", "events", "listen"])
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    DummySocket.data = [
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps({"device": "bbb-01", "device_type": "bbb", "status": "Idle"}),
        ),
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "status": "Running",
                    "job": "1234",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1234",
                    "device": "bbb-01",
                    "status": "Running",
                    "description": "a nice job",
                }
            ),
        ),
        ("invalid message"),
    ]
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5500",
            },
        ],
    )
    assert main() == 1  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Listening to tcp://lava.example.com:5500
\033[1;30m2018-01-29\033[0m \033[1;37mv.l.o.device\033[0m \033[32mlava-health\033[0m - [bbb-01] <bbb> Idle
\033[1;30m2018-01-29\033[0m \033[1;37mv.l.o.device\033[0m \033[32mlava-health\033[0m - [bbb-01] <bbb> Running for 1234
\033[1;30m2018-01-30\033[0m \033[1;37mv.l.o.testjob\033[0m \033[32mlava-health\033[0m - [1234] <bbb-01> Running (a nice job)
Invalid message: invalid message
Unknown error: pop from empty list
"""
    )


def test_events_listen_config(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lavacli",
            "--uri",
            "https://admin:12345@localhost:456/RPC2",
            "events",
            "listen",
        ],
    )
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    monkeypatch.setattr(DummySocket, "url", "tcp://localhost:5501")
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5501",
            },
        ],
    )
    assert main() == 1  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Listening to tcp://localhost:5501
Unknown error: pop from empty list
"""
    )


def test_events_listen_config_2(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "events", "listen"])
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    monkeypatch.setattr(DummySocket, "url", "tcp://localhost:789")
    with (tmpdir / "lavacli.yaml").open("w") as f_conf:
        f_conf.write(
            "default:\n  username: admin\n  token: 12345\n  uri: https://localhost:456/RPC2\n  events:\n    uri: tcp://localhost:789\n"
        )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [{"request": "system.version", "args": (), "ret": version}],
    )
    assert main() == 1  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Listening to tcp://localhost:789
Unknown error: pop from empty list
"""
    )


def test_events_listen_filter(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "events", "listen", "--filter", "device"]
    )
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    DummySocket.data = [
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Idle",
                    "health": "Good",
                }
            ),
        ),
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Running",
                    "health": "Good",
                    "job": "1234",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1234",
                    "device": "bbb-01",
                    "state": "Running",
                    "health": "Unknown",
                    "description": "a nice job",
                }
            ),
        ),
        ("invalid message"),
        (
            "v.l.o.worker",
            "uuid",
            "2018-01-31",
            "admin",
            json.dumps(
                {"hostname": "worker-01", "state": "Active", "health": "Maintenance"}
            ),
        ),
        (
            "v.l.o.event",
            "uuid",
            "2018-01-31",
            "lavaserver",
            json.dumps({"message": "hello from the job", "job": "1245"}),
        ),
    ]
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5500",
            },
        ],
    )
    assert main() == 1  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Listening to tcp://lava.example.com:5500
\033[1;30m2018-01-29\033[0m \033[1;37mv.l.o.device\033[0m \033[32mlava-health\033[0m - [bbb-01] <bbb> state=Idle health=Good
\033[1;30m2018-01-29\033[0m \033[1;37mv.l.o.device\033[0m \033[32mlava-health\033[0m - [bbb-01] <bbb> state=Running health=Good for 1234
Invalid message: invalid message
Unknown error: pop from empty list
"""
    )


def test_events_listen_filter_2(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "events", "listen", "--filter", "device", "--filter", "worker"],
    )
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    DummySocket.data = [
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Idle",
                    "health": "Good",
                }
            ),
        ),
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Running",
                    "health": "Good",
                    "job": "1234",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1234",
                    "device": "bbb-01",
                    "state": "Running",
                    "health": "Unknown",
                    "description": "a nice job",
                }
            ),
        ),
        ("invalid message"),
        (
            "v.l.o.worker",
            "uuid",
            "2018-01-31",
            "admin",
            json.dumps(
                {"hostname": "worker-01", "state": "Active", "health": "Maintenance"}
            ),
        ),
        (
            "v.l.o.event",
            "uuid",
            "2018-01-31",
            "lavaserver",
            json.dumps({"message": "hello from the job", "job": "1245"}),
        ),
    ]
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5500",
            },
        ],
    )
    assert main() == 1  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Listening to tcp://lava.example.com:5500
\033[1;30m2018-01-29\033[0m \033[1;37mv.l.o.device\033[0m \033[32mlava-health\033[0m - [bbb-01] <bbb> state=Idle health=Good
\033[1;30m2018-01-29\033[0m \033[1;37mv.l.o.device\033[0m \033[32mlava-health\033[0m - [bbb-01] <bbb> state=Running health=Good for 1234
Invalid message: invalid message
\033[1;30m2018-01-31\033[0m \033[1;37mv.l.o.worker\033[0m \033[32madmin\033[0m - [worker-01] state=Active health=Maintenance
Unknown error: pop from empty list
"""
    )


def test_events_wait_device(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "events", "wait", "device", "bbb-02"])
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    DummySocket.data = [
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Idle",
                    "health": "Good",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1234",
                    "device": "bbb-01",
                    "state": "Running",
                    "health": "Unknown",
                    "description": "a nice job",
                }
            ),
        ),
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-02",
                    "device_type": "bbb",
                    "state": "Running",
                    "health": "Good",
                    "job": "1234",
                }
            ),
        ),
    ]
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5500",
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "Listening to tcp://lava.example.com:5500\n"
    )
    assert DummySocket.data == []  # nosec


def test_events_wait_device_state(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "events", "wait", "device", "bbb-01", "--state", "RUNNING"],
    )
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    DummySocket.data = [
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Idle",
                    "health": "Good",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1234",
                    "device": "bbb-01",
                    "state": "Running",
                    "health": "Unknown",
                    "description": "a nice job",
                }
            ),
        ),
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Running",
                    "health": "Good",
                    "job": "1234",
                }
            ),
        ),
    ]
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5500",
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "Listening to tcp://lava.example.com:5500\n"
    )
    assert DummySocket.data == []  # nosec


def test_events_wait_device_health(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(
        sys,
        "argv",
        ["lavacli", "events", "wait", "device", "bbb-01", "--health", "MAINTENANCE"],
    )
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    DummySocket.data = [
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Idle",
                    "health": "Good",
                }
            ),
        ),
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Idle",
                    "health": "Maintenance",
                }
            ),
        ),
    ]
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5500",
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "Listening to tcp://lava.example.com:5500\n"
    )
    assert DummySocket.data == []  # nosec


def test_events_wait_job(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "events", "wait", "job", "1234"])
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    DummySocket.data = [
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Idle",
                    "health": "Good",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1233",
                    "device": "bbb-01",
                    "state": "Running",
                    "health": "Unknown",
                    "description": "a nice job",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1234",
                    "device": "bbb-01",
                    "state": "Running",
                    "health": "Unknown",
                    "description": "a nice job",
                }
            ),
        ),
    ]
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5500",
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "Listening to tcp://lava.example.com:5500\n"
    )
    assert DummySocket.data == []  # nosec


def test_events_wait_worker(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "events", "wait", "worker", "worker-01"]
    )
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    DummySocket.data = [
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Idle",
                    "health": "Good",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1233",
                    "device": "bbb-01",
                    "state": "Running",
                    "health": "Unknown",
                    "description": "a nice job",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1234",
                    "device": "bbb-01",
                    "state": "Running",
                    "health": "Unknown",
                    "description": "a nice job",
                }
            ),
        ),
        (
            "v.l.o.worker",
            "uuid",
            "2018-01-31",
            "admin",
            json.dumps(
                {"hostname": "worker-02", "state": "Active", "health": "Maintenance"}
            ),
        ),
        (
            "v.l.o.worker",
            "uuid",
            "2018-01-31",
            "admin",
            json.dumps(
                {"hostname": "worker-01", "state": "Active", "health": "Maintenance"}
            ),
        ),
    ]
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5500",
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "Listening to tcp://lava.example.com:5500\n"
    )
    assert DummySocket.data == []  # nosec


def test_events_wait_worker_invalid_message(setup, monkeypatch, capsys, tmpdir):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "events", "wait", "worker", "worker-01"]
    )
    monkeypatch.setattr(zmq, "Context", lambda: DummyContext())
    DummySocket.data = [
        (
            "v.l.o.device",
            "uuid",
            "2018-01-29",
            "lava-health",
            json.dumps(
                {
                    "device": "bbb-01",
                    "device_type": "bbb",
                    "state": "Idle",
                    "health": "Good",
                }
            ),
        ),
        (
            "v.l.o.testjob",
            "uuid",
            "2018-01-30",
            "lava-health",
            json.dumps(
                {
                    "job": "1233",
                    "device": "bbb-01",
                    "state": "Running",
                    "health": "Unknown",
                    "description": "a nice job",
                }
            ),
        ),
        ("strange"),
        (
            "v.l.o.worker",
            "uuid",
            "2018-01-31",
            "admin",
            json.dumps(
                {"hostname": "worker-02", "state": "Active", "health": "Maintenance"}
            ),
        ),
        (
            "v.l.o.worker",
            "uuid",
            "2018-01-31",
            "admin",
            json.dumps(
                {"hostname": "worker-01", "state": "Active", "health": "Maintenance"}
            ),
        ),
    ]
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "scheduler.get_publisher_event_socket",
                "args": (),
                "ret": "tcp://*:5500",
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == "Listening to tcp://lava.example.com:5500\nInvalid message: strange\n"
    )
    assert DummySocket.data == []  # nosec
