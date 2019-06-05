import os
import json
import datetime
from wed.utils import DataType, Service

# ---- Constants
## List the remote path to the datasets.
# You Need to update it when adding new stuff
settings_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")
with open(settings_path) as settings_file:
    SETTINGS = json.load(settings_file)

# Default values
DEFAULT_BUCKET = "dice-weather-data"
DEFAULT_CACHE_PATH = os.environ['HOME'] + "/.wed-cache"
DEFAULT_SERVICES = {
    DataType.WIND: Service.ECMWF,
    DataType.WAVE: Service.ECMWF
}
# ---- /Constants

class Settings:
    """Singleton used to store and modify wed settings"""
    class __Settings:
        def __init__(self):
            self.bucket = DEFAULT_BUCKET
            self.services = DEFAULT_SERVICES
            self.local_cache_path = DEFAULT_CACHE_PATH
            self.latitude_precision = None
            self.longitude_precision = None
            self.time_precision = None

    instance = None
    def __init__(self):
        if not Settings.instance:
            Settings.instance = Settings.__Settings()

    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name, value):
        setattr(self.instance, name, value)


def get_prefix(type: DataType, service: Service):
    return SETTINGS[str(type)][str(service)]['prefix']

def get_time_range(type: DataType):
    service = Settings().services[type]
    range = SETTINGS[str(type)][str(service)]['range']['date']
    return {
        'min': datetime.datetime.strptime(range["min"], '%Y-%m-%d'),
        'max': datetime.datetime.strptime(range["max"], '%Y-%m-%d')
    }

def get_coordinate_range(type: DataType, service: Service):
    lat_range = SETTINGS[str(type)][str(service)]['range']['latitude']
    lon_range = SETTINGS[str(type)][str(service)]['range']['longitude']
    return {
        "latitude": lat_range,
        "longitude": lon_range
    }
