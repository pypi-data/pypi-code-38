# -*- coding: utf-8 -*-
import logging
try:
    from .gcs import GCSObjectStore, BackendGCSObjectStore
except ImportError as ex:
    logging.debug("ImportError: %s", ex)
    GCSObjectStore = None
    BackendGCSObjectStore = None

from .null_storage import NullObjectStore
from .disk_object_store import DiskObjectStore
