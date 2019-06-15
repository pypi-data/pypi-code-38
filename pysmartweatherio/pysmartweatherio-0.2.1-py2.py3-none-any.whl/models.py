import datetime

import requests

from .utils import Conversion, PropertyUnavailable, UnicodeMixin


class StationData(UnicodeMixin):
    def __init__(self, data, response, headers, units):
        self.response = response
        self.http_headers = headers
        self.json = data
        self.units = units.lower()

        self._alerts = []
        for alertJSON in self.json.get('alerts', []):
            self._alerts.append(Alert(alertJSON))

    def update(self):
        r = requests.get(self.response.url)
        self.json = r.json()
        self.response = r

    def currentdata(self):
        dtformat = datetime.datetime.fromtimestamp(self.json['obs'][0]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        # If SKY module is present convert values else 0
        if 'precip' not in self.json['obs'][0]:
            feels_like = 0
            wind_avg = 0
            wind_bearing = 0
            wind_direction = "N"
            wind_gust = 0
            wind_lull = 0
            uv = 0
            precip_accum_local_day = 0
            precip_rate = 0
            precip = 0
            wind_chill = 0
            precip_accum_last_1hr = 0
            precip_accum_last_24hr = 0
            solar_radiation = 0
            brightness = 0
            precip_accum_local_yesterday = 0
        else:
            feels_like = self.json['obs'][0]['feels_like']
            wind_avg = Conversion.speed(float(self.json['obs'][0]['wind_avg']), self.units)
            wind_bearing = int(self.json['obs'][0]['wind_direction'])
            wind_direction = Conversion.wind_direction(self.json['obs'][0]['wind_direction'])
            wind_gust = Conversion.speed(float(self.json['obs'][0]['wind_gust']), self.units)
            wind_lull = Conversion.speed(float(self.json['obs'][0]['wind_lull']), self.units)
            uv = float(self.json['obs'][0]['uv'])
            precip_accum_local_day = Conversion.volume(float(self.json['obs'][0]['precip_accum_local_day']), self.units)
            precip_rate = Conversion.rate(float(self.json['obs'][0]['precip']), self.units)
            precip = float(self.json['obs'][0]['precip'])
            wind_chill = self.json['obs'][0]['wind_chill']
            precip_accum_last_1hr = Conversion.volume(float(self.json['obs'][0]['precip_accum_last_1hr']), self.units)
            # precip_accum_last_24hr = Conversion.volume(float(self.json['obs'][0]['precip_accum_last_24hr']), self.units)
            solar_radiation = int(self.json['obs'][0]['solar_radiation'])
            brightness = int(self.json['obs'][0]['brightness'])
            if 'precip_accum_local_yesterday' not in self.json['obs'][0]:
                precip_accum_local_yesterday = 0
            else:
                precip_accum_local_yesterday = Conversion.volume(float(self.json['obs'][0]['precip_accum_local_yesterday']), self.units)

        # If AIR module is present convert values else 0
        if 'air_temperature' not in self.json['obs'][0]:
            air_temperature = 0
            relative_humidity = 0
            station_pressure = 0
            heat_index = 0
            dew_point = 0
            lightning_strike_count = 0
            lightning_strike_count_last_3hr = 0
            lightning_strike_last_distance = 0
            lightning_strike_last_epoch = "1970-01-01 00:00:00"
        else:
            air_temperature = self.json['obs'][0]['air_temperature']
            relative_humidity = int(self.json['obs'][0]['relative_humidity'])
            station_pressure = Conversion.pressure(float(self.json['obs'][0]['station_pressure']), self.units)
            heat_index = self.json['obs'][0]['heat_index']
            dew_point = self.json['obs'][0]['dew_point']
            lightning_strike_count = int(self.json['obs'][0]['lightning_strike_count'])
            lightning_strike_count_last_3hr = int(self.json['obs'][0]['lightning_strike_count_last_3hr'])
            if 'lightning_strike_last_distance' not in self.json['obs'][0]:
                lightning_strike_last_distance = 0
            else:
                lightning_strike_last_distance = Conversion.distance(self.json['obs'][0]['lightning_strike_last_distance'], self.units)
            if 'lightning_strike_last_epoch' not in self.json['obs'][0]:
                lightning_strike_last_epoch = "1970-01-01 00:00:00"
            else:
                lightning_strike_last_epoch = datetime.datetime.fromtimestamp(self.json['obs'][0]['lightning_strike_last_epoch']).strftime('%Y-%m-%d %H:%M:%S')

        return CurrentData(
            self.json['station_name'],
            dtformat,
            air_temperature,
            feels_like,
            wind_avg,
            wind_bearing,
            wind_direction,
            wind_gust,
            wind_lull,
            uv,
            precip_accum_local_day,
            relative_humidity,
            precip_rate,
            precip,
            station_pressure,
            float(self.json['latitude']),
            float(self.json['longitude']),
            heat_index,
            wind_chill,
            dew_point,
            precip_accum_last_1hr,
            precip_accum_local_yesterday,
            solar_radiation,
            brightness,
            lightning_strike_last_epoch,
            lightning_strike_last_distance,
            lightning_strike_count,
            lightning_strike_count_last_3hr
            )

class DeviceData(UnicodeMixin):
    def __init__(self, data, response, headers, units):
        self.response = response
        self.http_headers = headers
        self.json = data
        self.units = units.lower()

        self._alerts = []
        for alertJSON in self.json.get('alerts', []):
            self._alerts.append(Alert(alertJSON))

    def update(self):
        r = requests.get(self.response.url)
        self.json = r.json()
        self.response = r

    def devicedata(self):
        """ Read Device Data from the Returned JSON. """
        if self.json['type'] == 'obs_sky':
            dtformat = datetime.datetime.fromtimestamp(self.json['obs'][0][0]).strftime('%Y-%m-%d %H:%M:%S')
            return DeviceSkyData(
                dtformat,
                self.json['obs'][0][8]
            )
        elif self.json['type'] == 'obs_air':
            dtformat = datetime.datetime.fromtimestamp(self.json['obs'][0][0]).strftime('%Y-%m-%d %H:%M:%S')
            return DeviceAirData(
                dtformat,
                self.json['obs'][0][8]
            )
        else:
            return None

class Alert(UnicodeMixin):
    def __init__(self, json):
        self.json = json

    def __getattr__(self, name):
        try:
            return self.json[name]
        except KeyError:
            raise PropertyUnavailable(
                "Property '{}' is not valid"
                " or is not available".format(name)
            )

    def __unicode__(self):
        return '<Alert instance: {0} at {1}>'.format(self.title, self.time)

class CurrentData:
    """ Returns an Array with Current Weather Observations. """
    def __init__(self, station_location, timestamp, temperature, feels_like, wind_speed, wind_bearing, wind_direction, wind_gust, wind_lull,
                 uv, precipitation,humidity, precipitation_rate, rain_rate_raw, pressure, latitude, longitude, heat_index, wind_chill, dewpoint,
                 precipitation_last_1hr, precipitation_last_24hr, precipitation_yesterday, solar_radiation, brightness,lightning_time,
                 lightning_distance, lightning_count,lightning_count_3hour
                 ):
        self.station_location = station_location
        self.timestamp = timestamp
        self.temperature = temperature
        self.feels_like_temperature = feels_like
        self.wind_speed = wind_speed
        self.wind_bearing = wind_bearing
        self.wind_direction = wind_direction
        self.wind_gust = wind_gust
        self.wind_lull = wind_lull
        self.uv = uv
        self.precipitation = precipitation
        self.humidity = humidity
        self.precipitation_rate = precipitation_rate * 60
        self.pressure = pressure
        self.latitude = latitude
        self.longitude = longitude
        self.heat_index = heat_index
        self.wind_chill = wind_chill
        self.dewpoint = dewpoint
        self.precipitation_last_1hr = precipitation_last_1hr
        self.precipitation_last_24hr = precipitation_last_24hr
        self.precipitation_yesterday = precipitation_yesterday
        self.solar_radiation = solar_radiation
        self.illuminance = brightness
        self.lightning_time = lightning_time
        self.lightning_distance = lightning_distance
        self.lightning_count = lightning_count
        self.lightning_last_3hr = lightning_count_3hour

        """ Binary Sensor Values """
        self.raining = True if rain_rate_raw > 0 else False
        self.freezing = True if temperature < 0 else False
        self.lightning = True if lightning_count > 0 else False

class DeviceSkyData:
    """ Returns an Array with data from a SKY module. """
    def __init__(self, timestamp, battery):
        self.timestamp = timestamp
        self.battery = battery

class DeviceAirData:
    """ Returns an Array with data from a AIR module. """
    def __init__(self, timestamp, battery):
        self.timestamp = timestamp
        self.battery = battery
