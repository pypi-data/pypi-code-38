# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module to manage all the Dataset enums."""

from enum import Enum


class HistogramCompareMethod(Enum):
    """Select the metric used to measure the difference between distributions of numeric columns in two profiles."""

    WASSERSTEIN = 0  #: Selects Wasserstein distance metric
    ENERGY = 1  #: Selects Energy distance metric


class PromoteHeadersBehavior(Enum):
    """Control how column headers are read from files."""

    NO_HEADERS = 0  #: No column headers are read
    ONLY_FIRST_FILE_HAS_HEADERS = 1  #: Read headers only from first row of first file, everything else is data.
    COMBINE_ALL_FILES_HEADERS = 2  #: Read headers from first row of each file, combining identically named columns.
    ALL_FILES_HAVE_SAME_HEADERS = 3  #: Read headers from first row of first file, drops first row from other files.


class SkipLinesBehavior(Enum):
    """Control how leading rows are skipped from files."""

    NO_ROWS = 0  #: All rows from all files are read, none are skipped.
    FROM_FIRST_FILE_ONLY = 1  #: Skip rows from  first file, reads all rows from other files.
    FROM_ALL_FILES = 2  #: Skip rows from each file.


class FileEncoding(Enum):
    """File encoding options."""

    UTF8 = 0
    ISO88591 = 1
    LATIN1 = 2
    ASCII = 3
    UTF16 = 4
    UTF32 = 5
    UTF8BOM = 6
    WINDOWS1252 = 7


class FileType(Enum):
    """Deprecated. class of the representation of a FileTypes."""

    import warnings
    warnings.warn(
        "FileType Enum is Deprecated in > 1.0.39. Use strings instead.",
        category=DeprecationWarning)

    GENERIC_CSV = "GenericCSV"
    GENERIC_CSV_NO_HEADER = "GenericCSVNoHeader"
    GENERIC_TSV = "GenericTSV"
    GENERIC_TSV_NO_HEADER = "GenericTSVNoHeader"
    ZIP = "Zip"
    UNKNOWN = "Unknown"
