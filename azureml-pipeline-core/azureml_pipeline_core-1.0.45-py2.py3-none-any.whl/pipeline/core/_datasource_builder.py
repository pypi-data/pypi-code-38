# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""datasource_builder.py, module for building a datasource."""
from abc import abstractmethod, ABCMeta
import hashlib
import os


class _DatasourceBuilder(object):
    """
    Encapsulates logic to build a datasource by interacting with a workflow_provider
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_fingerprint(self):
        """
        Calculate and return a deterministic unique fingerprint for the datasource
        :return: fingerprint
        :rtype str
        """
        pass

    @abstractmethod
    def build(self):
        """
        Build the datasource and register it with the provider
        :return: datasource_id
        :rtype str
        """
        pass

    @property
    @abstractmethod
    def datasource_def(self):
        """datasource def."""
        pass

    @staticmethod
    def _default_content_hash_calculator(hash_paths):
        hash_src = []
        for hash_path in hash_paths:
            if os.path.isfile(hash_path):
                hash_src.append(hash_path)
            elif os.path.isdir(hash_path):
                for root, dirs, files in os.walk(hash_path, topdown=True):
                    hash_src.extend([os.path.join(root, name) for name in files])
            else:
                raise ValueError("path not found %s" % hash_path)

        if len(hash_src) == 0:
            hash = "00000000000000000000000000000000"
        else:
            hasher = hashlib.md5()
            for f in hash_src:
                with open(str(f), 'rb') as afile:
                    buf = afile.read()
                    hasher.update(buf)
            hash = hasher.hexdigest()
        return hash

    @staticmethod
    def calculate_hash(datasource_def):
        """
        Calculate hash of datasource
        :param datasource_def: datasource def
        :type datasource_def: DatasourceDef
        """
        return datasource_def.calculate_hash()


class _DataReferenceDatasourceBuilder(_DatasourceBuilder):
    """
    _DataReferenceDatasourceBuilder.
    """

    def __init__(self, context, datasource_def):
        """Initialize _DataReferenceDatasourceBuilder.
        :param context: context object
        :type context: _GraphContext
        :param datasource_def: datasource definition object
        :type datasource_def: DataSourceDef
        """
        self._datasource_provider = context.workflow_provider.datasource_provider
        self._datasource_def = datasource_def

    def get_fingerprint(self):
        """
        Get a fingerprint.
        :return datasource hash
        :rtype str
        """
        datasource_hash = _DatasourceBuilder.calculate_hash(self._datasource_def)
        return datasource_hash

    def build(self):
        """
        Build a datasource.
        :return datasource id
        :rtype str
        """
        fingerprint = self.get_fingerprint()
        datasource_id = self._datasource_provider.upload(datasource_def=self._datasource_def, fingerprint=fingerprint)
        return datasource_id

    @property
    def datasource_def(self):
        """
        Get a datasource definition.
        :return _datasource_def
        :rtype DataSourceDef
        """
        return self._datasource_def
