import requests

from .models import DeviceData, StationData


def _urlstation(stationid, apikey):
    return "https://swd.weatherflow.com/swd/rest/observations/station/{}?api_key={}".format(stationid, apikey)
#    return 'https://swd.weatherflow.com/swd/rest/observations/station/' + str(stationid) + '?api_key=' + str(apikey)

def _urldevice(deviceid, apikey):
    return "https://swd.weatherflow.com/swd/rest/observations/device/{}?api_key={}".format(deviceid, apikey)

def load_stationdata(stationid, apikey, units='metric', callback=None):
    """
    This Function builds the URL and returns the
    data from WeatherFlow. You will need to supply a Station Id and
    if you don't have your own station, you can find a list of public
    available stations here: https://smartweather.weatherflow.com/map
    """

    return get_weather(_urlstation(stationid, apikey), units)

def load_devicedata(deviceid, apikey, units='metric', callback=None):
    """
    This Function builds the URL and returns the
    data from WeatherFlow. You will need to supply a Device Id and
    if you don't have your own station, you can find a list of public
    available stations here: https://smartweather.weatherflow.com/map
    """

    return get_device(_urldevice(deviceid, apikey), units)

def get_weather(requestURL, units):
    data_reponse = requests.get(requestURL)
    data_reponse.raise_for_status()

    json = data_reponse.json()
    headers = data_reponse.headers

    return StationData(json, data_reponse, headers, units)

def get_device(requestURL, units):
    data_reponse = requests.get(requestURL)
    data_reponse.raise_for_status()

    json = data_reponse.json()
    headers = data_reponse.headers

    return DeviceData(json, data_reponse, headers, units)
