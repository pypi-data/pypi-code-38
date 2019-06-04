# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)
"""This script enables users to read parquet files as
pandas dataframe and lets them write back to the location
after analysing or modifying the dataframe"""

from os import path
from io import BytesIO
import logging
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
from urllib.parse import urlparse


logger = logging.getLogger("dativa.tools.pandas.parquet")

class ParquetHandler(object):
    """
    ParquetHandler class, specify path of parquet file,
    and get pandas dataframe for analysis and modification.
    :param base_path                       : The base location where the parquet_files
                                             are stored.
    :type base_path                        : str
    :param row_group_size                  : The size of the row groups while writing out
                                             the parquet file.
    :type row_group_size                   : int
    :param use_dictionary                  : Specify whether to use boolean encoding or not
    :type use_dictionary                   : bool
    :param use_deprecated_int96_timestamps : Write nanosecond resolution timestamps
                                             to INT96 Parquet format.
    :type use_deprecated_int96_timestamps  : bool
    :param coerce_timestamps               : Cast timestamps a particular resolution.
                                             Valid values: {None, 'ms', 'us'}
    :type coerce_timestamps                : str
    :param compression                     : Specify the compression codec.
    :type compression                      : str
    """

    S3_PREFIX = "s3://"
    compression_standards = (None, 'snappy', 'gzip', None, 'brotli')
    def __init__(self,
                 base_path="",
                 row_group_size=None,
                 use_dictionary=None,
                 use_deprecated_int96_timestamps=None,
                 coerce_timestamps=None,
                 compression="snappy"):

        self.base_path = self._validate_base_path(base_path)
        self.row_group_size = self._validate_row_group_size(row_group_size)
        self.use_dictionary = self._validate_use_dictionary(use_dictionary)
        self.use_deprecated_int96_timestamps = self._validate_use_deprecated_int96_timestamps(use_deprecated_int96_timestamps)
        self.coerce_timestamps = self._validate_coerce_timestamps(coerce_timestamps)
        self.compression = self._validate_compression(compression)

    @classmethod
    def _validate_compression(cls, compression):
        logger.info("Validating compression argument...")
        if compression not in cls.compression_standards:
            raise ValueError("Invalid compressions {0} specified".format(compression))
        return compression

    @staticmethod
    def _validate_base_path(base_path):
        logger.info("Validating base_path argument...")
        if base_path == "" or path.exists(base_path):
            return base_path
        else:
            raise ValueError("The specified base_path, {0},"\
                             " does not exist.".format(base_path))

    @staticmethod
    def _validate_row_group_size(row_group_size):
        logger.info("Validating row_group_size argument...")
        if (row_group_size is None) or (row_group_size > 0):
            return row_group_size
        else:
            raise ValueError("Invalid row group size passed, {0}".format(row_group_size))

    @staticmethod
    def _validate_use_dictionary(use_dictionary):
        logger.info("Validating use_dictionary argument...")
        if (use_dictionary is None) or isinstance(use_dictionary, bool):
            return use_dictionary
        else:
            raise ValueError("Invalid arguement passed for use_dictionary"\
                             " expected boolean or list got {0} instead".format(type(use_dictionary)))

    @staticmethod
    def _validate_use_deprecated_int96_timestamps(use_deprecated_int96_timestamps):
        logger.info("Validating use_deprecated_int96_timestamps argument...")
        if (use_deprecated_int96_timestamps is None) or (isinstance(use_deprecated_int96_timestamps, bool)):
            return use_deprecated_int96_timestamps
        else:
            raise ValueError("Invalid arguement passed for use_deprecated_int96_timestamps"\
                             " expected boolean or NoneType, got {0} instead".format(type(use_deprecated_int96_timestamps)))

    @staticmethod
    def _validate_coerce_timestamps(coerce_timestamps):
        logger.info("Validating coerce_timestamps argument...")
        if coerce_timestamps in (None, 'ms', 'us'):
            return coerce_timestamps
        else:
            raise ValueError("Invalid argument passed for coerce_timestamps"\
                             " allowed values are None, us, ms")

    @staticmethod
    def _get_parquet_file(file_to_read):
        logger.info("Reading parquet file from location...")
        _bytes = BytesIO()
        with open(file_to_read, 'rb') as file_obj:
            _bytes.write(file_obj.read())
        parquet_file = pq.ParquetFile(_bytes)
        return parquet_file

    @staticmethod
    def _s3_path_to_bucket(url):
        s3_bucket = None
        s3_key = ""
        if url:
            parsed_s3_url = urlparse(url)
            if parsed_s3_url and parsed_s3_url.scheme.lower() == "s3":
                s3_bucket = parsed_s3_url.netloc
                if parsed_s3_url.path:
                    s3_key = parsed_s3_url.path.lstrip('/')
        return s3_bucket, s3_key

    @classmethod
    def _get_parquet_file_s3(cls, path):
        s3 = boto3.client("s3")
        bucket, key = cls._s3_path_to_bucket(path)
        obj = s3.get_object(Bucket=bucket, Key=key)
        parquet_file = pq.ParquetFile(BytesIO(obj['Body'].read()))
        return parquet_file

    def load_df(self, file_name, required_cols=None, read_row_group=-1):
        """
        :param file_name      : The name of the file to be read
        :type file_name       : str
        :param required_cols  : The columnnames of the file
                                to read.
        :type required_cols   : List of str
        :param read_row_group : Row group number to read
        :type read_row_group  : int

        :return               : a dataframe representation of the parquet file
        :rtype                : pandas.DataFrame
        """

        file_name = path.join(self.base_path, file_name)
        if file_name.startswith(self.S3_PREFIX):
            parquet_file = self._get_parquet_file_s3(file_name)
        else:
            parquet_file = self._get_parquet_file(file_name)

        self.row_group_size = self._get_row_group_size(parquet_file)
        # TODO: how can we evaluate these from the file?
        # self.use_dictionary =
        # self.use_deprecated_int96_timestamps =
        # self.coerce_timestamps =
        self.compression = self._get_columnwise_compression(parquet_file)

        if read_row_group >= 0 and required_cols:
            table = parquet_file.read_row_group(read_row_group,
                                                columns=required_cols)
        elif read_row_group >= 0:
            table = parquet_file.read_row_group(read_row_group)
        elif required_cols:
            table = parquet_file.read(columns=required_cols)
        else:
            table = parquet_file.read()
        logger.info("Converting pyarrow table to dataframe...")
        return table.to_pandas()

    @staticmethod
    def _get_row_group_size(parquet_file):
        if parquet_file.num_row_groups > 1:
            return round(parquet_file.metadata.num_rows / parquet_file.num_row_groups)

    def _get_columnwise_compression(self, parquet_file):
        compression_dict = dict()
        columns = parquet_file.schema.names
        logger.info("Obtaining columnwise copression from parquet file...")
        for col_no, col_name in enumerate(columns):
            compression = parquet_file.metadata.row_group(0).column(col_no).compression.lower()
            if compression:
                compression_dict[col_name] = compression
        if compression_dict:
            compression = compression_dict
            uniq_compressions = set(compression_dict.values())
            if len(uniq_compressions) == 1:
                compression = list(uniq_compressions)[0]
        if compression != 'uncompressed':
            return compression

    def save_df(self, df, file_name,
                row_group_size=None,
                use_dictionary=None,
                use_deprecated_int96_timestamps=None,
                coerce_timestamps=None,
                compression=None):
        """
        :param df                              : A pandas dataframe to write to
                                                 original file location of parquet file.
        :type df                               : pandas.DataFrame
        :param row_group_size                  : The size of the row groups while writing out
                                                 the parquet file.
        :type row_group_size                   : int
        :param use_deprecated_int96_timestamps : Write nanosecond resolution timestamps
                                                 to INT96 Parquet format.
        :type use_deprecated_int96_timestamps  : bool
        :param coerce_timestamps               : Cast timestamps a particular resolution.
                                                 Valid values: {None, 'ms', 'us'}
        :type coerce_timestamps                : str
        :param compression                     : Specify the compression codec.
        :type compression                      : str

        :return                                : None
        :rtype                                 : None
        """
        file_name = path.join(self.base_path, file_name)

        if row_group_size is None:
            row_group_size = self.row_group_size
        if use_dictionary is None:
            use_dictionary = self.use_dictionary
        if use_deprecated_int96_timestamps is None:
            use_deprecated_int96_timestamps = self.use_deprecated_int96_timestamps
        if coerce_timestamps is None:
            coerce_timestamps = self.coerce_timestamps
        if self._validate_compression(compression) is None:
            compression = self.compression
        # TODO - Add code to handle parquet files with multiple
        # row groups, write only specific row group, keeping all
        # else the same
        table = pa.Table.from_pandas(df, preserve_index=False)
        if file_name.startswith(self.S3_PREFIX):
            s3 = boto3.client('s3')
            buffer = BytesIO()
            # Stream the data via buffer
            writer = pq.ParquetWriter(buffer,
                                    schema=table.schema,
                                    use_dictionary=use_dictionary,
                                    use_deprecated_int96_timestamps=use_deprecated_int96_timestamps,
                                    coerce_timestamps=coerce_timestamps,
                                    compression=compression)
            writer.write_table(table, row_group_size)
            writer.close()
            buffer.seek(0)
            # Extract bucket name from base path
            s3_bucket, s3_key = self._s3_path_to_bucket(file_name)
            # Save buffered data to file in S3 bucket
            if s3_bucket:
                s3.put_object(Bucket=s3_bucket,
                              Key=s3_key,
                              Body=buffer.read())
        else:
            writer = pq.ParquetWriter(file_name,
                                    schema=table.schema,
                                    use_dictionary=use_dictionary,
                                    use_deprecated_int96_timestamps=use_deprecated_int96_timestamps,
                                    coerce_timestamps=coerce_timestamps,
                                    compression=compression)
            writer.write_table(table, row_group_size)
            writer.close()
