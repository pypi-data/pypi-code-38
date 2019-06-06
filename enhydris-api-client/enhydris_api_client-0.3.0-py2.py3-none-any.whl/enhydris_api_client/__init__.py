from io import StringIO
from urllib.parse import urljoin

import iso8601
import requests
from htimeseries import HTimeseries


class EnhydrisApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

        # My understanding from requests' documentation is that when I make a post
        # request, it shouldn't be necessary to specify Content-Type:
        # application/x-www-form-urlencoded, and that requests adds the header
        # automatically. However, when running in Python 3, apparently requests does not
        # add the header (although it does convert the post data to
        # x-www-form-urlencoded format). This is why I'm specifying it explicitly.
        self.session.headers.update(
            {"Content-Type": "application/x-www-form-urlencoded"}
        )

    def login(self, username, password):
        if not username:
            return

        # Get a csrftoken
        login_url = urljoin(self.base_url, "api/auth/login/")
        data = "username={}&password={}".format(username, password)
        r = self.session.post(login_url, data=data, allow_redirects=False)
        r.raise_for_status()
        self.session.headers.update({"Authorization": "token " + r.json()["key"]})

    def get_station(self, station_id):
        url = urljoin(self.base_url, "api/stations/{}/".format(station_id))
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def get_timeseries(self, station_id, timeseries_id):
        url = urljoin(
            self.base_url,
            "api/stations/{}/timeseries/{}/".format(station_id, timeseries_id),
        )
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def post_timeseries(self, station_id, data):
        r = self.session.post(
            urljoin(self.base_url, "api/stations/{}/timeseries/".format(station_id)),
            data=data,
        )
        r.raise_for_status()
        return r.json()["id"]

    def delete_timeseries(self, station_id, timeseries_id):
        url = urljoin(
            self.base_url,
            "api/stations/{}/timeseries/{}/".format(station_id, timeseries_id),
        )
        r = self.session.delete(url)
        if r.status_code != 204:
            raise requests.HTTPError()

    def read_tsdata(self, station_id, timeseries_id):
        url = urljoin(
            self.base_url,
            "api/stations/{}/timeseries/{}/data/".format(station_id, timeseries_id),
        )
        r = self.session.get(url)
        r.raise_for_status()
        if r.text:
            return HTimeseries(StringIO(r.text))
        else:
            return HTimeseries()

    def post_tsdata(self, station_id, timeseries_id, ts):
        f = StringIO()
        ts.data.to_csv(f, header=False)
        url = urljoin(
            self.base_url,
            "api/stations/{}/timeseries/{}/data/".format(station_id, timeseries_id),
        )
        r = self.session.post(url, data={"timeseries_records": f.getvalue()})
        r.raise_for_status()
        return r.text

    def get_ts_end_date(self, station_id, timeseries_id):
        url = urljoin(
            self.base_url,
            "api/stations/{}/timeseries/{}/bottom/".format(station_id, timeseries_id),
        )
        r = self.session.get(url)
        r.raise_for_status()
        try:
            datestring = r.text.strip().split(",")[0]
            return iso8601.parse_date(datestring, default_timezone=None)
        except (IndexError, iso8601.ParseError):
            return None
