# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.storage.blob import BlockBlobService
from ..environ import SparkEnv, PandasEnv
from multimethods import multimethod
from pandas import read_csv
from pyspark.sql import SparkSession
from io import StringIO

azure_storage_account_name = "azureopendatastorage"
azure_storage_container_name = "zipcode"
azure_storage_relative_path = '/zipcodeMapping.csv'
azure_storage_sas_token = (
    r'?sp=r&st=2019-01-16T08:05:00Z&se=2069-01-16T08:05:00Z&sv=2018-03-28'
    # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Offline sas token")]
    r'&sig=2A94YxzePdwYNCxG8FSDWN8GRGsP8%2B0X1q8K8QjGukE%3D&sr=b')


@multimethod(SparkEnv)
def load_zipcode_mapping(env):
    wasbs_path = 'wasbs://%s@%s.blob.core.windows.net/%s' % (
        azure_storage_container_name,
        azure_storage_account_name,
        azure_storage_relative_path)

    spark = SparkSession.builder.getOrCreate()
    spark.conf.set('fs.azure.sas.%s.%s.blob.core.windows.net' % (
        azure_storage_container_name, azure_storage_account_name),
        azure_storage_sas_token)

    return spark.read.csv(wasbs_path, header=True, inferSchema=True)


@multimethod(PandasEnv)
def load_zipcode_mapping(env):
    blob_service = BlockBlobService(
        account_name=azure_storage_account_name,
        sas_token=azure_storage_sas_token.lstrip('?'))

    blob = blob_service.get_blob_to_text(
        azure_storage_container_name,
        azure_storage_relative_path.lstrip('/'))

    return read_csv(StringIO(blob.content))
