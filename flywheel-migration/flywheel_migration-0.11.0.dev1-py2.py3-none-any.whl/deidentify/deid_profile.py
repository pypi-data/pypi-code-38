"""Provides profile loading/saving for file de-identification"""
from . import factory
from .file_profile import FileProfile
from .deid_log import DeIdLog


class DeIdProfile:
    """Represents steps to take to de-identify a file or set of files."""
    def __init__(self):
        # Multiple file profiles
        # Optional name / description
        self.name = None
        self.description = None

        self.map_subjects_url = None
        self.map_subjects = None

        self.log = None

        self.file_profiles = []

    def to_config(self):
        """Create configuration dictionary from this profile"""
        result = {}

        if self.name is not None:
            result['name'] = self.name

        if self.description is not None:
            result['description'] = self.description

        if self.map_subjects_url is not None:
            result['map-subjects'] = self.map_subjects_url

        if self.log is not None:
            result['deid-log'] = self.log.to_config_str()

        for profile in self.file_profiles:
            result[profile.name] = profile.to_config()

        return result

    def initialize(self):
        """Initialize the profile, prior to importing"""
        if self.log:
            self.log.initialize(self)

    def finalize(self):
        """Perform any necessary cleanup with profile"""
        if self.log:
            self.log.close()

    def load_config(self, config):
        """Initialize this profile from a config dictionary"""
        self.name = config.get('name')
        self.description = config.get('description')

        # Load subject map
        self.map_subjects_url = config.get('map-subjects')
        if self.map_subjects_url:
            self.map_subjects = factory.load_subject_map(self.map_subjects_url)

        # De-id logfile
        log_str = config.get('deid-log')
        if log_str:
            self.log = DeIdLog.factory(log_str)

        # Load file profiles
        for name in FileProfile.profile_names():
            self.file_profiles.append(FileProfile.factory(name, config=config.get(name), log=self.log))

    def get_file_profile(self, name):
        """Get file profile for name, or None if not present"""
        for profile in self.file_profiles:
            if profile.name == name:
                return profile
        return None

    def process_file(self, src_fs, src_file, dst_fs):
        """Process the given file, if it's handled by a file profile.

        Args:
            src_fs: The source filesystem
            src_file: The source file path
            dst_fs: The destination filesystem

        Returns:
            bool: True if the file was processed, false otherwise
        """
        for profile in self.file_profiles:
            if profile.matches_file(src_file):
                profile.process_files(src_fs, dst_fs, [src_file])
                return True
        return False

    def process_packfile(self, packfile_type, src_fs, dst_fs, paths, callback=None):
        """Process the given packfile, if it's handled by a file profile.

        Args:
            packfile_type (str): The packfile type
            src_fs: The source filesystem
            dst_fs: The destination filesystem
            paths: The list of paths to process
            callback: Optional function to call after processing each file

        Returns:
            bool: True if the packfile was processed, false otherwise
        """
        for profile in self.file_profiles:
            if profile.matches_packfile(packfile_type):
                profile.process_files(src_fs, dst_fs, paths, callback=callback)
                return True
        return False
