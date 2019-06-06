# -*- coding: utf-8 -*-
import logging

try:
    from .backend_gcs_object_store import *
except ImportError as ex:
    logging.debug("ImportError: %s", ex)
    BackendGCSObjectStore = None

try:
    from .gcs_object_store import GCSObjectStore
except ImportError as ex:
    logging.debug("ImportError: %s", ex)
    GCSObjectStore = None
