import datetime as dt
import json
import os
import textwrap
from io import StringIO
from unittest import TestCase, mock, skipUnless

import pandas as pd
import requests
from htimeseries import HTimeseries

from enhydris_api_client import EnhydrisApiClient


def mock_session(**kwargs):
    """Mock requests.Session.

    Returns
        @mock.patch("requests.Session", modified_kwargs)

    However, it first tampers with kwargs in order to achieve the following:
    - It adds a leading "return_value." to the kwargs; so you don't need to specify,
      for example, "return_value.get.return_value", you just specify "get.return_value".
    - If kwargs doesn't contain "get.return_value.status_code", it adds
      a return code of 200. Likewise for post, put and patch. For delete it's 204.
    - If "get.return_value.status_code" is not between 200 and 399,
      then raise_for_status() will raise HTTPError. Likewise for the other methods.
    """
    for method in ("get", "post", "put", "patch", "delete"):
        default_value = 204 if method == "delete" else 200
        c = kwargs.setdefault(method + ".return_value.status_code", default_value)
        if c < 200 or c >= 400:
            method_side_effect = method + ".return_value.raise_for_status.side_effect"
            kwargs[method_side_effect] = requests.HTTPError
    for old_key in list(kwargs.keys()):
        kwargs["return_value." + old_key] = kwargs.pop(old_key)
    return mock.patch("requests.Session", **kwargs)


class SuccessfulLoginTestCase(TestCase):
    @mock_session(
        **{
            "get.return_value.cookies": {"csrftoken": "reallysecret"},
            "post.return_value.cookies": {"acookie": "a cookie value"},
        }
    )
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.client.login("admin", "topsecret")

    def test_makes_post_request(self):
        self.mock_requests_session.return_value.post.assert_called_once_with(
            "https://mydomain.com/api/auth/login/",
            data="username=admin&password=topsecret",
            allow_redirects=False,
        )


class FailedLoginTestCase(TestCase):
    @mock_session(**{"post.return_value.status_code": 404})
    def test_raises_exception_on_post_failure(self, mock_requests_session):
        self.client = EnhydrisApiClient("https://mydomain.com")
        with self.assertRaises(requests.HTTPError):
            self.client.login("admin", "topsecret")


class LoginWithEmptyUsernameTestCase(TestCase):
    @mock_session()
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.client.login("", "useless_password")

    def test_does_not_make_get_request(self):
        self.mock_requests_session.get.assert_not_called()

    def test_does_not_make_post_request(self):
        self.mock_requests_session.post.assert_not_called()


class GetStationTestCase(TestCase):
    @mock_session(**{"get.return_value.json.return_value": {"hello": "world"}})
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.data = self.client.get_station(42)

    def test_makes_request(self):
        self.mock_requests_session.return_value.get.assert_called_once_with(
            "https://mydomain.com/api/stations/42/"
        )

    def test_returns_data(self):
        self.assertEqual(self.data, {"hello": "world"})


class PostStationTestCase(TestCase):
    @mock_session(**{"post.return_value.json.return_value": {"id": 42}})
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.data = self.client.post_station(data={"location": "Syria"})

    def test_makes_request(self):
        self.mock_requests_session.return_value.post.assert_called_once_with(
            "https://mydomain.com/api/stations/", data={"location": "Syria"}
        )

    def test_returns_id(self):
        self.assertEqual(self.data, 42)


class PutStationTestCase(TestCase):
    @mock_session()
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.client.put_station(42, data={"location": "Syria"})

    def test_makes_request(self):
        self.mock_requests_session.return_value.put.assert_called_once_with(
            "https://mydomain.com/api/stations/42/", data={"location": "Syria"}
        )


class PatchStationTestCase(TestCase):
    @mock_session()
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.client.patch_station(42, data={"location": "Syria"})

    def test_makes_request(self):
        self.mock_requests_session.return_value.patch.assert_called_once_with(
            "https://mydomain.com/api/stations/42/", data={"location": "Syria"}
        )


class DeleteStationTestCase(TestCase):
    @mock_session()
    def test_makes_request(self, mock_requests_session):
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.client.delete_station(42)
        mock_requests_session.return_value.delete.assert_called_once_with(
            "https://mydomain.com/api/stations/42/"
        )

    @mock_session(**{"delete.return_value.status_code": 404})
    def test_raises_exception_on_error(self, mock_requests_delete):
        self.client = EnhydrisApiClient("https://mydomain.com")
        with self.assertRaises(requests.HTTPError):
            self.client.delete_station(42)


