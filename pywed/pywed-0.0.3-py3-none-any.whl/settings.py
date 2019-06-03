import os
import json
import datetime
from wed.utils import DataType, Service


## List the remote path to the datasets.
# You Need to update it when adding new stuff
settings_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")
with open(settings_path) as settings_file:
    SETTINGS = json.load(settings_file)

def get_prefix(type: DataType, service: Service):
    return SETTINGS[str(type)][str(service)]['prefix']

def get_time_range(type: DataType, service: Service):
    range = SETTINGS[str(type)][str(service)]['range']['date']
    return {
        'min': datetime.datetime.strptime(range["min"], '%Y-%m-%d'),
        'max': datetime.datetime.strptime(range["max"], '%Y-%m-%d')
    }

# Default values
DEFAULT_BUCKET = "dice-weather-data"
DEFAULT_CACHE_PATH = os.environ['HOME'] + "/.wed-cache"
DEFAULT_SERVICES = {
    DataType.WIND: Service.ECMWF,
    DataType.WAVE: Service.ECMWF
}
