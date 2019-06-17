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
            'solar_radiation'
        )
    )
    
    return reader