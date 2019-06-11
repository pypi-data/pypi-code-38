"""Provides gear helper functions"""
import copy
import json
import logging
import os

from .client import Client


DEFAULT_GEAR_PATH = '/flywheel/v0'


class GearContext(object):
    """Provides helper functions for gear development"""

    def __init__(self, gear_path=None):
        self._path = os.path.abspath(gear_path or DEFAULT_GEAR_PATH)
        self._client = None
        self._invocation = None
        self._out_dir = None
        self._work_dir = None
        self._metadata = {}
        self.log = logging.getLogger(__name__)

    def init_logging(self, level='INFO'):
        """Initializes logging to the given level"""
        logging.basicConfig(level=getattr(logging, level.upper(), None) or logging.INFO)

    @property
    def config(self):
        """Get the config dictionary.

        :return: The configuration dictionary.
        :rtype: dict
        """
        return self._get_invocation()['config']

    @property
    def destination(self):
        """Get the destination reference.

        :return: The destination dictionary.
        :rtype: dict
        """
        return self._get_invocation()['destination']

    @property
    def work_dir(self):
        """Get the absolute path to a work directory

        :return: The absolute path to work.
        :rtype: str
        """
        if self._work_dir is None:
            self._work_dir = os.path.join(self._path, 'work')
            if not os.path.exists(self._work_dir):
                os.makedirs(self._work_dir)
        return self._work_dir

    @property
    def output_dir(self):
        """Get the absolute path to the output directory.

        :return: The absolute path to outputs.
        :rtype: str
        """
        if self._out_dir is None:
            self._out_dir = os.path.join(self._path, 'output')
            if not os.path.exists(self._out_dir):
                os.makedirs(self._out_dir)
        return self._out_dir

    @property
    def client(self):
        """Get the SDK client, if an api key input exists.

        Raises a ValueError if there is no api-key input.

        :return: The SDK client
        :rtype: Client
        """
        if self._client is None:
            api_key = None
            for inp in self._get_invocation()['inputs'].values():
                if inp['base'] == 'api-key' and inp['key']:
                    api_key = inp['key']
                    break

            if api_key is None:
                raise RuntimeError('Could not find an api-key in config')

            self._client = Client(api_key)
        return self._client

    def log_config(self):
        """Print the configuration and input files to the logger"""
        # Log destination
        self.log.info('Destination is %s=%s', self.destination.get('type'), self.destination.get('id'))

        # Log file inputs
        for inp_name, inp in self._get_invocation()['inputs'].items():
            if inp['base'] != 'file':
                continue

            container_type = inp.get('hierarchy', {}).get('type')
            container_id = inp.get('hierarchy', {}).get('id')
            file_name = inp.get('location', {}).get('name')

            self.log.info('Input file "%s" is %s from %s=%s', inp_name, file_name,
                container_type, container_id)

        # Log configuration values
        for key, value in self.config.items():
            self.log.info('Config "%s=%s"', key, value)

    def get_input(self, name):
        """Get the input for name.

        :param str name: The name of the input
        :return: The input dictionary, or None if not found.
        :rtype: dict
        """
        return self._get_invocation()['inputs'].get(name)

    def get_input_path(self, name):
        """Get the full path to the given input file.

        Raises an exception if the input exists, but is not a file.

        :param str name: The name of the input
        :return: The path to the input file if it exists, otherwise None
        :rtype: str
        """
        inp = self.get_input(name)
        if inp is None:
            return None
        if inp['base'] != 'file':
            raise ValueError('The specified input {} is not a file'.format(name))
        return inp['location']['path']

    def open_input(self, name, mode='r', **kwargs):
        """Open the named input file.

        Raises an exception if the input does not exist or is not a file.

        :param str name: The name of the input
        :param str mode: The open mode (default is 'r')
        :param **kwargs: Additional args to pass to ``open``
        :return: The file object
        :rtype: file
        """
        path = self.get_input_path(name)
        if path is None:
            raise OSError('An input named {} does not exist!'.format(name))

        return open(path, mode, **kwargs)

    def open_output(self, name, mode='w', **kwargs):
        """Open the named output file.

        :param str name: The name of the output
        :param str mode: The open mode (default is 'w')
        :param **kwargs: Additional args to pass to ``open``
        :return: The file object
        :rtype: file
        """
        path = os.path.join(self.output_dir, name)
        return open(path, mode, **kwargs)

    def get_context_value(self, name):
        """Get the context input for name.

        :param str name: The name of the input
        :return: The input context value, or None if not found.
        :rtype: dict
        """
        inp = self.get_input(name)
        if not inp:
            return None
        if inp['base'] != 'context':
            raise ValueError('The specified input {} is not a context input'.format(name))
        return inp.get('value')

    def update_container_metadata(self, container_type, *args, **kwargs):
        """Update metadata for the given container name in the hierarchy.

        A dictionary and/or a set of key=value args can be passed to this function.

        The metadata will be written when write_metadata() is called, or
        if using this as a context manager, when the context is exited.

        :param str container_type: The container type (e.g. session or acquisition)
        :param *args: The optional update dictionary
        :param **kwargs: The optional update key-value pairs
        """
        update = self._create_update_dict(args, kwargs)
        self._update_metadata(container_type, update)

    def update_file_metadata(self, file_name, *args, **kwargs):
        """Update metadata for the given file on the destination.

        A dictionary and/or a set of key=value args can be passed to this function.

        The metadata will be written when write_metadata() is called, or
        if using this as a context manager, when the context is exited.

        :param str file_name: The name of the file
        :param *args: The optional update dictionary
        :param **kwargs: The optional update key-value pairs
        """
        container_type = self.destination['type']
        update = self._create_update_dict(args, kwargs)
        self._update_metadata(container_type, update, file_name=file_name)

    def update_destination_metadata(self, *args, **kwargs):
        """Update metadata for the destination container.

        A dictionary and/or a set of key=value args can be passed to this function.

        The metadata will be written when write_metadata() is called, or
        if using this as a context manager, when the context is exited.

        :param *args: The optional update dictionary
        :param **kwargs: The optional update key-value pairs
        """
        container_type = self.destination['type']
        update = self._create_update_dict(args, kwargs)
        self._update_metadata(container_type, update)

    def write_metadata(self):
        """Write the metadata json file to the output folder"""
        if not self._metadata:
            return

        with self.open_output('.metadata.json') as f:
            json.dump(self._metadata, f, indent=2)

    def download_session_bids(self, target_dir='work/bids', src_data=False, folders=None, **kwargs):
        """Download the session in bids format to target_dir.

        :param str target_dir: The destination directory (otherwise work/bids will be used)
        :param bool src_data: Whether or not to include src data (e.g. dicoms)
        :param list folders: The list of folders to include (otherwise all folders) e.g. ['anat', 'func']
        :param **kwargs: Additional arguments to pass to download_bids_dir
        :return: The absolute path to the downloaded bids directory
        :rtype: str
        """
        kwargs['src_data'] = src_data
        kwargs['folders'] = folders
        return self._download_bids('session', target_dir, kwargs)

    def download_project_bids(self, target_dir='work/bids', src_data=False, subjects=None, sessions=None, folders=None):
        """Download the project in bids format to target_dir.

        :param str target_dir: The destination directory (otherwise work/bids will be used)
        :param bool src_data: Whether or not to include src data (e.g. dicoms)
        :param list subjects: The list of subjects to include (via subject code) otherwise all subjects
        :param list sessions: The list of sessions to include (via session label) otherwise all sessions
        :param list folders: The list of folders to include (otherwise all folders) e.g. ['anat', 'func']
        :param **kwargs: Additional arguments to pass to download_bids_dir
        :return: The absolute path to the downloaded bids directory
        :rtype: str
        """
        kwargs['src_data'] = src_data
        kwargs['subjects'] = subjects
        kwargs['sessions'] = sessions
        kwargs['folders'] = folders
        return self._download_bids('project', target_dir, kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.write_metadata()

    def _download_bids(self, container_type, target_dir, kwargs):
        """Download bids to the given target directory"""
        # Raise a specific error if BIDS not installed
        download_bids_dir = self._load_download_bids()

        # Cleanup kwargs
        for key in ('subjects', 'sessions', 'folders'):
            if key in kwargs and kwargs[key] is None:
                kwargs.pop(key)

        # Resolve container type from parents
        dest_container = self.client.get(self.destination['id'])

        parent_id = dest_container.get(container_type)
        if parent_id is None:
            parent_id = dest_container.get('parents', {}).get(container_type)

        if parent_id is None:
            raise RuntimeError('Cannot find {} from destination'.format(container_type))

        self.log.info('Using source container: %s=%s', container_type, parent_id)

        # Download bids to the target directory
        # download_bids_dir will create the target path
        target_path = os.path.join(self._path, target_dir)
        download_bids_dir(self.client, parent_id, container_type, target_path, **kwargs)
        return target_path

    def _load_download_bids(self):
        """Load the download_bids_dir function from flywheel_bids"""
        try:
            from flywheel_bids.export_bids import download_bids_dir
            return download_bids_dir
        except ImportError:
            self.log.error('Cannot load flywheel-bids package.')
            self.log.error('Make sure it is installed with "pip install flywheel-bids"')
            raise RuntimeError('Unable to load flywheel-bids package, make sure it is installed!')

    def _get_invocation(self):
        """Load the invocation"""
        if self._invocation is None:
            cfg_path = os.path.join(self._path, 'config.json')
            try:
                with open(cfg_path, 'r') as f:
                    self._invocation = json.load(f)
            except Exception:
                self.log.exception('Cannot load config.json at <%s>', cfg_path)
                raise

        return self._invocation

    def _update_metadata(self, container_type, metadata, file_name=None):
        dest = self._metadata.setdefault(container_type, {})
        if file_name:
            files = dest.setdefault('files', [])
            file_entry = None
            for fe in files:
                if fe.get('name') == file_name:
                    file_entry = fe
                    break
            if file_entry is None:
                file_entry = {'name': file_name}
                files.append(file_entry)
            dest = file_entry

        dest.update(metadata)

    @staticmethod
    def _create_update_dict(args, kwargs):
        result = copy.deepcopy(kwargs) or {}
        if len(args) > 0:
            if len(args) > 1 or not isinstance(args[0], dict):
                raise ValueError('Expected at most one update dictionary')
            result.update(args[0])
        return result
