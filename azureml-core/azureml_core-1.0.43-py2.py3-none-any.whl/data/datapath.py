# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""datapath class."""
import uuid
from .data_reference import DataReference


class DataPath(object):
    """Represents a path in a datastore.

    The path can point to a directory or a data artifact (blob, file)
    """

    # TODO DPrep team will extend this implementation with filters
    def __init__(self, datastore=None, path_on_datastore=None, name=None):
        """Initialize DataPath.

        :param datastore: the Datastore to reference
        :type datastore: AbstractAzureStorageDatastore or AzureDataLakeDatastore
        :param path_on_datastore: the relative path on cloud for the data reference
        :type path_on_datastore: str
        :param name: the name for the DataPath, optional.
        :type name: str
        """
        if None in [datastore]:
            raise ValueError('datastore parameter is required.')

        self._datastore = datastore
        self._path_on_datastore = path_on_datastore
        if not name:
            self._name = '{0}_{1}'.format(self.datastore_name, str(uuid.uuid4().hex)[0:8])
        else:
            self._name = name

    def create_data_reference(self, data_reference_name=None, datapath_compute_binding=None):
        """Create a DataReference object using this DataPath and the given DataPathComputeBinding.

        :param data_reference_name:
        :type data_reference_name:
        :param datapath_compute_binding: datapath compute binding to create datareference
        :type datapath_compute_binding: DataPathComputeBinding
        :return: data reference object
        :rtype: DataReference
        """
        if not datapath_compute_binding:
            raise ValueError('datapath_compute_binding is a required parameter')

        if not isinstance(datapath_compute_binding, DataPathComputeBinding):
            raise ValueError('Invalid type. Expected datapath_compute_binding, but type is {0}'.
                             format(type(datapath_compute_binding).__name__))

        return DataReference.create(data_reference_name=data_reference_name, datapath=self,
                                    datapath_compute_binding=datapath_compute_binding)

    @property
    def datastore_name(self):
        """Name of the datastore.

        :return: name
        :rtype: string
        """
        return self._datastore.name

    @property
    def path_on_datastore(self):
        """Path on datastore.

        :return: path
        :rtype: string
        """
        return self._path_on_datastore

    @staticmethod
    def create_from_data_reference(data_reference):
        """Create DataPath from DataReference.

        :param data_reference: datareference to create datapath from
        :type data_reference: DataReference
        :return: datapath object
        :rtype: DataPath
        """
        if not data_reference:
            raise ValueError('data_reference is a required parameter')

        if not isinstance(data_reference, DataReference):
            raise ValueError('Invalid type. Expected DataReference, but type is {0}'.
                             format(type(data_reference).__name__))

        return DataPath(datastore=data_reference.datastore, path_on_datastore=data_reference.path_on_datastore)


class DataPathComputeBinding(object):
    """DataPath compute binding.

    Represents configuration for where a data represented by DataPath will be available in a compute target and how
    (mount or download, whether data can be overwritten).
    """

    def __init__(self, mode='mount', path_on_compute=None, overwrite=False):
        """Initialize DataPathComputeBinding.

        :param mode: the operation on the data reference, we support mount, download
        :type mode: str
        :param path_on_compute: the path on compute for the data reference
        :type path_on_compute: str
        :param overwrite: whether to overwrite the data if existing
        :type overwrite: bool
        """
        self._mode = mode
        self._path_on_compute = path_on_compute
        self._overwrite = overwrite

    def create_data_reference(self, data_reference_name=None, datapath=None):
        """Create DataReference using the given DataPath and this DataPathComputeBinding.

        :param data_reference_name:
        :type data_reference_name:
        :param datapath: datapath to create datareference
        :type datapath: DataPathComputeBinding
        :return: data reference object
        :rtype: DataReference
        """
        if not datapath:
            raise ValueError('datapath is a required parameter')

        if not isinstance(datapath, DataPath):
            raise ValueError('Invalid type. Expected DataReference, but type is {0}'.
                             format(type(datapath).__name__))

        return DataReference.create(datapath=datapath, datapath_compute_binding=self,
                                    data_reference_name=data_reference_name)

    @staticmethod
    def create_from_data_reference(data_reference):
        """Create DataPathComputeBinding from DataReference.

        :param data_reference: datareference to create datapath_compute_binding from
        :type data_reference: DataReference
        :return: datapath compute binding object
        :rtype: DataPathComputeBinding
        """
        if not data_reference:
            raise ValueError('data_reference is a required parameter')

        if not isinstance(data_reference, DataReference):
            raise ValueError('Invalid type. Expected DataReference, but type is {0}'.
                             format(type(data_reference).__name__))

        return DataPathComputeBinding(mode=data_reference.mode, path_on_compute=data_reference.path_on_compute,
                                      overwrite=data_reference.overwrite)
