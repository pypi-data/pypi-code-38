import re
import os
import datetime
import numpy as np
import pandas as pd
from glob import glob
from . import fileio

CAMELCASE_PATTERN = r'(?:[A-Z][A-Za-z0-9]+)+'
VERSIONCODE_PATTERN = r'(?:NA|[0-9x]+)'
SID_PATTERN = r'[A-Z0-9]+'
ANNOTATOR_PATTERN = r'[A-Za-z0-9]+'
FILE_TIMESTAMP_PATTERN = r'[0-9]{4}(?:\-[0-9]{2}){5}-[0-9]{3}-(?:P|M)[0-9]{4}'
FILE_EXTENSION_PATTERN = r'''
(?:sensor|event|log|annotation|feature|class|prediction|model|classmap)\.csv
'''
MHEALTH_FLAT_FILEPATH_PATTERN = r'(\w+)[\/\\]{1}(?:(?:MasterSynced[\/\\]{1})|(?:Derived[\/\\]{1}(?:\w+[\/\\]{1})*))[0-9A-Za-z\-\.]+\.csv(\.gz)*'
MHEALTH_FILEPATH_PATTERN = r'(\w+)[\/\\]{1}(?:(?:MasterSynced[\/\\]{1})|(?:Derived[\/\\]{1}(?:\w+[\/\\]{1})*))\d{4}[\/\\]{1}\d{2}[\/\\]{1}\d{2}[\/\\]{1}\d{2}'


def is_mhealth_filepath(filepath):
    filepath = os.path.abspath(filepath)
    matched = re.search(
        MHEALTH_FILEPATH_PATTERN,
        filepath)
    return matched is not None


def is_mhealth_flat_filepath(filepath):
    matched = re.search(
        MHEALTH_FLAT_FILEPATH_PATTERN,
        os.path.abspath(filepath)
    )
    return matched is not None


def get_mhealth_root(filepath):
    assert is_mhealth_filepath(filepath) or is_mhealth_flat_filepath(filepath)
    pid = get_pid(filepath)
    return filepath.split(pid)[0]


def get_pid_root(filepath):
    assert is_mhealth_filepath(filepath) or is_mhealth_flat_filepath(filepath)
    pid = get_pid(filepath)
    return os.path.join(filepath.split(pid)[0], pid)


def find_location_mapping(filepath):
    mhealth_root = get_mhealth_root(filepath)
    result = os.path.join(
        mhealth_root, 'MetaCrossParticipants', 'location_mapping.csv')
    if os.path.exists(result):
        return result
    else:
        pid_root = get_pid_root(filepath)
        candicates = glob(os.path.join(
            pid_root, '**', 'location_mapping.csv'), recursive=True)
        if len(candicates) == 1:
            return candicates[0]
        else:
            return False


def find_offset_mapping(filepath):
    pid_root = get_pid_root(filepath)
    candicates = glob(os.path.join(
        pid_root, '**', 'offset_mapping.csv'), recursive=True)
    if len(candicates) == 1:
        return candicates[0]
    else:
        mhealth_root = get_mhealth_root(filepath)
        result = os.path.join(
            mhealth_root, 'MetaCrossParticipants', 'offset_mapping.csv')
        if os.path.exists(result):
            return result
        else:
            return False


def get_offset(filepath, offset_column):
    offset_mapping_file = find_offset_mapping(filepath)
    pid = get_pid(filepath)
    if bool(offset_mapping_file):
        offset_mapping = fileio.load_offset_mapping(offset_mapping_file)
        offset_in_secs = float(
            offset_mapping.loc[offset_mapping.iloc[:, 0] == pid,
                               offset_mapping.columns[offset_column]].values[0]
        )
    else:
        offset_in_secs = 0
    return offset_in_secs


def find_pid_exceptions(filepath):
    mhealth_root = get_mhealth_root(filepath)
    result = os.path.join(
        mhealth_root, 'MetaCrossParticipants', 'pid_exceptions.csv')
    if os.path.exists(result):
        return result
    else:
        return False


def is_pid_included(filepath):
    exceptions = pd.read_csv(find_pid_exceptions(filepath))
    pid = get_pid(filepath)
    if np.any(pid == exceptions['PID'].values):
        return False
    else:
        return True


def find_orientation_corrections(filepath):
    pid_root = get_pid_root(filepath)
    candicates = glob(os.path.join(
        pid_root, '**', 'orientation_corrections.csv'), recursive=True)
    if len(candicates) == 1:
        return candicates[0]
    else:
        mhealth_root = get_mhealth_root(filepath)
        result = os.path.join(
            mhealth_root, 'MetaCrossParticipants',
            'orientation_corrections.csv')
        if os.path.exists(result):
            return result
        else:
            return False


def get_orientation_correction(filepath):
    orientation_corrections_file = find_orientation_corrections(
        filepath)
    pid = get_pid(filepath)
    sid = get_sid(filepath)
    if bool(orientation_corrections_file):
        orientation_corrections = fileio.load_orientation_corrections(
            orientation_corrections_file)
        orientation_correction = orientation_corrections.loc[
            (orientation_corrections.iloc[:, 0] == pid) & (
                orientation_corrections.iloc[:, 1] == sid),
            orientation_corrections.columns[3:6]
        ]
        if orientation_correction.empty:
            orientation_correction = np.array(['x', 'y', 'z'])
        else:
            orientation_correction = orientation_correction.values[0]
    else:
        orientation_correction = np.array(['x', 'y', 'z'])
    return orientation_correction


