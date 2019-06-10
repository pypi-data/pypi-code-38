# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Boston crime."""

from ._boston_reported_crime_blob_info import BostonReportedCrimeBlobInfo
from .dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from .city_reported_crime import CityReportedCrime
from datetime import datetime
from dateutil import parser


class BostonReportedCrime(CityReportedCrime):
    """Boston city crime class."""

    _default_start_date = parser.parse('2015-06-01')
    _default_end_date = datetime.today()

    """const instance of blobInfo."""
    _blobInfo = BostonReportedCrimeBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)
