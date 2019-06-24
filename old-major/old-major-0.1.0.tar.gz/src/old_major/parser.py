import csv
import json


def parse(data):
    f = open(data, 'r')
    reader = csv.DictReader(
        f,
        fieldnames=(
            'moisture1',
            'moisture2',
            'moisture3',
            'temperature',
            'wind_direction',
            'rainfall',
            'wind_speed',
            'air_humidity',
            'air_temperature',
            'air_pressure',
            'radiation'
        )
    )
    str_out = json.dumps([row for row in reader])
    data_json = json.loads(str_out)[0]
    
    result = {
        'soil': {
            'moisture1': data_json['moisture1'],
            'moisture2': data_json['moisture2'],
            'moisture3': data_json['moisture3'],
            'temprature': data_json['temperature']
        },
        'air': {
            'humidity': data_json['air_humidity'],
            'temperature': data_json['air_temperature'],
            'pressure': data_json['air_pressure']
        },
        'wind': {
            'speed': data_json['wind_speed'],
            'direction': data_json['wind_direction'],
        },
        'rain': {
            'rainfall': data_json['rainfall']
        },
        'solar': {
            'radiation': data_json['radiation']
        },
        'actuator': {
            'status': False
        }
    }

    return result
