"""Provides base class for SubjectMap implementations"""
from abc import ABCMeta, abstractmethod

SUBJECT_CODE_KEY = 'SubjectCode'


class SubjectMapConfig:
    """Configuration for subject mapping"""
    def __init__(self, fields, format_str):
        """Create the subject map config

        Arguments:
            fields (list): The ordered list of fields to use as a key
            format_str (str): The format string (e.g. 'ex{SubjectCode:02}')
        """
        self._fields = fields
        self._format_str = format_str

    @property
    def fields(self):
        """Return the list of fields used when mapping subjects"""
        return self._fields

    @property
    def format_str(self):
        """Return the format string used when mapping subjects"""
        return self._format_str

    def format_code(self, code):
        """Format numeric subject code using format_str"""
        format_args = {SUBJECT_CODE_KEY: code}
        return self._format_str.format(**format_args)


class SubjectMap:
    """Abstract base class for mapping subjects to codes"""
    __metaclass__ = ABCMeta

    """Provides subject mapping functionality"""
    def __init__(self):
        self.config = None

    def get_config(self):
        """Return the configuration for this SubjectMap"""
        return self.config

    def get_code(self, record):
        """Given a record, get the subject code

        Args:
            record: A dictionary-like object containing fields to be mapped

        Returns:
            str: The formatted subject code
        """
        code = self.lookup_code(record)
        return self.config.format_code(code)

    @abstractmethod
    def lookup_code(self, record):
        """Lookup subject code for the given record

        Args:
            record: A dictionary-like object containing fields to be mapped

        Returns:
            int: The numeric subject code
        """

    @abstractmethod
    def load(self):
        """Load the subject map from disk"""

    @abstractmethod
    def save(self):
        """Save the subject map to disk"""

    @abstractmethod
    def rows(self):
        """Generator that returns all of the rows in the subject map, as dictionaries"""

    @staticmethod
    def extract_field(record, fieldname):
        """Extract field from record, and normalize it (by converting to lowercase and stripping whitespace)

        Args:
            record: A dictionary-like object
            fieldname (str): The field to extract

        Returns:
            str: The normalized value
        """
        value = record.get(fieldname, '')
        return str(value).strip().lower()
