from collections.abc import Mapping
from pyoos.collectors.coops.coops_sos import CoopsSos
# from datetime import datetime

# import requests
# import pytz
# from datetime import datetime, timedelta

# kw = dict(minute=0, second=0, microsecond=0, tzinfo=pytz.utc)

# stop = datetime.utcnow()
# stop = stop.replace(**kw)
# start = stop - timedelta(days=6)


class TidalStations(Mapping):

    def __init__(self, datatype="VerifiedSixMinute"):
        self._storage = dict()
        self._collector = CoopsSos()
        self.__set_datatype(datatype)
        self.__set_sos_name()

    def __getitem__(self, key):
        return self._storage[key]

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage.keys())

    def fetch(self, station_id, start_date, end_date):
        # observations = []
        print(start_date)
        print(end_date)
        self.collector.features = [station_id]
        self.collector.start_date = start_date
        self.collector.end_date = end_date
        response = self.collector.raw(responseFormat="text/csv")
        print(response)
        self.collector.features = None
        self.collector.start_date = None
        self.collector.end_date = None

        #     kw = dict(parse_dates=True, index_col='date_time')
        #     data = read_csv(BytesIO(response.encode('utf-8')), **kw).reset_index()
        #     data = data.drop_duplicates(subset='date_time').set_index('date_time')

        #     series = data[col]
        #     series._metadata = [dict(name=row['name'],
        #                              station=row['station_id'],
        #                              sensor=row['sensor_id'],
        #                              lon=row['longitude (degree)'],
        #                              lat=row['latitude (degree)'],)]

        #     observations.append(series)

        # self.collector

    def __set_datatype(self, datatype):
        assert datatype in self.collector.list_datatypes()
        self.collector.set_datatype(datatype)

    def __set_sos_name(self):
        self.collector.variables \
            = ['water_surface_height_above_reference_datum']

    @property
    def collector(self):
        return self._collector

    @property
    def _collector(self):
        return self.__collector

    @_collector.setter
    def _collector(self, collector):
        assert isinstance(collector, CoopsSos)
        self.__collector = collector
