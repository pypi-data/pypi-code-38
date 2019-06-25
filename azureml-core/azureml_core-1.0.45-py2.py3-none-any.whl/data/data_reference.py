# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""data reference class."""

import uuid
from azureml.exceptions import UserErrorException


class DataReference(object):
    """A class used to describe how and where data should be made available in a run.

    For more information on how this can be used in training, please refer to the link below:
    https://aka.ms/train-with-datastore.

    For more information on how this can be used in pipeline, please refer to the link below:
    https://aka.ms/pipeline-with-datastore
    """

    def __init__(self, datastore, data_reference_name=None,
                 path_on_datastore=None, mode="mount", path_on_compute=None, overwrite=False):
        """Class DataReference constructor.

        :param datastore: the Datastore to reference
        :type datastore: AbstractAzureStorageDatastore or AzureDataLakeDatastore
        :param data_reference_name: the name of the data reference
        :type data_reference_name: str
        :param path_on_datastore: the relative path on cloud for the data reference
        :type path_on_datastore: str
        :param mode: the operation on the data reference, we support mount, download
        :type mode: str
        :param path_on_compute: the path on compute for the data reference
        :type path_on_compute: str
        """
        self.datastore = datastore
        self.data_reference_name = data_reference_name
        self.path_on_datastore = path_on_datastore
        self.mode = mode
        self.path_on_compute = path_on_compute
        self.overwrite = overwrite

        if not self.data_reference_name and (
                path_on_datastore and not self._is_current_path(path_on_datastore)):
            self.data_reference_name = str(uuid.uuid4().hex)
        elif not self.data_reference_name:
            self.data_reference_name = self.datastore.name
        self._validate_mode(mode)

    def path(self, path=None, data_reference_name=None):
        """Create a DataReference instance based on the given path.

        :param path: the path on the datastore
        :type path: str
        :param data_reference_name: the name of the data reference
        :type data_reference_name: str
        :return: the data reference object
        :rtype: DataReference
        """
        if not path or self._is_current_path(path):
            if data_reference_name:
                return DataReference(
                    datastore=self.datastore,
                    data_reference_name=data_reference_name)
            else:
                return self

        if not self.path_on_datastore or self._is_current_path(self.path_on_datastore):
            return DataReference(
                datastore=self.datastore,
                data_reference_name=data_reference_name,
                path_on_datastore=path)
        else:
            return DataReference(
                datastore=self.datastore,
                data_reference_name=data_reference_name,
                path_on_datastore="{0}/{1}".format(self.path_on_datastore, path)
            )

    def as_download(self, path_on_compute=None, overwrite=False):
        """Switch data reference operation to download.

        The matrix on which computes and datastores support downloading of the data can be found in the link:
        https://aka.ms/datastore-matrix.

        :param path_on_compute: the path on the compute for the data reference
        :type path_on_compute: str
        :param overwrite: whether to overwrite the data if existing
        :type overwrite: bool
        :return: a new data reference object
        :rtype: DataReference
        """
        dref = self._clone()
        dref.path_on_compute = path_on_compute
        dref.mode = "download"
        return dref

    def as_upload(self, path_on_compute=None, overwrite=False):
        """Switch data reference operation to upload.

        The matrix on which computes and datastores support uploading of the data can be found in the link:
        https://aka.ms/datastore-matrix.

        :param path_on_compute: the path on the compute for the data reference
        :type path_on_compute: str
        :param overwrite: whether to overwrite the data if existing
        :type overwrite: bool
        :return: a new data reference object
        :rtype: DataReference
        """
        dref = self._clone()
        dref.path_on_compute = path_on_compute
        dref.mode = "upload"
        return dref

    def as_mount(self):
        """Switch data reference operation to mount.

        The matrix on which computes and datastores support mounting of the data can be found in the link:
        https://aka.ms/datastore-matrix.

        :return: a new data reference object
        :rtype: DataReference
        """
        dref = self._clone()
        dref.mode = "mount"
        return dref

    def to_config(self):
        """Convert the DataReference object to DataReferenceConfiguration object.

        :return: a new azureml.core.runconfig.DataReferenceConfiguration object
        :rtype: azureml.core.runconfig.DataReferenceConfiguration
        """
        from azureml.core.runconfig import DataReferenceConfiguration
        return DataReferenceConfiguration(
            datastore_name=self.datastore.name,
            mode=self.mode,
            path_on_datastore=self._get_normalized_path(self.path_on_datastore),
            path_on_compute=self._get_normalized_path(self.path_on_compute),
            overwrite=self.overwrite)

    def __str__(self):
        """Return string representation of object.

        :return:
        """
        result = "$AZUREML_DATAREFERENCE_{0}".format(self.data_reference_name)
        return result

    def __repr__(self):
        """Return string representation of object.

        :return:
        """
        return self.__str__()

    def _is_current_path(self, path):
        return path == "/" or path == "." or path == "./"

    def _validate_mode(self, mode):
        from azureml.core.runconfig import SUPPORTED_DATAREF_MODES
        message = "Invalid mode {0}. Only mount, download, upload are supported"
        if mode not in SUPPORTED_DATAREF_MODES:
            raise UserErrorException(message.format(mode))

    def _clone(self):
        return DataReference(
            datastore=self.datastore,
            path_on_compute=self.path_on_compute,
            path_on_datastore=self.path_on_datastore,
            mode=self.mode,
            overwrite=self.overwrite
        )

    def _get_normalized_path(self, path):
        result = path
        if (self._is_current_path(path)):
            result = None
        return result

    @staticmethod
    def create(data_reference_name=None, datapath=None, datapath_compute_binding=None):
        """Create a DataReference using DataPath and DataPathComputeBinding.

        :param data_reference_name: name for the data reference to create
        :param datapath: datapath
        :param datapath_compute_binding: datapath compute binding
        :return: DataReference object
        :rtype: DataReference
        """
        if None in [datapath, datapath_compute_binding]:
            raise ValueError('datapath and datapath_compute_binding are expected parameters')

        return DataReference(datastore=datapath._datastore, path_on_datastore=datapath._path_on_datastore,
                             data_reference_name=data_reference_name,
                             mode=datapath_compute_binding._mode,
                             path_on_compute=datapath_compute_binding._path_on_compute,
                             overwrite=datapath_compute_binding._overwrite)
