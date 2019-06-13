"""Individual file/packfile profile for de-identification"""

import fnmatch
from abc import ABCMeta, abstractmethod

from .deid_field import DeIdField


class FileProfile:
    """Abstract class that represents a single file/packfile profile"""
    __metaclass__ = ABCMeta

    # NOTE: If you derive from this class, set a unique name for the factory method to use
    name = None
    log_fields = []

    # NOTE: Date/Time formats are from dicom standard, override as necessary
    # http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html

    uid_prefix_fields = 4  # How many prefix fields to keep
    uid_suffix_fields = 1  # How many suffix fields to keep in uid
    uid_max_suffix_digits = 6  # Maximum number of digits to keep from the suffix (trailing)
    uid_hash_fields = (6, 6, 6, 6, 6, 6)  # The number and length of parts to add to the hash

    hash_digits = 0  # How many digits are supported for 'hash' action
    hash_algorithm = 'sha256'
    date_format = '%Y%m%d'  # YYYYMMDD
    datetime_format = '%Y%m%d%H%M%S.%f'  # YYYYMMDDHHMMSS.FFFFFF&ZZXX
    datetime_has_timezone = True  # Whether or not optional timezone exists

    def __init__(self, packfile_type=None, file_filter=None):
        """Initialize the file profile"""
        self.packfile_type = packfile_type
        self.file_filter = file_filter
        self.fields = []
        self.field_map = {}
        self.log = None

        # Action configuration
        self.date_increment = None
        self.hash_salt = None

    def add_field(self, field):
        """Add a field to de-identify"""
        self.fields.append(field)
        self.field_map[field.fieldname] = field

    def set_log(self, log):
        """Set the log instance"""
        self.log = log

    def get_log_fields(self):
        """Return the full set of fieldnames that should be logged"""
        result = list(self.log_fields)
        for field in self.fields:
            result.append(field.fieldname)
        return result

    @classmethod
    def factory(cls, name, config=None, log=None):
        """Create a new file profile instance for the given name.

        Arguments:
            name (str): The name of the profile type
            config (dict): The optional configuration dictionary
            log: The optional de-id log instance
        """
        result = None

        for subclass in cls.__subclasses__():
            if subclass.name == name:
                result = subclass()
                break

        if not result:
            raise ValueError('Unknown file profile: "{}"'.format(name))

        if config is not None:
            result.load_config(config)

        if log is not None:
            result.set_log(log)

        return result

    @classmethod
    def profile_names(cls):
        """Get the list of profile names"""
        result = []
        for subclass in cls.__subclasses__():
            if subclass.name is not None:
                result.append(subclass.name)
        return result

    def to_config(self):
        """Get configuration as a dictionary"""

        result = {
            'fields': [field.to_config() for field in self.fields]
        }

        # Read action configuration
        if self.date_increment is not None:
            result['date-increment'] = self.date_increment

        if self.hash_salt is not None:
            result['salt'] = self.hash_salt

        return result

    def load_config(self, config):
        """Read configuration from a dictionary"""
        # Read fields
        for field in config.get('fields', []):
            self.add_field(DeIdField.factory(field))

        # Read action configuration
        self.date_increment = config.get('date-increment', None)
        self.hash_salt = config.get('salt', None)

    def matches_file(self, filename):
        """Check if this profile can process the given file"""
        return self.file_filter and fnmatch.fnmatch(self.file_filter, filename)

    def matches_packfile(self, packfile_type):
        """Check if this profile can process the given packfile"""
        return self.packfile_type and self.packfile_type == packfile_type

    def process_files(self, src_fs, dst_fs, files, callback=None):
        """Process all files in the file list, performing de-identification steps

        Args:
            src_fs: The source filesystem (Provides open function)
            dst_fs: The destination filesystem
            files: The set of files in src_fs to process
            callback: Function to call after writing each file
        """
        state = self.create_file_state()

        for path in files:
            # Load file
            record, modified = self.load_record(state, src_fs, path)

            # Record could be None if it should be skipped
            if not record:
                continue

            # Override destination path
            dst_path = self.get_dest_path(state, record, path)

            if modified or self.fields:
                # Create before entry, if log is provided
                if self.log:
                    self.write_log_entry(path, 'before', state, record)

                # De-identify
                for field in self.fields:
                    field.deidentify(self, state, record)

                # Create after entry, if log is provided
                if self.log:
                    self.write_log_entry(path, 'after', state, record)

                # Save to dst_fs if we modified the record
                self.save_record(state, record, dst_fs, dst_path)
            else:
                # No fields to de-identify, just copy to dst
                with src_fs.open(path, 'rb') as src_file:
                    dst_fs.upload(dst_path, src_file)

            if callable(callback):
                callback(dst_fs, dst_path)

    def get_value(self, state, record, fieldname):
        """Get the transformed value for fieldname"""
        field = self.field_map.get(fieldname)
        if field:
            return field.get_value(self, state, record)
        return self.read_field(state, record, fieldname)

    def create_file_state(self):  # pylint: disable=no-self-use
        """Create state object for processing files"""
        return None

    def get_dest_path(self, state, record, path):  # pylint: disable=no-self-use, unused-argument
        """Get optional override for the destination path for record"""
        return path

    def write_log_entry(self, path, entry_type, state, record):
        """Write a single log entry of type for path"""
        log_entry = {'path': path, 'type': entry_type}
        for fieldname in self.get_log_fields():
            log_entry[fieldname] = self.read_field(state, record, fieldname)
        self.log.write_entry(log_entry)

    @abstractmethod
    def load_record(self, state, src_fs, path):
        """Load the record(file) at path, return None to ignore this file"""

    @abstractmethod
    def save_record(self, state, record, dst_fs, path):
        """Save the record to the destination path"""

    @abstractmethod
    def read_field(self, state, record, fieldname):
        """Read the named field as a string"""

    @abstractmethod
    def remove_field(self, state, record, fieldname):
        """Remove the named field from the record"""

    @abstractmethod
    def replace_field(self, state, record, fieldname, value):
        """Replace the named field with value in the record"""
