"""
    AWS S3 class
"""

import boto3
import io
import os

from botocore.exceptions import ClientError
from hellofresh_data import logging_setup

class S3():
    """
        S3 Helper Class
    """
    def __init__(self):

        self.__location__ = os.getcwd()
        self._logger = logging_setup.init_logging("S3")

    def df_to_s3(self, data_df, s3_bucket_name, file_path):
        """
            Loads data into S3 bucket.

            data_df - pandas DF
            s3_bucket_name - AWS S3 bucket
            file_path - path to file, i.e Folder/SubFolder/file_name.csv

            ex: s3_obj.df_to_s3(df,
                                'hf-us-oa-etl-odl',
                                'IMT/po_master/test_file.csv')
        """

        self._logger.info('Load pandas DataFrame to S3 path, %s/%s',
                          s3_bucket_name,
                          file_path)

        csv_buffer = io.StringIO()
        data_df.to_csv(csv_buffer)

        s3_resource = boto3.resource('s3', region_name="us-east-2")

        try:
            s3_resource.Object(s3_bucket_name,
                               file_path
                               ).put(Body=csv_buffer.getvalue())

            self._logger.info('Loaded "%s" to S3 path, %s',
                              file_path,
                              s3_bucket_name)
        except ClientError as err:
            self._logger.error(err)
