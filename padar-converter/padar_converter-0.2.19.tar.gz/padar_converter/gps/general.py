import gpxpy
import gpxpy.gpx
import pandas as pd
import numpy as np


def convert_gpx(gpx_data):
    gpx = gpxpy.parse(gpx_data)
    rows = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                ts_str = point.time.strftime('%Y-%m-%d %H:%M:%S.%f')
                ts_str = ts_str[:-3]
                row = pd.DataFrame(data={
                    "HEADER_TIME_STAMP": [ts_str],
                    "START_TIME": [ts_str],
                    "LATITUDE": [point.latitude],
                    "LONGITUDE": [point.longitude],
                    "HEIGHT": [point.elevation],
                })
                rows.append(row)

    # concatenate as dataframe
    csv = pd.concat(rows)
    return csv


def convert_csv(gps_csv_data):
    output = pd.DataFrame()
    output['HEADER_TIME_STAMP'] = gps_csv_data['LOCAL DATE'] \
        .str.cat(gps_csv_data['LOCAL TIME'], sep=' ') \
        .str.cat(gps_csv_data['MS'].map(
            lambda x: str(x).strip()), sep='.') \
        .astype('datetime64[ms]') \
        .map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]).values
    output['START_TIME'] = output['HEADER_TIME_STAMP']
    output['LATITUDE'] = gps_csv_data['LATITUDE']
    output['LONGITUDE'] = gps_csv_data['LONGITUDE']
    output['HEIGHT'] = gps_csv_data['HEIGHT']
    output['SPEED'] = gps_csv_data['SPEED']
    output['QUALITY'] = gps_csv_data['VALID']
    return output
