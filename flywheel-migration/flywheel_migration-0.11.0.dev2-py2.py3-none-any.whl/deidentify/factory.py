"""Provides factory methods for de-identification classes"""
from copy import copy

from .subject_map import SubjectMapConfig
from .csv_subject_map import CSVSubjectMap

DEFAULT_SUBJECT_MAP_FIELDS = ['PatientName', 'PatientBirthDate']
DEFAULT_SUBJECT_MAP_FORMAT = '{SubjectCode}'


def load_subject_map(url):
    """Load subject map from url (currently only CSV is supported)"""
    subject_map = CSVSubjectMap(url)
    subject_map.load()
    return subject_map


def create_subject_map(url, fieldnames=None, format_str=None):
    """Create a subject mapping. (Currently only CSV is supported)

    Arguments:
        fields (list): The ordered list of fields to use as a key
        format_str (str): The format string (e.g. 'ex{SubjectCode:02}')
    """
    if fieldnames is None:
        fieldnames = copy(DEFAULT_SUBJECT_MAP_FIELDS)
    if format_str is None:
        format_str = DEFAULT_SUBJECT_MAP_FORMAT
    config = SubjectMapConfig(fieldnames, format_str)
    return CSVSubjectMap.create(url, config)
