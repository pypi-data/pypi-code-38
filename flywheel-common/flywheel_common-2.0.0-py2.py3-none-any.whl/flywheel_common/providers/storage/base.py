"""Provides the BaseStorageProvider base class"""
from abc import abstractmethod
import uuid

from ..creds import Creds
from ..provider import BaseProvider
from ...errors import *
from ...storage.interface import Interface
from ...storage import create_flywheel_fs

class BaseStorageProvider(BaseProvider):
    """The base storage provider object. Provides interface for storage type providers"""

    # Local composite objects
    _storage_plugin = None
    _storage_plugin_type = None

    # The schema for validating configuration (required)
    _schema = None

    config = None
    creds = None

    def __init__(self, **kwargs):
        """Initializes this class with the given configuration

        Args:
            creds (Creds): The provider credentials object
            config (dict): The configuration object for storage
        """
        super(BaseStorageProvider, self).__init__(**kwargs)

        # Storage needs a validate before trying to create the FS plugin as we need those fields
        self.origin = {'type': 'system', 'id': 'system'}
        self.validate()
        del self.origin

        self._storage_plugin = create_flywheel_fs(self._storage_plugin_type, config=self.config, creds=self.creds)

    @property
    def storage_plugin(self):
        """
            Allow access to the internal storage plugin
            :rtype Interface: The storage plugin implementation
        """
        return self._storage_plugin


    def _test_files(self):
        """
            Use the provider to upload to the plugins and then read from the plugin
            This is seperated so that we can use the provider after we verify the keys are correct
        """

        test_uuid = str(uuid.uuid4())

        try:
            test_file = self._storage_plugin.open(test_uuid, None, 'wb')
            test_file.write('This is a permissions test')
            test_file.close()
        except:
            raise PermissionError('Error writing data to the storage plugin')

        try:
            test_file = self._storage_plugin.open(test_uuid, None, 'rb')
            result = test_file.read()
            test_file.close()
        except:
            raise PermissionError('Error reading data from the storage plugin')
        finally:
            try:
                self.storage_plugin.remove_file(test_uuid, None)
            except:
                pass

        if result != 'This is a permissions test':
            raise ResourceError('The data written to storage does not match what was expected')

        try:
            self._storage_plugin.remove_file(test_uuid, None)
        except:
            raise PermissionError('Error removing files from the storage plugin')
