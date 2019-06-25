# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
import subprocess

from datetime import datetime

import logging

from azureml._vendor.azure_storage.common import AccountPermissions
from azureml._vendor.azure_storage.blob import BlockBlobService

module_logger = logging.getLogger(__name__)


def get_wasb_container_url():
    get_wasb_url_cmd = ["hdfs", "getconf", "-confKey", "fs.defaultFS"]
    return subprocess.check_output(get_wasb_url_cmd).strip().decode('utf-8')


def get_regular_container_path(wasb_container_uri):
    module_logger.debug("Remapping wasb to https: {0}".format(wasb_container_uri))
    wasb_regex = r"wasbs?://(.*)@(.*)\.blob.core.windows.net$"
    match = re.search(wasb_regex, wasb_container_uri)

    # Extract storage account name and container name from the above URL
    storage_container_name = match.group(1)
    storage_account_name = match.group(2)
    res = "https://{0}.blob.core.windows.net/{1}".format(
        storage_account_name, storage_container_name)
    module_logger.debug("Mapped to {0}".format(res))
    return res


def get_container_sas(wasb_container_url=None, request_session=None):

    if (wasb_container_url is None):
        # Get the entire wasb container URL
        wasb_container_url = get_wasb_container_url()

    module_logger.debug(
        "Generating container-level Read SAS for {0}".format(wasb_container_url))

    if "blob.core.windows.net" not in wasb_container_url:
        module_logger.debug(
            "Outputs Error: Currently - Only default wasb file systems are supported to generate SAS URLs for Outputs")
        # TODO: log error or something - better handling
        return ""

    wasb_regex = r"wasbs?://(.*)@(.*)\.blob.core.windows.net$"
    match = re.search(wasb_regex, wasb_container_url)

    # Extract storage account name and container name from the above URL
    storage_container_name = match.group(1)
    storage_account_name = match.group(2)

    # Get Encrypted Key #
    ACCOUNT_KEY_CONF_FMT = "fs.azure.account.key.{StorageAccountName}.blob.core.windows.net"
    get_hdfs_encrypted_key_cmd = ["hdfs", "getconf", "-confKey",
                                  ACCOUNT_KEY_CONF_FMT.format(StorageAccountName=storage_account_name)]
    encrypted_key = subprocess.check_output(
        get_hdfs_encrypted_key_cmd).strip().decode('utf-8')

    # Get Decrypted Key #
    get_hdfs_decrypted_key_cmd = ["/usr/lib/hdinsight-common/scripts/decrypt.sh",
                                  "{encrypted_key}".format(encrypted_key=encrypted_key)]
    storage_account_key = subprocess.check_output(get_hdfs_decrypted_key_cmd)

    # Create a block blob service instance
    blob_service = BlockBlobService(
        storage_account_name, storage_account_key, request_session=request_session)
    permissions = AccountPermissions(read=True, list=True)
    container_sas = blob_service.generate_container_shared_access_signature(
        storage_container_name,
        permission=permissions,
        expiry=datetime.max)

    return "?{0}".format(container_sas)
