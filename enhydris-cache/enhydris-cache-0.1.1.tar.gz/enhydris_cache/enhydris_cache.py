import datetime as dt

from enhydris_api_client import EnhydrisApiClient
from htimeseries import HTimeseries


class TimeseriesCache(object):
    def __init__(self, timeseries_group):
        self.timeseries_group = timeseries_group

    def update(self):
        for item in self.timeseries_group:
            self.base_url = item["base_url"]
            if self.base_url[-1] != "/":
                self.base_url += "/"
            self.station_id = item["station_id"]
            self.timeseries_id = item["timeseries_id"]
            self.user = item["user"]
            self.password = item["password"]
            self.filename = item["file"]
            self._update_for_one_timeseries()

    def _update_for_one_timeseries(self):
        cached_ts = self._read_timeseries_from_cache_file()
        end_date = self._get_timeseries_end_date(cached_ts)
        start_date = end_date + dt.timedelta(minutes=1)
        new_ts = self._append_newer_timeseries(start_date, cached_ts)
        with open(self.filename, "w", encoding="utf-8") as f:
            new_ts.write(f, format=HTimeseries.FILE)

    def _read_timeseries_from_cache_file(self):
        try:
            with open(self.filename, newline="\n") as f:
                return HTimeseries(f)
        except (FileNotFoundError, ValueError):
            # If file is corrupted or nonexistent, continue with empty time series
            return HTimeseries()

    def _get_timeseries_end_date(self, timeseries):
        try:
            end_date = timeseries.data.index[-1]
        except IndexError:
            # Timeseries is totally empty; no start and end date
            end_date = dt.datetime(1, 1, 1, 0, 0)
        return end_date

    def _append_newer_timeseries(self, start_date, old_ts):
        with EnhydrisApiClient(self.base_url) as api_client:
            api_client.login(self.user, self.password)
            ts = api_client.read_tsdata(
                self.station_id, self.timeseries_id, start_date=start_date
            )
            new_data = ts.data
            ts.data = old_ts.data.append(new_data, verify_integrity=True, sort=False)
        return ts
