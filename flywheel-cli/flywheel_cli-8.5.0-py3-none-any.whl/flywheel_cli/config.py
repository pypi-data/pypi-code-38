import argparse
import logging
import logging.handlers
import math
import multiprocessing
import os
import re
import time
import zlib
import zipfile

from flywheel_migration import deidentify, dcm

from . import walker
from .sdk_impl import create_flywheel_client, SdkUploadWrapper
from .folder_impl import FSWrapper
from .private_tags import add_private_tags

DEFAULT_CONFIG_PATH = '~/.config/flywheel/cli.cfg'
CLI_LOG_PATH = '~/.cache/flywheel/logs/cli.log'

RE_CONFIG_LINE = re.compile(r'^\s*([-_a-zA-Z0-9]+)\s*([:=]\s*(.+?))?\s*$')


class Config(object):
    def __init__(self, args=None):
        self._resolver = None

        # Configure logging
        self.configure_logging(args)

        # Set the default compression (used by zipfile/ZipFS)
        self.compression_level = getattr(args, 'compression_level', 1)
        if self.compression_level > 0:
            zlib.Z_DEFAULT_COMPRESSION = self.compression_level

        self.cpu_count = getattr(args, 'jobs', 1)
        if self.cpu_count == -1:
            self.cpu_count = max(1, math.floor(multiprocessing.cpu_count() / 2))

        self.concurrent_uploads = getattr(args, 'concurrent_uploads', 4)

        self.follow_symlinks = getattr(args, 'symlinks', False)

        self.buffer_size = 65536
        self.max_spool = getattr(args, 'max_tempfile', 50) * (1024 * 1024)  # Max tempfile size before rolling over to disk

        # Assume yes option
        self.assume_yes = getattr(args, 'yes', False)
        self.max_retries = getattr(args, 'max_retries', 3)
        self.retry_wait = 5 # Wait 5 seconds between retries

        # Certificates
        ca_certs = getattr(args, 'ca_certs', None)
        if ca_certs is not None:
            # Monkey patch certifi.where()
            import certifi
            certifi.where = lambda: ca_certs
            logging.info('Using certificates override: %s', certifi.where())

        # Set output folder
        self.output_folder = getattr(args, 'output_folder', None)

        # Skip existing files
        self.skip_existing_files = getattr(args, 'skip_existing', False)

        # Set use_uids property (default is use uids)
        self.use_uids = not getattr(args, 'no_uids', False)

        # Set check_unique_uids property (default is False)
        self.check_unique_uids = getattr(args, 'unique_uids', False)

        # Get de-identification profile
        if getattr(args, 'de_identify', False):
            profile_name = 'minimal'
        else:
            profile_name = getattr(args, 'profile', None)

        if not profile_name:
            profile_name = 'none'

        self.deid_profile = self.load_deid_profile(profile_name, args=args)

        # Add private dicom tags
        dicom_tags_file = getattr(args, 'private_dicom_tags', None)
        if dicom_tags_file is not None:
            add_private_tags(dicom_tags_file)

        # Handle unknown dicom tags
        if getattr(args, 'ignore_unknown_tags', False):
            dcm.global_ignore_unknown_tags()

        # Register encoding aliases
        encoding_aliases = getattr(args, 'encodings', None)
        if encoding_aliases is not None:
            Config.register_encoding_aliases(encoding_aliases)

        # An audit file to track which files are being uploaded to where
        self.audit_log = not getattr(args, 'no_audit_log', False)
        if self.audit_log:
            self.audit_log = getattr(args, 'audit_log_path', None) or True

        self.related_acquisitions = getattr(args, 'related_acquisitions', False)

        self.walk_filters = {
            'filter': getattr(args, 'filter', []),
            'exclude': getattr(args, 'exclude', []),
            'filter_dirs': getattr(args, 'include_dirs', []),
            'exclude_dirs': getattr(args, 'exclude_dirs', []),
        }

    def get_compression_type(self):
        if self.compression_level == 0:
            return zipfile.ZIP_STORED
        return zipfile.ZIP_DEFLATED

    def load_deid_profile(self, name, args=None):
        if os.path.isfile(name):
            return deidentify.load_profile(name)

        # Load default profiles
        profiles = deidentify.load_default_profiles()
        for profile in profiles:
            if profile.name == name:
                return profile

        msg = 'Unknown de-identification profile: {}'.format(name)
        if args:
            args.parser.error(msg)
        else:
            raise ValueError(msg)

    def get_resolver(self):
        if not self._resolver:
            if self.output_folder:
                self._resolver = FSWrapper(self.output_folder)
            else:
                fw = create_flywheel_client()
                self._resolver = SdkUploadWrapper(fw)

        return self._resolver

    def get_uploader(self):
        # Currently all resolvers are uploaders
        return self.get_resolver()

    def create_walker(self, fs_url, **kwargs):
        # Merge include/exclusion lists
        for key in ('filter', 'exclude', 'filter_dirs', 'exclude_dirs'):
            kwargs[key] = merge_lists(kwargs.get(key, []), self.walk_filters[key])
        kwargs.setdefault('follow_symlinks', self.follow_symlinks)

        return walker.create_walker(fs_url, **kwargs)

    def configure_logging(self, args):
        root = logging.getLogger()

        # Propagate all debug logging
        root.setLevel(logging.DEBUG)

        # Always log to cli log file
        log_path = os.path.expanduser(os.environ.get('FW_LOG_FILE_PATH', CLI_LOG_PATH))
        log_dir = os.path.dirname(log_path)
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)

        # Use GMT ISO date for logfile
        file_formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
        file_formatter.converter = time.gmtime

        # Allow environment overrides for log size and backup count
        log_file_size = int(os.environ.get('FW_LOG_FILE_SIZE', '5242880')) # Default is 5 MB
        log_file_backup_count = int(os.environ.get('FW_LOG_FILE_COUNT', '2')) # Default is 2

        file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=log_file_size, backupCount=log_file_backup_count)
        file_handler.setFormatter(file_formatter)
        root.addHandler(file_handler)

        # Control how much (if anything) goes to console
        console_log_level = logging.INFO
        if getattr(args, 'quiet', False):
            console_log_level = logging.ERROR
        elif getattr(args, 'debug', False):
            console_log_level = logging.DEBUG

        console_formatter = logging.Formatter(fmt='%(levelname)s: %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(console_log_level)
        root.addHandler(console_handler)

        # Finally, capture all warnings to the logging framework
        logging.captureWarnings(True)

    @staticmethod
    def get_global_parser():
        parser = argparse.ArgumentParser(add_help=False)
        config_group = parser.add_mutually_exclusive_group()
        config_group.add_argument('--config-file', '-C', help='Specify configuration options via config file')
        config_group.add_argument('--no-config', action='store_true', help='Do NOT load the default configuration file')

        parser.add_argument('-y', '--yes', action='store_true', help='Assume the answer is yes to all prompts')
        parser.add_argument('--ca-certs', help='The file to use for SSL Certificate Validation')

        log_group = parser.add_mutually_exclusive_group()
        log_group.add_argument('--debug', action='store_true', help='Turn on debug logging')
        log_group.add_argument('--quiet', action='store_true', help='Squelch log messages to the console')
        return parser

    @staticmethod
    def get_import_parser():
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--max-retries', default=3, help='Maximum number of retry attempts, if assume yes')
        parser.add_argument('--jobs', '-j', default=-1, type=int, help='The number of concurrent jobs to run (e.g. compression jobs)')
        parser.add_argument('--concurrent-uploads', default=4, type=int, help='The maximum number of concurrent uploads')
        parser.add_argument('--compression-level', default=1, type=int, choices=range(-1, 9),
                help='The compression level to use for packfiles. -1 for default, 0 for store')
        parser.add_argument('--symlinks', action='store_true', help='follow symbolic links that resolve to directories')
        parser.add_argument('--include-dirs', action='append', dest='include_dirs', help='Patterns of directories to include')
        parser.add_argument('--exclude-dirs', action='append', dest='exclude_dirs', help='Patterns of directories to exclude')
        parser.add_argument('--include', action='append', dest='filter', help='Patterns of filenames to include')
        parser.add_argument('--exclude', action='append', dest='exclude', help='Patterns of filenames to exclude')
        parser.add_argument('--output-folder', help='Output to the given folder instead of uploading to flywheel')
        parser.add_argument('--no-uids', action='store_true', help='Ignore UIDs when grouping sessions and acquisitions')
        parser.add_argument('--unique-uids', action='store_true', help='Warn before creating any containers with duplicate UIDs')
        parser.add_argument('--max-tempfile', default=50, type=int, help='The max in-memory tempfile size, in MB, or 0 to always use disk')
        parser.add_argument('--skip-existing', action='store_true', help='Skip import of existing files')
        parser.add_argument('--no-audit-log', action='store_true', help='Don\'t generate an audit log.')
        parser.add_argument('--audit-log-path', help='Location to save audit log')
        parser.add_argument('--private-dicom-tags', help='Path to a private dicoms csv file')
        parser.add_argument('--ignore-unknown-tags', action='store_true', help='Ignore unknown dicom tags')
        parser.add_argument('--encodings', help='Set character encoding aliases. E.g. win_1251=cp1251')
        parser.add_argument('--related-acquisitions', action='store_true', help='Store related dicoms in the same acquisition')
        return parser

    @staticmethod
    def get_deid_parser():
        parser = argparse.ArgumentParser(add_help=False)
        deid_group = parser.add_mutually_exclusive_group()
        deid_group.add_argument('--de-identify', action='store_true', help='De-identify DICOM files, e-files and p-files prior to upload')
        deid_group.add_argument('--profile', help='Use the De-identify profile by name or file')
        return parser

    @staticmethod
    def set_defaults(parsers):
        # Read defaults from:
        # ~/.config/flywheel/cli.cfg
        # --config-file, -C
        defaults = Config.read_config_defaults()

        # Then set defaults for each subparser
        for key, parser in parsers.items():
            parser.set_defaults(**defaults)

    @staticmethod
    def read_config_defaults():
        """Read config defaults from the default file, and an optional arg file"""

        # Parse config_file argument from command line
        config_parser = Config.get_global_parser()
        args, _ = config_parser.parse_known_args()

        defaults = {}

        if not args.no_config:
            for path in [DEFAULT_CONFIG_PATH, args.config_file]:
                if not path:
                    continue

                path = os.path.expanduser(path)
                if os.path.isfile(path):
                    if not args.quiet:
                        print('Reading config options from: {}'.format(path))
                    Config.read_config_file(path, defaults)

        return defaults

    @staticmethod
    def read_config_file(path, dest):
        """Read configuration values from path, into dest"""
        with open(path) as f:
            for line in f.readlines():
                m = RE_CONFIG_LINE.match(line)
                if m is not None:
                    key = m.group(1).lower().replace('-', '_')
                    value = m.group(3)
                    if value is None:
                        value = 'true'
                    dest[key] = value

    @staticmethod
    def register_encoding_aliases(encoding_aliases):
        """Register common encoding aliases"""
        import encodings
        for encoding_spec in re.split(r'[,\s]+', encoding_aliases):
            if not encoding_spec:
                continue
            key, _, value = encoding_spec.partition('=')
            encodings.aliases.aliases[key.strip().lower()] = value.strip().lower()


def merge_lists(a, b):
    """Merge lists a and b, returning the result or None if the result is empty"""
    result = (a or []) + (b or [])
    if result:
        return result
    return None
