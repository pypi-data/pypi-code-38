"""Provides logging of de-identification actions"""
import csv
import os

from abc import ABCMeta, abstractmethod


class DeIdLog:
    """Abstract class that logs original values of de-identified fields"""
    __metaclass__ = ABCMeta

    @staticmethod
    def factory(path):
        """Create a new deid_log instance for the path string"""
        # Currently only support csv, so that's what you get
        return CsvDeIdLog(path)

    @abstractmethod
    def to_config_str(self):
        """Convert the log configuration to a string"""

    @abstractmethod
    def initialize(self, profile):
        """Initialize the log instance for the given profile."""

    @abstractmethod
    def write_entry(self, entry):
        """Write the log entry (which is a dict)"""

    @abstractmethod
    def close(self):
        """Close the logfile"""


class CsvDeIdLog(DeIdLog):
    """Logs de-identified fields in CSV format"""
    def __init__(self, path):
        """Create a csv log-file at path"""
        self.path = path
        self.fileobj = None
        self.writer = None

    def to_config_str(self):
        return self.path

    def initialize(self, profile):
        fields = ['path', 'type']
        for file_profile in profile.file_profiles:
            for fieldname in file_profile.get_log_fields():
                fields.append(fieldname)

        # Create output directory, if it doesn't exist
        log_dir = os.path.dirname(self.path)
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)

        # Open the file and write header
        # Assume, but don't check, that headers didn't change...
        exists = os.path.exists(self.path)
        if exists:
            self.fileobj = open(self.path, 'a')
        else:
            self.fileobj = open(self.path, 'w')

        self.writer = csv.DictWriter(self.fileobj, fields)
        if not exists:
            self.writer.writeheader()

    def write_entry(self, entry):
        self.writer.writerow(entry)
        self.fileobj.flush()

    def close(self):
        if self.fileobj:
            self.fileobj.close()
            self.fileobj = None
            self.writer = None