def is_mhealth_filename(filepath):
    filename = os.path.basename(filepath)

    sensor_filename_pattern = '^' + CAMELCASE_PATTERN + '\-' + \
        CAMELCASE_PATTERN + \
        '\-' + VERSIONCODE_PATTERN + '\.' + \
        SID_PATTERN + '\-' + CAMELCASE_PATTERN + '\.' + \
        FILE_TIMESTAMP_PATTERN + '\.sensor\.csv(\.gz)*$'

    annotation_filename_pattern = '^' + CAMELCASE_PATTERN + '\.' + \
        ANNOTATOR_PATTERN + '\-' + CAMELCASE_PATTERN + '\.' + \
        FILE_TIMESTAMP_PATTERN + '\.annotation\.csv(\.gz)*$'

    sensor_matched = re.search(
        sensor_filename_pattern,
        filename
    )
    annotation_matched = re.search(
        annotation_filename_pattern,
        filename
    )
    return sensor_matched is not None or annotation_matched is not None


def get_pid(filepath):
    if is_mhealth_filepath(filepath):
        matched = re.search(MHEALTH_FILEPATH_PATTERN, filepath)
    elif is_mhealth_flat_filepath(filepath):
        matched = re.search(MHEALTH_FLAT_FILEPATH_PATTERN, filepath)
    else:
        return None
    return matched.group(1) if matched is not None else None


def get_pids(root):
    return list(filter(lambda name: 'SPADES' in name, os.listdir(root)))


def get_sensor_type(filepath):
    assert is_mhealth_filename(filepath)
    filename = os.path.basename(filepath)
    result = filename.split('.')[0].split('-')[0]
    return result


def get_data_type(filepath):
    assert is_mhealth_filename(filepath)
    filename = os.path.basename(filepath)
    tokens = filename.split('.')[0]
    tokens = tokens.split('-')
    if len(tokens) >= 2:
        return tokens[1]
    else:
        return None


def get_version_code(filepath):
    assert is_mhealth_filename(filepath)
    filename = os.path.basename(filepath)
    tokens = filename.split('.')[0]
    tokens = tokens.split('-')
    if len(tokens) >= 3:
        return tokens[2]
    else:
        return None


def get_sid(filepath):
    assert is_mhealth_filename(filepath)
    filename = os.path.basename(filepath)
    return filename.split('.')[1].split('-')[0]


def get_file_type(filepath):
    assert is_mhealth_filename(filepath)
    filename = os.path.basename(filepath)
    if filename.endswith('gz'):
        return filename.split('.')[-3]
    else:
        return filename.split('.')[-2]


def get_file_timestamp(filepath, ignore_tz=True):
    assert is_mhealth_filename(filepath)
    filename = os.path.basename(filepath)
    if filename.endswith('gz'):
        timestamp_index = -4
    else:
        timestamp_index = -3
    timestamp_str = filename.split('.')[timestamp_index]
    if ignore_tz:
        timestamp_str = timestamp_str[:-6]
        result = datetime.datetime.strptime(
            timestamp_str, '%Y-%m-%d-%H-%M-%S-%f')
    else:
        timestamp_str = timestamp_str.replace('P', '+').replace('M', '-')
        result = datetime.datetime.strptime(
            timestamp_str, '%Y-%m-%d-%H-%M-%S-%f-%z')
    return result


def get_session_start_time(filepath, filepaths):
    pid = get_pid(filepath)
    smallest = datetime.datetime.now()
    for path in filepaths:
        if get_pid(path) == pid:
            timestamp = get_file_timestamp(path, ignore_tz=True)
            if timestamp < smallest:
                smallest = timestamp
    smallest = smallest.replace(microsecond=0, second=0, minute=0)
    return smallest


def get_session_end_time(filepath, filepaths):
    pid = get_pid(filepath)
    largest = datetime.datetime.fromtimestamp(100000)
    for path in filepaths:
        if get_pid(path) == pid:
            timestamp = get_file_timestamp(path, ignore_tz=True)
            if timestamp > largest:
                largest = timestamp
    largest = largest.replace(microsecond=0, second=0,
                              minute=0) + datetime.timedelta(hours=1)
    return largest


def get_timezone(filepath):
    dt = get_file_timestamp(filepath, ignore_tz=False)
    return dt.tzinfo


def get_timezone_name(filepath):
    dt = get_file_timestamp(filepath, ignore_tz=False)
    tz_name = dt.strftime('%Z')
    return tz_name


def get_init_placement(filepath, mapping_file):
    assert is_mhealth_filename(filepath)
    mapping = pd.read_csv(mapping_file)
    sid = get_sid(filepath)
    pid = get_pid(filepath)
    pid_col = mapping.columns[0]
    sid_col = mapping.columns[1]
    placement_col = mapping.columns[2]
    loc = mapping.loc[(mapping[pid_col] == pid) & (
        mapping[sid_col] == sid), placement_col].values[0]
    return loc


def get_placement_abbr(placement):
    tokens = placement.split(' ')
    tokens = list(map(lambda token: token[0].upper(), tokens))
    return ''.join(tokens)


def auto_init_placement(filepath):
    assert is_mhealth_filename(filepath)
    mapping_file = find_location_mapping(filepath)
    if mapping_file:
        mapping = pd.read_csv(mapping_file)
    else:
        return None
    sid = get_sid(filepath)
    pid = get_pid(filepath)

    if len(mapping.columns) == 3:
        pid_col = mapping.columns[0]
        sid_col = mapping.columns[1]
        placement_col = mapping.columns[2]
        mask = (mapping[pid_col] == pid) & (mapping[sid_col] == sid)
    else:
        sid_col = mapping.columns[0]
        placement_col = mapping.columns[1]
        mask = mapping[sid_col] == sid
    loc = mapping.loc[mask, placement_col]
    if loc.empty:
        return None
    else:
        return loc.values[0]
    return loc