class GetTimeseriesTestCase(TestCase):
    @mock_session(**{"get.return_value.json.return_value": {"hello": "world"}})
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.data = self.client.get_timeseries(41, 42)

    def test_makes_request(self):
        self.mock_requests_session.return_value.get.assert_called_once_with(
            "https://mydomain.com/api/stations/41/timeseries/42/"
        )

    def test_returns_data(self):
        self.assertEqual(self.data, {"hello": "world"})


class GetStationOrTimeseriesErrorTestCase(TestCase):
    @mock_session(**{"get.return_value.status_code": 404})
    def setUp(self, mock_requests_session):
        self.client = EnhydrisApiClient("https://mydomain.com")

    def test_raises_exception_on_get_station_error(self):
        with self.assertRaises(requests.HTTPError):
            self.data = self.client.get_station(42)

    def test_raises_exception_on_get_timeseries_error(self):
        with self.assertRaises(requests.HTTPError):
            self.data = self.client.get_timeseries(41, 42)


class PostTimeseriesTestCase(TestCase):
    @mock_session(**{"post.return_value.json.return_value": {"id": 42}})
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.data = self.client.post_timeseries(41, data={"location": "Syria"})

    def test_makes_request(self):
        self.mock_requests_session.return_value.post.assert_called_once_with(
            "https://mydomain.com/api/stations/41/timeseries/",
            data={"location": "Syria"},
        )

    def test_returns_id(self):
        self.assertEqual(self.data, 42)


class FailedPostTimeseriesTestCase(TestCase):
    @mock_session(**{"post.return_value.status_code": 404})
    def setUp(self, mock_requests_session):
        self.client = EnhydrisApiClient("https://mydomain.com")

    def test_raises_exception_on_error(self):
        with self.assertRaises(requests.HTTPError):
            self.client.post_timeseries(41, data={"location": "Syria"})


class DeleteTimeseriesTestCase(TestCase):
    @mock_session()
    def test_makes_request(self, mock_requests_session):
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.client.delete_timeseries(41, 42)
        mock_requests_session.return_value.delete.assert_called_once_with(
            "https://mydomain.com/api/stations/41/timeseries/42/"
        )

    @mock_session(**{"delete.return_value.status_code": 404})
    def test_raises_exception_on_error(self, mock_requests_delete):
        self.client = EnhydrisApiClient("https://mydomain.com")
        with self.assertRaises(requests.HTTPError):
            self.client.delete_timeseries(41, 42)


test_timeseries_csv = textwrap.dedent(
    """\
    2014-01-01 08:00,11.0,
    2014-01-02 08:00,12.0,
    2014-01-03 08:00,13.0,
    2014-01-04 08:00,14.0,
    2014-01-05 08:00,15.0,
    """
)
test_timeseries_hts = HTimeseries(StringIO(test_timeseries_csv))
test_timeseries_csv_top = "".join(test_timeseries_csv.splitlines(keepends=True)[:-1])
test_timeseries_csv_bottom = test_timeseries_csv.splitlines(keepends=True)[-1]


class ReadTsDataTestCase(TestCase):
    @mock_session(**{"get.return_value.text": test_timeseries_csv})
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.data = self.client.read_tsdata(41, 42)

    def test_makes_request(self):
        self.mock_requests_session.return_value.get.assert_called_once_with(
            "https://mydomain.com/api/stations/41/timeseries/42/data/",
            params={"fmt": "hts", "start_date": None, "end_date": None},
        )

    def test_returns_data(self):
        pd.testing.assert_frame_equal(self.data.data, test_timeseries_hts.data)


class ReadTsDataWithStartAndEndDateTestCase(TestCase):
    @mock_session(**{"get.return_value.text": test_timeseries_csv})
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.data = self.client.read_tsdata(
            41,
            42,
            start_date=dt.datetime(2019, 6, 12, 0, 0),
            end_date=dt.datetime(2019, 6, 13, 15, 25),
        )

    def test_makes_request(self):
        self.mock_requests_session.return_value.get.assert_called_once_with(
            "https://mydomain.com/api/stations/41/timeseries/42/data/",
            params={
                "fmt": "hts",
                "start_date": "2019-06-12T00:00:00",
                "end_date": "2019-06-13T15:25:00",
            },
        )

    def test_returns_data(self):
        pd.testing.assert_frame_equal(self.data.data, test_timeseries_hts.data)


