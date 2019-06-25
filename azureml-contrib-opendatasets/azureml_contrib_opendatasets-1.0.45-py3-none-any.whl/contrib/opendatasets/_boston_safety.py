# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Boston city safety."""

from ._boston_safety_blob_info import BostonSafetyBlobInfo
from .dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from .city_safety import CitySafety
from datetime import datetime
from dateutil import parser


class BostonSafety(CitySafety):
    """Boston city safety class."""

    _default_start_date = parser.parse('2001-01-01')
    _default_end_date = datetime.today()

    """const instance of blobInfo."""
    _blobInfo = BostonSafetyBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)
