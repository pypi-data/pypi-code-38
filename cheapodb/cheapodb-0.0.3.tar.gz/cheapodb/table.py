import os

from cheapodb import logger
from cheapodb.schema import Schema


class Table(object):
    def __init__(self, name: str, schema: Schema):
        self.name = name
        self.schema = schema

    def upload(self, f):
        logger.info(f'Uploading file {f} to {os.path.join(self.schema.name, self.name)}')
        self.schema.db.bucket.upload_file(f, os.path.join(self.schema.name, self.name))
