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
import yaml

from lavacli import main


def test_results_job(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testjob_results_yaml",
                "args": ("1234",),
                "ret": yaml.dump(
                    [
                        {"suite": "lava", "name": "validate", "result": "pass"},
                        {"suite": "lava", "name": "job", "result": "fail"},
                    ]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Results:
* lava.validate [pass]
* lava.job [fail]
"""
    )


def test_results_job_isatty(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234"])
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testjob_results_yaml",
                "args": ("1234",),
                "ret": yaml.dump(
                    [
                        {"suite": "lava", "name": "validate", "result": "pass"},
                        {"suite": "lava", "name": "boot", "result": "skip"},
                        {"suite": "lava", "name": "job", "result": "fail"},
                    ]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Results:
* lava.validate [\033[1;32mpass\033[0m]
* lava.boot [skip]
* lava.job [\033[1;31mfail\033[0m]
"""
    )


def test_results_job_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testjob_results_yaml",
                "args": ("1234",),
                "ret": yaml.dump(
                    [
                        {"suite": "lava", "name": "validate", "result": "pass"},
                        {"suite": "lava", "name": "job", "result": "fail"},
                    ]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == [  # nosec
        {"name": "validate", "result": "pass", "suite": "lava"},
        {"name": "job", "result": "fail", "suite": "lava"},
    ]


def test_results_job_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testjob_results_yaml",
                "args": ("1234",),
                "ret": yaml.dump(
                    [
                        {"suite": "lava", "name": "validate", "result": "pass"},
                        {"suite": "lava", "name": "job", "result": "fail"},
                    ]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """- {name: validate, result: pass, suite: lava}
- {name: job, result: fail, suite: lava}
"""
    )


def test_results_suite(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234", "lava"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testsuite_results_yaml",
                "args": ("1234", "lava"),
                "ret": yaml.dump(
                    [
                        {"suite": "lava", "name": "validate", "result": "pass"},
                        {"suite": "lava", "name": "job", "result": "fail"},
                    ]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """Results:
* lava.validate [pass]
* lava.job [fail]
"""
    )


def test_results_suite_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234", "lava", "--json"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testsuite_results_yaml",
                "args": ("1234", "lava"),
                "ret": yaml.dump(
                    [
                        {"suite": "lava", "name": "validate", "result": "pass"},
                        {"suite": "lava", "name": "job", "result": "fail"},
                    ]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == [  # nosec
        {"name": "validate", "result": "pass", "suite": "lava"},
        {"name": "job", "result": "fail", "suite": "lava"},
    ]


def test_results_suite_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234", "lava", "--yaml"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testsuite_results_yaml",
                "args": ("1234", "lava"),
                "ret": yaml.dump(
                    [
                        {"suite": "lava", "name": "validate", "result": "pass"},
                        {"suite": "lava", "name": "job", "result": "fail"},
                    ]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0]
        == """- {name: validate, result: pass, suite: lava}
- {name: job, result: fail, suite: lava}
"""
    )


def test_results_case(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234", "lava", "validate"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testcase_results_yaml",
                "args": ("1234", "lava", "validate"),
                "ret": yaml.dump(
                    [{"suite": "lava", "name": "validate", "result": "pass"}]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "pass\n"  # nosec


def test_results_case_isatty_pass(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234", "lava", "validate"])
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testcase_results_yaml",
                "args": ("1234", "lava", "validate"),
                "ret": yaml.dump(
                    [{"suite": "lava", "name": "validate", "result": "pass"}]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "\033[1;32mpass\033[0m\n"  # nosec


def test_results_case_isatty_fail(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234", "lava", "validate"])
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testcase_results_yaml",
                "args": ("1234", "lava", "validate"),
                "ret": yaml.dump(
                    [{"suite": "lava", "name": "validate", "result": "fail"}]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "\033[1;31mfail\033[0m\n"  # nosec


def test_results_case_isatty_skip(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234", "lava", "validate"])
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testcase_results_yaml",
                "args": ("1234", "lava", "validate"),
                "ret": yaml.dump(
                    [{"suite": "lava", "name": "validate", "result": "skip"}]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "skip\n"  # nosec


def test_results_case_1(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "results", "1234", "lava", "validate"])
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testcase_results_yaml",
                "args": ("1234", "lava", "validate"),
                "ret": yaml.dump(
                    [
                        {"suite": "lava", "name": "validate", "result": "pass"},
                        {"suite": "lava", "name": "validate", "result": "fail"},
                    ]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "pass\nfail\n"  # nosec


def test_results_case_json(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "results", "1234", "lava", "validate", "--json"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testcase_results_yaml",
                "args": ("1234", "lava", "validate"),
                "ret": yaml.dump(
                    [{"suite": "lava", "name": "validate", "result": "pass"}]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert json.loads(capsys.readouterr()[0]) == [  # nosec
        {"name": "validate", "result": "pass", "suite": "lava"}
    ]


def test_results_case_yaml(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(
        sys, "argv", ["lavacli", "results", "1234", "lava", "validate", "--yaml"]
    )
    monkeypatch.setattr(
        xmlrpc.client.ServerProxy,
        "data",
        [
            {"request": "system.version", "args": (), "ret": version},
            {
                "request": "results.get_testcase_results_yaml",
                "args": ("1234", "lava", "validate"),
                "ret": yaml.dump(
                    [{"suite": "lava", "name": "validate", "result": "pass"}]
                ),
            },
        ],
    )
    assert main() == 0  # nosec
    assert (  # nosec
        capsys.readouterr()[0] == "- {name: validate, result: pass, suite: lava}\n"
    )
