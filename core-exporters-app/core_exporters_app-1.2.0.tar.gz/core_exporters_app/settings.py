""" Core exporters app settings
"""
from django.conf import settings

if not settings.configured:
    settings.configure()

# GridFS
GRIDFS_EXPORTED_COMPRESSED_FILE_COLLECTION = getattr(settings,
                                                     'GRIDFS_EXPORTED_COMPRESSED_FILE_COLLECTION',
                                                     'fs_exporter_compressed_file_collection')
