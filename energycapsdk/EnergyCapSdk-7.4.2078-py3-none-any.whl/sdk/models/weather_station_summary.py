# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class WeatherStationSummary(Model):
    """WeatherStationSummary.

    :param begin_date: Begin date for this weather station
     May differ from the begin date provided by the user if the most recent
     weather reading for this station was earlier.
    :type begin_date: datetime
    :param weather_station_id: Weather station ID
    :type weather_station_id: int
    :param weather_station_code: Weather station code
    :type weather_station_code: str
    :param weather_station_name: Weather station name
    :type weather_station_name: str
    :param base_weather_station_code: Source weather station code (if any)
    :type base_weather_station_code: str
    :param number_of_readings_imported: Number of readings imported
    :type number_of_readings_imported: int
    :param number_of_failed_readings: Number of readings failed to import
    :type number_of_failed_readings: int
    :param channel_id: Channel ID
    :type channel_id: int
    :param channel_code: Channel code
    :type channel_code: str
    :param channel_interval_in_seconds: Channel interval in seconds
    :type channel_interval_in_seconds: int
    """

    _attribute_map = {
        'begin_date': {'key': 'beginDate', 'type': 'iso-8601'},
        'weather_station_id': {'key': 'weatherStationId', 'type': 'int'},
        'weather_station_code': {'key': 'weatherStationCode', 'type': 'str'},
        'weather_station_name': {'key': 'weatherStationName', 'type': 'str'},
        'base_weather_station_code': {'key': 'baseWeatherStationCode', 'type': 'str'},
        'number_of_readings_imported': {'key': 'numberOfReadingsImported', 'type': 'int'},
        'number_of_failed_readings': {'key': 'numberOfFailedReadings', 'type': 'int'},
        'channel_id': {'key': 'channelId', 'type': 'int'},
        'channel_code': {'key': 'channelCode', 'type': 'str'},
        'channel_interval_in_seconds': {'key': 'channelIntervalInSeconds', 'type': 'int'},
    }

    def __init__(self, begin_date=None, weather_station_id=None, weather_station_code=None, weather_station_name=None, base_weather_station_code=None, number_of_readings_imported=None, number_of_failed_readings=None, channel_id=None, channel_code=None, channel_interval_in_seconds=None):
        super(WeatherStationSummary, self).__init__()
        self.begin_date = begin_date
        self.weather_station_id = weather_station_id
        self.weather_station_code = weather_station_code
        self.weather_station_name = weather_station_name
        self.base_weather_station_code = base_weather_station_code
        self.number_of_readings_imported = number_of_readings_imported
        self.number_of_failed_readings = number_of_failed_readings
        self.channel_id = channel_id
        self.channel_code = channel_code
        self.channel_interval_in_seconds = channel_interval_in_seconds
