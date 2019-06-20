import pandas as pd


def load_sensor(filepath):
    if filepath is None:
        return None
    result = pd.read_csv(filepath, parse_dates=[0], infer_datetime_format=True)
    result = result.rename(columns={result.columns[0]: 'HEADER_TIME_STAMP'})
    return result


def load_annotation(filepath):
    if filepath is None:
        return None
    result = pd.read_csv(filepath, parse_dates=[0, 1, 2],
                         infer_datetime_format=True)
    result = result[['HEADER_TIME_STAMP',
                     'START_TIME', 'STOP_TIME', 'LABEL_NAME']]
    return result


def load_offset_mapping(filepath):
    if filepath is None:
        return None
    result = pd.read_csv(filepath)
    return result


def load_orientation_corrections(filepath):
    if filepath is None:
        return None
    result = pd.read_csv(filepath)
    return result
