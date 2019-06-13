import json
import os
import shutil
import sys
import tempfile
import textwrap
from io import StringIO
from unittest import TestCase, skipUnless
from unittest.mock import patch

import click
from click.testing import CliRunner
from enhydris_api_client import EnhydrisApiClient
from htimeseries import HTimeseries

from enhydris_cache import cli


class NonExistentConfigFileTestCase(TestCase):
    def setUp(self):
        runner = CliRunner(mix_stderr=False)
        self.result = runner.invoke(cli.main, ["nonexistent.conf"])

    def test_exit_status(self):
        self.assertEqual(self.result.exit_code, 1)

    def test_error_message(self):
        self.assertIn(
            "No such file or directory: 'nonexistent.conf'", self.result.stderr
        )


class ConfigurationTestCase(TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.configfilename = os.path.join(self.tempdir, "enhydris-cache.conf")

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_nonexistent_log_level_raises_error(self):
        with open(self.configfilename, "w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    [General]
                    loglevel = HELLO
                    """
                )
            )
        msg = "loglevel must be one of ERROR, WARNING, INFO, DEBUG"
        with self.assertRaisesRegex(click.ClickException, msg):
            cli.App(self.configfilename).run()

    def test_missing_base_url_parameter_raises_error(self):
        with open(self.configfilename, "w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    [General]
                    loglevel = WARNING

                    [Temperature]
                    station_id = 585
                    timeseries_id = 5858
                    file = /tmp/temperature.hts
                    """
                )
            )
        msg = "No option 'base_url'"
        with self.assertRaisesRegex(click.ClickException, msg):
            cli.App(self.configfilename).run()

    def test_missing_station_id_parameter_raises_error(self):
        with open(self.configfilename, "w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    [General]
                    loglevel = WARNING

                    [Temperature]
                    base_url = https://openmeteo.org/
                    timeseries_id = 5858
                    file = /tmp/temperature.hts
                    """
                )
            )
        msg = "No option 'station_id'"
        with self.assertRaisesRegex(click.ClickException, msg):
            cli.App(self.configfilename).run()

    def test_missing_timeseries_id_parameter_raises_error(self):
        with open(self.configfilename, "w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    [General]
                    loglevel = WARNING

                    [Temperature]
                    base_url = https://openmeteo.org/
                    station_id = 585
                    file = /tmp/temperature.hts
                    """
                )
            )
        msg = "No option 'timeseries_id'"
        with self.assertRaisesRegex(click.ClickException, msg):
            cli.App(self.configfilename).run()

    def test_missing_file_parameter_raises_error(self):
        with open(self.configfilename, "w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    [General]
                    loglevel = WARNING

                    [Temperature]
                    base_url = https://openmeteo.org/
                    station_id = 585
                    timeseries_id = 5858
                    """
                )
            )
        msg = "No option 'file'"
        with self.assertRaisesRegex(click.ClickException, msg):
            cli.App(self.configfilename).run()

    def test_wrong_station_id_parameter_raises_error(self):
        with open(self.configfilename, "w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    [General]
                    loglevel = WARNING

                    [Temperature]
                    base_url = https://openmeteo.org/
                    station_id = hello
                    timeseries_id = 5858
                    file = /tmp/temperature.hts
                    """
                )
            )
        with self.assertRaisesRegex(click.ClickException, "not a valid integer"):
            cli.App(self.configfilename).run()

    def test_wrong_timeseries_id_parameter_raises_error(self):
        with open(self.configfilename, "w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    [General]
                    loglevel = WARNING

                    [Temperature]
                    base_url = https://openmeteo.org/
                    station_id = 585
                    timeseries_id = hello
                    file = /tmp/temperature.hts
                    """
                )
            )
        with self.assertRaisesRegex(click.ClickException, "not a valid integer"):
            cli.App(self.configfilename).run()

    @patch("enhydris_cache.cli.App._execute")
    def test_correct_configuration_executes(self, m):
        with open(self.configfilename, "w") as f:
            f.write(
                """\
                    [General]
                    loglevel = WARNING

                    [Temperature]
                    base_url = https://openmeteo.org/
                    station_id = 585
                    timeseries_id = 5850
                    file = /tmp/temperature.hts
                    """
            )
        cli.App(self.configfilename).run()
        m.assert_called_once_with()

    @patch("enhydris_cache.cli.App._execute")
    def test_creates_log_file(self, *args):
        logfilename = os.path.join(self.tempdir, "enhydris_cache.log")
        with open(self.configfilename, "w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    [General]
                    logfile = {}
                    loglevel = WARNING

                    [Temperature]
                    base_url = https://openmeteo.org/
                    station_id = 585
                    timeseries_id = 5850
                    file = /tmp/temperature.hts
                    """.format(
                        logfilename
                    )
                )
            )
        cli.App(self.configfilename).run()
        self.assertTrue(os.path.exists(logfilename))


