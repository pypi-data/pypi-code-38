"""Google Storage API."""

import io

try:
    import StringIO
except ImportError:
    from io import StringIO

from apiclient import http as apihttp
from bits.google.services.base import Base
from googleapiclient.discovery import build


class Storage(Base):
    """Storage class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.storage = build('storage', 'v1', credentials=credentials)

    def delete_bucket(self, bucket):
        """Return a storage bucket."""
        return self.storage.buckets().delete(bucket=bucket).execute()

    def delete_object(self, bucket, name):
        """Delete a storage bucket."""
        params = {
            'bucket': bucket,
            'object': name,
        }
        return self.storage.objects().delete(**params).execute()

    def insert_object(self, bucket, objectName, objectMedia):
        """Create a new object in a storage bucket."""
        params = {
            'bucket': bucket,
            'body': {'name': objectName},
            'media_body': apihttp.MediaIoBaseUpload(
                StringIO.StringIO(objectMedia),
                'application/json'
            ),
        }
        return self.storage.objects().insert(**params).execute()

    def get_bucket(self, bucket):
        """Return a storage bucket."""
        return self.storage.buckets().get(bucket=bucket).execute()

    def get_buckets(self, project, prefix=None):
        """Return list of bucket."""
        buckets = self.storage.buckets()
        request = buckets.list(project=project, prefix=prefix)
        return self.get_list_items(buckets, request, 'items')

    def get_object_media(self, bucket, objectName):
        """Return a storage bucket objects media."""
        params = {
            'bucket': bucket,
            'object': objectName,
        }
        request = self.storage.objects().get_media(**params)

        # The BytesIO object may be replaced with any io.Base instance.
        f = io.BytesIO()
        downloader = apihttp.MediaIoBaseDownload(f, request, chunksize=1024*1024)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        return f

    def get_object(
            self,
            bucket,
            object,
    ):
        """Return a list of storage bucket objects."""
        params = {
            'bucket': bucket,
            'object': object
        }
        objects = self.storage.objects()
        return objects.get(**params).execute()

    def get_objects(
            self,
            bucket,
            fields=None,
            prefix=None,
    ):
        """Return a list of storage bucket objects."""
        params = {
            'bucket': bucket,
            'fields': fields,
            'prefix': prefix,
        }
        objects = self.storage.objects()
        request = objects.list(**params)
        return self.get_list_items(objects, request, 'items')