class ReadEmptyTsDataTestCase(TestCase):
    @mock_session(**{"get.return_value.text": ""})
    def test_returns_data(self, mock_requests_session):
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.data = self.client.read_tsdata(41, 42)
        pd.testing.assert_frame_equal(self.data.data, HTimeseries().data)


class ReadTsDataErrorTestCase(TestCase):
    @mock_session(**{"get.return_value.status_code": 404})
    def test_raises_exception_on_error(self, mock_requests_session):
        self.client = EnhydrisApiClient("https://mydomain.com")
        with self.assertRaises(requests.HTTPError):
            self.client.read_tsdata(41, 42)


class PostTsDataTestCase(TestCase):
    @mock_session()
    def test_makes_request(self, mock_requests_session):
        client = EnhydrisApiClient("https://mydomain.com")
        client.post_tsdata(41, 42, test_timeseries_hts)
        f = StringIO()
        test_timeseries_hts.data.to_csv(f, header=False)
        mock_requests_session.return_value.post.assert_called_once_with(
            "https://mydomain.com/api/stations/41/timeseries/42/data/",
            data={"timeseries_records": f.getvalue()},
        )

    @mock_session(**{"post.return_value.status_code": 404})
    def test_raises_exception_on_error(self, mock_requests_session):
        client = EnhydrisApiClient("https://mydomain.com")
        with self.assertRaises(requests.HTTPError):
            client.post_tsdata(41, 42, test_timeseries_hts)


class GetTsEndDateTestCase(TestCase):
    @mock_session(**{"get.return_value.text": test_timeseries_csv_bottom})
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        self.client = EnhydrisApiClient("https://mydomain.com")
        self.result = self.client.get_ts_end_date(41, 42)

    def test_makes_request(self):
        self.mock_requests_session.return_value.get.assert_called_once_with(
            "https://mydomain.com/api/stations/41/timeseries/42/bottom/"
        )

    def test_returns_date(self):
        self.assertEqual(self.result, dt.datetime(2014, 1, 5, 8, 0))


class GetTsEndDateErrorTestCase(TestCase):
    @mock_session(**{"get.return_value.status_code": 404})
    def test_checks_response_code(self, mock_requests_session):
        client = EnhydrisApiClient("https://mydomain.com")
        with self.assertRaises(requests.HTTPError):
            client.get_ts_end_date(41, 42)


class GetTsEndDateEmptyTestCase(TestCase):
    @mock_session(**{"get.return_value.text": ""})
    def test_returns_date(self, mock_requests_session):
        client = EnhydrisApiClient("https://mydomain.com")
        date = client.get_ts_end_date(41, 42)
        self.assertIsNone(date)


class UseAsContextManagerTestCase(TestCase):
    @mock_session()
    def setUp(self, mock_requests_session):
        self.mock_requests_session = mock_requests_session
        with EnhydrisApiClient("https://mydomain.com/") as api_client:
            api_client.get_station(42)

    def test_called_enter(self):
        self.mock_requests_session.return_value.__enter__.assert_called_once_with()

    def test_called_exit(self):
        self.assertEqual(
            len(self.mock_requests_session.return_value.__exit__.mock_calls), 1
        )

    def test_makes_request(self):
        self.mock_requests_session.return_value.get.assert_called_once_with(
            "https://mydomain.com/api/stations/42/"
        )


