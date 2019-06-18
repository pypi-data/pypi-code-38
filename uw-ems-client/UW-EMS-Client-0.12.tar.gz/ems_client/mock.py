"""
EMS API mock data class
"""
from hashlib import md5
import json
from logging import getLogger
from os.path import abspath, dirname, join

from restclients_core.util.mock import convert_to_platform_safe


class EMSMockData(object):
    paths = []

    def __init__(self):
        self._log = getLogger(__name__)

    @classmethod
    def register_mock_path(cls, path):
        if path not in EMSMockData.paths:
            EMSMockData.paths.append(path)

    def get_registered_paths(self):
        return EMSMockData.paths

    def service_mock_paths(self):
        return [abspath(join(dirname(__file__), "resources"))]

    def _get_mock_paths(self):
        return self.get_registered_paths() + self.service_mock_paths()

    def mock(self, portName, methodName, params):
        mock_path = self._mock_file_path(portName, methodName, params)
        for path in self._get_mock_paths():
            resource = join(path, 'ems', 'file')
            mock_data = self._load_mock_resource_from_path(resource, mock_path)
            if mock_data:
                return mock_data

        return ''

    def _load_mock_resource_from_path(self, resource_dir, resource_path):
        orig_file_path = join(resource_dir, resource_path)

        paths = [
            convert_to_platform_safe(orig_file_path),
        ]

        handle = None
        for path in paths:
            try:
                file_path = path
                handle = open(path)
                break
            except IOError:
                pass

        if handle is None:
            return None

        mock_data = handle.read()
        handle.close()

        return mock_data

    def _mock_file_path(self, portName, methodName, params):
        return join(portName, methodName,
                    md5(self._normalize(params)).hexdigest().upper())

    def _normalize(self, params):
        ignored = ['auth']
        normalized = {}

        for k in sorted(params.keys()):
            if k not in ignored:
                normalized[k] = params[k]

        return json.dumps(normalized, sort_keys=True).encode('ascii', 'ignore')
