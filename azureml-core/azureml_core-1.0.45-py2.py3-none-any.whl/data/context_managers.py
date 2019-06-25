# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""datastore context manager."""
import os
import logging
import re
from six import raise_from
from azureml.exceptions import UserErrorException, RunEnvironmentException
from azureml.core.runconfig import DataReferenceConfiguration
from azureml.core.datastore import Datastore

module_logger = logging.getLogger(__name__)


class DatastoreContextManager(object):
    """Data store context manager for upload/download."""

    def __init__(self, config):
        """Class DatastoreContextManager constructor.

        :param config: the configuration passed to the context manager
        :type config: dict
        """
        self._config = config
        module_logger.debug("Get config {}".format(config))
        self._workspace = self._get_datastore_workspace()

    def __enter__(self):
        """Download files for datastore.

        :return:
        """
        module_logger.debug("Enter __enter__ function of datastore cmgr")
        for key, value in self._config.items():
            df_config = self._to_data_reference_config(value)
            if self._is_download(df_config):
                self._validate_config(df_config, key)
                ds = Datastore(workspace=self._workspace, name=df_config.data_store_name)
                target_path = df_config.data_store_name
                if df_config.path_on_compute:
                    target_path = os.path.join(df_config.data_store_name, df_config.path_on_compute)
                    # The target_path is always set the the data store name with no way
                    # for the user to overwrite this behavior. The user might attempt to use ../ in
                    # the path on compute as a solution but this throws an exception
                    # because the path  is not normalized.
                    # Normalizing the path to allow the user to use up-level references.
                    target_path = os.path.normpath(target_path)
                ds.download(
                    target_path=target_path,
                    prefix=df_config.path_on_data_store,
                    overwrite=df_config.overwrite)
        module_logger.debug("Exit __enter__ function of datastore cmgr")

    def __exit__(self, *exc_details):
        """Upload files for datastore.

        :param exc_details:
        :return:
        """
        module_logger.debug("Enter __exit__ function of datastore cmgr")
        for key, value in self._config.items():
            df_config = self._to_data_reference_config(value)
            if self._is_upload(df_config):
                self._validate_config(df_config, key)
                ds = Datastore(workspace=self._workspace, name=df_config.data_store_name)
                if os.path.isdir(df_config.path_on_compute):
                    ds.upload(
                        src_dir=df_config.path_on_compute,
                        target_path=df_config.path_on_data_store,
                        overwrite=df_config.overwrite)
                elif os.path.isfile(df_config.path_on_compute):
                    ds.upload_files(
                        files=[df_config.path_on_compute],
                        target_path=df_config.path_on_data_store,
                        overwrite=df_config.overwrite)
        module_logger.debug("Exit __exit__ function of datastore cmgr")

    def _get_datastore_workspace(self):
        from azureml.core.workspace import Workspace
        from azureml.core.authentication import AzureMLTokenAuthentication

        try:
            # Load authentication scope environment variables
            subscription_id = os.environ['AZUREML_ARM_SUBSCRIPTION']
            resource_group = os.environ["AZUREML_ARM_RESOURCEGROUP"]
            workspace_name = os.environ["AZUREML_ARM_WORKSPACE_NAME"]
            experiment_name = os.environ["AZUREML_ARM_PROJECT_NAME"]
            run_id = os.environ["AZUREML_RUN_ID"]

            # Initialize an AMLToken auth, authorized for the current run
            token = os.environ['AZUREML_RUN_TOKEN']
            token_expiry_time = os.environ.get('AZUREML_RUN_TOKEN_EXPIRY',
                                               AzureMLTokenAuthentication._parse_expiry_time_from_token(token))
            url = os.environ["AZUREML_SERVICE_ENDPOINT"]
            location = re.compile("//(.*?)\.").search(url).group(1)
        except KeyError as key_error:
            raise_from(RunEnvironmentException(), key_error)
        else:
            auth = AzureMLTokenAuthentication.create(token,
                                                     AzureMLTokenAuthentication._convert_to_datetime(
                                                         token_expiry_time),
                                                     url,
                                                     subscription_id,
                                                     resource_group,
                                                     workspace_name,
                                                     experiment_name,
                                                     run_id)
            # Disabling service check as this code executes in the remote context, without arm token.
            workspace_object = Workspace(subscription_id, resource_group, workspace_name,
                                         auth=auth, _location=location, _disable_service_check=True)
            return workspace_object

    def _validate_config(self, data_reference, key):
        if not data_reference.data_store_name:
            raise UserErrorException("DataReference {} misses the datastore name".format(key))
        if self._is_upload(data_reference) and not data_reference.path_on_compute:
            raise UserErrorException("DataReference {} misses the relative path on the compute".format(key))

    def _to_data_reference_config(self, config):
        return DataReferenceConfiguration(
            datastore_name=config.get("DataStoreName", None),
            mode=config.get("Mode", "mount").lower(),
            path_on_datastore=config.get("PathOnDataStore", None),
            path_on_compute=config.get("PathOnCompute", None),
            overwrite=config.get("Overwrite", False))

    def _is_download(self, data_reference):
        return data_reference.mode.lower() == 'download'

    def _is_upload(self, data_reference):
        return data_reference.mode.lower() == 'upload'
