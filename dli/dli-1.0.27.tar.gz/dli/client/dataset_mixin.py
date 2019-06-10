from dli.client.dataset_functions import DatasetFunctions
from dli.client.datafile_functions import DatafileFunctions
from dli.client.auto_reg_metadata_functions import AutoRegMetadataFunctions


"""
Aggregate mixin of Dataset and related entities.
"""

class DatasetMixin(DatasetFunctions, DatafileFunctions, AutoRegMetadataFunctions):
    pass