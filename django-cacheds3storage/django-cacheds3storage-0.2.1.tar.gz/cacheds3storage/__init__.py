import os
from django.core.files.storage import get_storage_class
from storages.backends.s3boto3 import S3Boto3Storage, SpooledTemporaryFile
from django.conf import settings
from dateutil import tz


class CachedS3BotoStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            'compressor.storage.CompressorFileStorage')()

    # Fix for "ValueError: seek of closed file" problem with boto3
    # https://github.com/jschneier/django-storages/issues/382#issuecomment-377174808
    def _save_content(self, obj, content, parameters):
        """
        We create a clone of the content file as when this is passed to boto3 it wrongly closes
        the file upon upload where as the storage backend expects it to still be open
        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified size
        content_autoclose = SpooledTemporaryFile()

        # Write our original content into our copy that will be closed by boto3
        content_autoclose.write(content.read())

        # Upload the object which will auto close the content_autoclose instance
        super(CachedS3BotoStorage, self)._save_content(obj, content_autoclose, parameters)

        # Cleanup if this is fixed upstream our duplicate should always close
        if not content_autoclose.closed:
            content_autoclose.close()

    def save(self, name, content):
        name = super(CachedS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name

    def modified_time(self, prefixed_path):
        # S3Boto3Storage returns a UTC timestamp (which it gets from S3)
        # but an offset-naive one.
        # collectstatic needs to compare that timestamp against
        # a local timestamp (but again an offset-naive one)
        # so here, we need to convert our naive UTC to a naive local
        # takes a few steps...

        # get the offset-naive UTC timestamp
        r = super(CachedS3BotoStorage, self).modified_time(prefixed_path)

        # make it offset-aware
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(settings.TIME_ZONE)
        utc = r.replace(tzinfo=from_zone)

        # convert it to a local offset-aware one
        lcl = utc.astimezone(to_zone)

        # then make it offset-naive
        naive = lcl.replace(tzinfo=None)
        return naive


CompressorS3BotoStorage = lambda: CachedS3BotoStorage(location='media')
MediaRootS3BotoStorage = lambda: S3Boto3Storage(location='uploads')
