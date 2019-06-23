import textwrap
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from haggregate import cli


class CliUsageErrorTestCase(TestCase):
    def setUp(self):
        runner = CliRunner()
        self.result = runner.invoke(cli.main, [])

    def test_exit_code(self):
        self.assertTrue(self.result.exit_code > 0)

    def test_error_message(self):
        self.assertIn("Usage: main [OPTIONS] CONFIGFILE", self.result.output)


class CliConfigFileNotFoundTestCase(TestCase):
    def setUp(self):
        runner = CliRunner()
        self.result = runner.invoke(cli.main, ["/nonexistent/nonexistent"])

    def test_exit_code(self):
        self.assertTrue(self.result.exit_code > 0)

    def test_error_message(self):
        self.assertIn("No such file or directory", self.result.output)


class CliNoTimeSeriesErrorTestCase(TestCase):
    def setUp(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.ini", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                        [General]
                        target_step = D
                        min_count = 10
                        missing_flag = MISSING
                        """
                    )
                )
            self.result = runner.invoke(cli.main, ["config.ini"])

    def test_exit_code(self):
        self.assertTrue(self.result.exit_code > 0)

    def test_error_messages(self):
        self.assertIn("No time series have been specified", self.result.output)


class CliTestCase(TestCase):
    @patch("haggregate.cli.HTimeseries", **{"return_value": "my timeseries"})
    @patch("haggregate.cli.regularize", return_value="regularized timeseries")
    @patch("haggregate.cli.aggregate")
    def setUp(self, mock_aggregate, mock_regularize, mock_htimeseries):
        self.mock_aggregate = mock_aggregate
        self.mock_regularize = mock_regularize
        self.mock_htimeseries = mock_htimeseries
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("config.ini", "w") as f:
                f.write(
                    textwrap.dedent(
                        """\
                        [General]
                        target_step = D
                        min_count = 10
                        missing_flag = MISSING

                        [MyTimeseries]
                        source_file = mytimeseries.hts
                        target_file = aggregatedtimeseries.hts
                        method = sum
                        """
                    )
                )
            open("mytimeseries.hts", "a").close()
            self.result = runner.invoke(cli.main, ["config.ini"])

    def test_exit_code(self):
        self.assertEqual(self.result.exit_code, 0)

    def test_read_source_file(self):
        self.assertEqual(self.mock_htimeseries.call_count, 1)

    def test_regularize_called_correctly(self):
        self.mock_regularize.assert_called_once_with(
            "my timeseries", new_date_flag="DATEINSERT"
        )

    def test_aggregate_called_correctly(self):
        self.mock_aggregate.assert_called_once_with(
            "regularized timeseries", "D", "sum", min_count=10, missing_flag="MISSING"
        )

    def test_wrote_target_file(self):
        self.assertEqual(self.mock_aggregate.return_value.write.call_count, 1)
