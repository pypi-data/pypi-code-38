# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Factory class that automatically selects the appropriate cache store."""
from typing import Any, Optional
import logging

from automl.client.core.common.cache_store import CacheStore, FileCacheStore, MemoryCacheStore, \
    DEFAULT_TASK_TIMEOUT_SECONDS
from automl.client.core.common.pickler import ChunkPickler
from azureml.train.automl._azurefilecachestore import AzureFileCacheStore
from azureml.train.automl.constants import ComputeTargets


class CacheStoreFactory:

    # TODO: simplify this
    @staticmethod
    def get_cache_store(enable_cache: bool,
                        run_target: str = ComputeTargets.LOCAL,
                        run_id: Optional[str] = None,
                        data_store: Optional[Any] = None,
                        temp_location: Optional[str] = None,
                        task_timeout: int = DEFAULT_TASK_TIMEOUT_SECONDS,
                        logger: Optional[logging.Logger] = None) -> CacheStore:
        """Get the cache store based on run type."""
        try:
            if (run_target == "local" and run_id is not None and enable_cache)\
                    or (run_target == 'adb' and data_store is None and enable_cache):
                return FileCacheStore(
                    path=temp_location,
                    module_logger=logger,
                    pickler=ChunkPickler(),
                    task_timeout=task_timeout)

            if run_id is not None and data_store is not None and enable_cache:
                return AzureFileCacheStore(
                    path=run_id,
                    account_key=data_store.account_key,
                    account_name=data_store.account_name,
                    module_logger=logger,
                    temp_location=temp_location,
                    task_timeout=task_timeout)
        except Exception as e:
            if logger:
                logger.warning("Failed to get store, fallback to memorystore {}, {}".format(run_id, e))

        return MemoryCacheStore()
