import cerberus
import botocore
import datetime
from decimal import Decimal, InvalidOperation
from geopy.location import Point

from metagenomi.config import TIME_FMT
from metagenomi.db import (S3resource, S3)

'''
Custom validator
'''


class MgValidator(cerberus.Validator):
    def _validate_type_nonestring(self, value):
        if value == "None":
            return True

    def _validate_type_datestring(self, value):
        try:
            datetime.datetime.strptime(value, TIME_FMT)
        except ValueError:
            return False
        return True

    def _validate_type_s3path(self, path):
        # Check if s3 path exists (i.e. if there are objects with this prefix)
        try:
            bucket = path.split('/')[2]
            key = '/'.join(path.split('/')[3:])
        except IndexError:
            return False

        result = S3.list_objects(Bucket=bucket, Prefix=key)
        if 'Contents' in result:
            return True
        return False

    def _validate_type_s3file(self, file):
        # LOAD works better than HEAD
        # Check if a specific key (object) exists
        try:
            bucket = file.split('/')[2]
            key = '/'.join(file.split('/')[3:])
        except IndexError:
            return False

        try:
            S3resource.Object(bucket, key).load()
        except botocore.exceptions.ClientError:
            return False
        return True

    def _validate_type_mgid(self, value):
        if len(value) == 22:
            if len(value.split('_')) == 4:
                p = value[:4]
                n = value.split('_')[1]
                c = value.split('_')[2]
                t = value.split('-')[-1]
                if p.isalpha() and p.isupper():
                    if len(n) == 4:
                        if len(c) == 3:
                            if t in ['read', 'samp', 'assm', 'tran']:
                                return True
        return False

    def _validate_type_decimal(self, value):
        try:
            d = Decimal(value)
            if d.as_tuple().exponent < -3:
                return False
        except InvalidOperation:
            return False
        return True

    # TODO: intermittent error with this one (possibly fixed?)
    # 68.3532, 19.0477
    def _validate_type_latlon(self, value):
        try:
            p = Point(value)
        except Exception:
            return False

        return True