@skipUnless(
    os.getenv("ENHYDRIS_API_CLIENT_E2E_TEST"), "Set ENHYDRIS_API_CLIENT_E2E_TEST"
)
class EndToEndTestCase(TestCase):
    """End-to-end test against a real Enhydris instance.
    To execute this test, specify the ENHYDRIS_API_CLIENT_E2E_TEST environment variable
    like this:
        ENHYDRIS_API_CLIENT_E2E_TEST='
            {"base_url": "http://localhost:8001",
             "username": "admin",
             "password": "topsecret",
             "owner_id": 9,
             "stype_id": 1,
             "time_zone_id": 3,
             "unit_of_measurement_id": 18,
             "variable_id": 22
             }
        '
    This should point to an Enhydris server. Avoid using a production database for
    that; the testing functionality will write objects to the database. Although
    things are normally cleaned up (created objects will be deleted), id serial
    numbers will be affected and things might not be cleaned up if there is an error.

    It would be better to specify only base_url, username and password, and let the
    test create a user, a station type, a time zone, etc. However the Enhydris API
    currently does not allow creation of these types.
    """

    def setUp(self):
        v = json.loads(os.getenv("ENHYDRIS_API_CLIENT_E2E_TEST"))
        self.client = EnhydrisApiClient(v["base_url"])
        self.username = v["username"]
        self.password = v["password"]
        self.stype_id = v["stype_id"]
        self.owner_id = v["owner_id"]
        self.time_zone_id = v["time_zone_id"]
        self.unit_of_measurement_id = v["unit_of_measurement_id"]
        self.variable_id = v["variable_id"]

    def test_e2e(self):
        # Verify we are logged out
        r = self.client.session.get(
            self.client.base_url + "/admin/", allow_redirects=False
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["Location"], "/admin/login/?next=/admin/")

        # Login and verify we're logged on
        self.client.login(self.username, self.password)
        r = self.client.session.get(self.client.base_url + "/admin/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue("Log out" in r.text)

        # Create a station
        self.station_id = self.client.post_station(
            {
                "name": "My station",
                "is_automatic": True,
                "copyright_holder": "Joe User",
                "copyright_years": "2019",
                "point": "POINT(20.94565 39.12102)",
                "original_srid": 4326,
                "owner": self.owner_id,
            }
        )

        # Get the station
        station = self.client.get_station(self.station_id)
        self.assertEqual(station["id"], self.station_id)
        self.assertEqual(station["name"], "My station")

        # Create a time series and verify it was created
        self.timeseries_id = self.client.post_timeseries(
            self.station_id,
            data={
                "name": "Delete this time series",
                "gentity": self.station_id,
                "time_zone": self.time_zone_id,
                "unit_of_measurement": self.unit_of_measurement_id,
                "variable": self.variable_id,
            },
        )
        timeseries = self.client.get_timeseries(self.station_id, self.timeseries_id)
        self.assertEqual(timeseries["name"], "Delete this time series")

        # Post time series data
        self.client.post_tsdata(
            self.station_id, self.timeseries_id, test_timeseries_hts
        )

        # Get the last date and check it
        date = self.client.get_ts_end_date(self.station_id, self.timeseries_id)
        self.assertEqual(date, dt.datetime(2014, 1, 5, 8, 0))

        # Get all time series data and check it
        hts = self.client.read_tsdata(self.station_id, self.timeseries_id)
        pd.testing.assert_frame_equal(hts.data, test_timeseries_hts.data)

        # The other attributes should have been set too.
        self.assertTrue(hasattr(hts, "variable"))

        # Get part of the time series data and check it
        hts = self.client.read_tsdata(
            self.station_id,
            self.timeseries_id,
            start_date=dt.datetime(2014, 1, 3, 8, 0),
            end_date=dt.datetime(2014, 1, 4, 8, 0),
        )
        expected_result = HTimeseries(
            StringIO(
                textwrap.dedent(
                    """\
                    2014-01-03 08:00,13.0,
                    2014-01-04 08:00,14.0,
                    """
                )
            )
        )
        pd.testing.assert_frame_equal(hts.data, expected_result.data)

        # Delete the time series and verify
        self.client.delete_timeseries(self.station_id, self.timeseries_id)
        with self.assertRaises(requests.HTTPError):
            self.client.get_timeseries(self.station_id, self.timeseries_id)

        # Patch station and verify
        self.client.patch_station(self.station_id, {"name": "New name"})
        station = self.client.get_station(self.station_id)
        self.assertEqual(station["name"], "New name")
        self.assertEqual(station["is_automatic"], True)  # Remains as it was

        # Put station and verify
        self.client.put_station(
            self.station_id,
            {
                "name": "Newer name",
                "copyright_holder": "Joe User",
                "copyright_years": "2019",
                "point": "POINT(20.94565 39.12102)",
                "original_srid": 4326,
                "owner": self.owner_id,
            },
        )
        station = self.client.get_station(self.station_id)
        self.assertEqual(station["name"], "Newer name")
        self.assertEqual(station["is_automatic"], False)  # Has been reset

        # Delete station and verify
        self.client.delete_station(self.station_id)
        with self.assertRaises(requests.HTTPError):
            self.client.get_station(self.station_id)
