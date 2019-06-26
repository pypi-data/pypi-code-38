import csv
from io import StringIO
from urllib.parse import urlparse

import requests

from .extension import Extension
from .extension_version import ExtensionVersion
from .exceptions import DoesNotExist, MissingExtensionMetadata


class ExtensionRegistry:
    def __init__(self, extension_versions_data, extensions_data=None):
        """
        Accepts extension_versions.csv and, optionally, extensions.csv as either URLs or data (as string) and reads
        them into ExtensionVersion objects. If extensions_data is not provided, the extension versions will not have
        category or core properties.
        """
        self.versions = []

        # If extensions data is provided, prepare to merge it with extension versions data.
        extensions = {}
        if extensions_data:
            extensions_data = self._resolve(extensions_data)
            for row in csv.DictReader(StringIO(extensions_data)):
                extension = Extension(row)
                extensions[extension.id] = extension

        extension_versions_data = self._resolve(extension_versions_data)
        for row in csv.DictReader(StringIO(extension_versions_data)):
            version = ExtensionVersion(row)
            if version.id in extensions:
                version.update(extensions[version.id])
            self.versions.append(version)

    def filter(self, **kwargs):
        """
        Returns the extension versions in the registry that match the keyword arguments.
        """
        try:
            return list(filter(lambda ver: all(getattr(ver, k) == v for k, v in kwargs.items()), self.versions))
        except AttributeError as e:
            self._handle_attribute_error(e)

    def get(self, **kwargs):
        """
        Returns the first extension version in the registry that matches the keyword arguments.
        """
        try:
            return next(ver for ver in self.versions if all(getattr(ver, k) == v for k, v in kwargs.items()))
        except StopIteration:
            raise DoesNotExist('Extension version matching {} does not exist.'.format(repr(kwargs)))
        except AttributeError as e:
            self._handle_attribute_error(e)

    def __iter__(self):
        """
        Iterates over the extension versions in the registry.
        """
        for version in self.versions:
            yield version

    def _resolve(self, data_or_url):
        parsed = urlparse(data_or_url)
        if parsed.scheme:
            if parsed.scheme == 'file':
                with open(data_or_url[7:]) as f:
                    return f.read()
            return requests.get(data_or_url).text
        return data_or_url

    def _handle_attribute_error(self, e):
        if "'category'" in str(e.args) or "'core'" in str(e.args):
            raise MissingExtensionMetadata('ExtensionRegistry must be initialized with extensions data.') from e
        raise