@skipUnless(os.getenv("ENHYDRIS_CACHE_E2E_TEST"), "set ENHYDRIS_CACHE_E2E_TEST")
class EnhydrisCacheE2eTestCase(TestCase):
    test_timeseries1 = textwrap.dedent(
        """\
        2014-01-01 08:00,11,
        2014-01-02 08:00,12,
        2014-01-03 08:00,13,
        2014-01-04 08:00,14,
        2014-01-05 08:00,15,
        """
    )
    test_timeseries2 = textwrap.dedent(
        """\
        2014-07-01 08:00,9.11,
        2014-07-02 08:00,9.12,
        2014-07-03 08:00,9.13,
        2014-07-04 08:00,9.14,
        2014-07-05 08:00,9.15,
        """
    )
    timeseries1_top = "".join(test_timeseries1.splitlines(True)[:-1])
    timeseries2_top = "".join(test_timeseries2.splitlines(True)[:-1])
    timeseries1_bottom = test_timeseries1.splitlines(True)[-1]
    timeseries2_bottom = test_timeseries2.splitlines(True)[-1]

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.tempdir, "enhydris_cache.conf")
        self.saved_argv = sys.argv
        sys.argv = ["enhydris_cache", "--traceback", self.config_file]
        self.savedcwd = os.getcwd()

        # Create two stations, each one with a time series
        self.parms = json.loads(os.getenv("ENHYDRIS_CACHE_E2E_TEST"))
        self.api_client = EnhydrisApiClient(self.parms["base_url"])
        self.api_client.__enter__()
        with self.api_client.session:
            self.api_client.login(self.parms["user"], self.parms["password"])
            self.station1_id = self.api_client.post_station(
                {
                    "name": "station1",
                    "original_srid": 4326,
                    "point": "POINT (23.78743 37.97385)",
                    "copyright_holder": "Joe User",
                    "copyright_years": "2014",
                    "stype": 1,
                    "owner": self.parms["owner_id"],
                }
            )
            self.timeseries1_id = self.api_client.post_timeseries(
                self.station1_id,
                {
                    "gentity": self.station1_id,
                    "variable": self.parms["variable_id"],
                    "unit_of_measurement": self.parms["unit_of_measurement_id"],
                    "time_zone": self.parms["time_zone_id"],
                    "precision": 0,
                    "time_step": 3,
                    "timestamp_offset_minutes": 0,
                    "timestamp_offset_months": 0,
                },
            )
            self.station2_id = self.api_client.post_station(
                {
                    "name": "station1",
                    "original_srid": 4326,
                    "point": "POINT (24.56789 38.76543)",
                    "copyright_holder": "Joe User",
                    "copyright_years": "2014",
                    "stype": 1,
                    "owner": self.parms["owner_id"],
                }
            )
            self.timeseries2_id = self.api_client.post_timeseries(
                self.station2_id,
                {
                    "gentity": self.station2_id,
                    "variable": self.parms["variable_id"],
                    "unit_of_measurement": self.parms["unit_of_measurement_id"],
                    "time_zone": self.parms["time_zone_id"],
                    "precision": 2,
                    "time_step": 3,
                    "timestamp_offset_minutes": 0,
                    "timestamp_offset_months": 0,
                },
            )

        # Add some data (all but the last record) to the database
        self.api_client.post_tsdata(
            self.station1_id,
            self.timeseries1_id,
            HTimeseries(StringIO(self.timeseries1_top)),
        )
        self.api_client.post_tsdata(
            self.station2_id,
            self.timeseries2_id,
            HTimeseries(StringIO(self.timeseries2_top)),
        )

        # Prepare a configuration file (some tests override it)
        with open(self.config_file, "w") as f:
            f.write(
                textwrap.dedent(
                    """\
                    [General]
                    cache_dir = {self.tempdir}

                    [timeseries1]
                    base_url = {base_url}
                    station_id = {self.station1_id}
                    timeseries_id = {self.timeseries1_id}
                    file = file1
                    user = {self.parms[user]}
                    password = {self.parms[password]}

                    [timeseries2]
                    base_url = {base_url}
                    station_id = {self.station2_id}
                    timeseries_id = {self.timeseries2_id}
                    file = file2
                    user = {self.parms[user]}
                    password = {self.parms[password]}
                    """
                ).format(self=self, base_url=self.parms["base_url"])
            )

    def tearDown(self):
        os.chdir(self.savedcwd)
        shutil.rmtree(self.tempdir)
        sys.argv = self.saved_argv
        self.api_client.__exit__()

    def test_execute(self):
        application = cli.App(self.config_file)

        # Check that the two files don't exist yet
        self.assertFalse(os.path.exists(os.path.join(self.tempdir, "file1")))
        self.assertFalse(os.path.exists(os.path.join(self.tempdir, "file2")))

        # Execute the application
        application.run()

        # Check that it has created two files
        self.assertTrue(os.path.exists(os.path.join(self.tempdir, "file1")))
        self.assertTrue(os.path.exists(os.path.join(self.tempdir, "file2")))

        # Check that the files are what they should be
        with open("file1", newline="\n") as f:
            ts1_before = HTimeseries(f)
        self.assertEqual(ts1_before.time_step, "1440,0")
        c = StringIO()
        ts1_before.write(c)
        self.assertEqual(c.getvalue().replace("\r", ""), self.timeseries1_top)
        with open("file2", newline="\n") as f:
            ts2_before = HTimeseries(f)
        self.assertEqual(ts2_before.time_step, "1440,0")
        c = StringIO()
        ts2_before.write(c)
        self.assertEqual(c.getvalue().replace("\r", ""), self.timeseries2_top)

        # Append a record to the database for each timeseries
        self.api_client.post_tsdata(
            self.station1_id,
            self.timeseries1_id,
            HTimeseries(StringIO(self.timeseries1_bottom)),
        )
        self.api_client.post_tsdata(
            self.station2_id,
            self.timeseries2_id,
            HTimeseries(StringIO(self.timeseries2_bottom)),
        )

        # Execute the application again
        application.run()

        # Check that the files are what they should be
        with open("file1", newline="\n") as f:
            ts1_after = HTimeseries(f)
        self.assertEqual(ts1_after.time_step, "1440,0")
        c = StringIO()
        ts1_after.write(c)
        self.assertEqual(c.getvalue().replace("\r", ""), self.test_timeseries1)
        with open("file2", newline="\n") as f:
            ts2_after = HTimeseries(f)
        self.assertEqual(ts2_after.time_step, "1440,0")
        c = StringIO()
        ts2_after.write(c)
        self.assertEqual(c.getvalue().replace("\r", ""), self.test_timeseries2)

        # Check that the time series comments are the same before and after
        self.assertEqual(ts1_before.comment, ts1_after.comment)
        self.assertEqual(ts2_before.comment, ts2_after.comment)
