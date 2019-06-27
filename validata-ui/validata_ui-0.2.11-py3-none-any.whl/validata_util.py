""" Call validation code """

import logging
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

log = logging.getLogger(__name__)


class ValidataResource(ABC):
    """A resource to validate: url or uploaded file"""

    def __init__(self, type_):
        self.type = type_

    @abstractmethod
    def build_tabulator_stream_args(self):
        """return (source, option_dict)"""
        pass


class URLValidataResource(ValidataResource):
    """URL resource"""

    def __init__(self, url):
        """Built from URL"""
        super().__init__('url')
        self.url = url
        self.filename = Path(urlparse(url).path).name

    def build_tabulator_stream_args(self):
        """URL implementation"""
        return (self.url, {})


class UploadedFileValidataResource(ValidataResource):
    """Uploaded file resource"""

    def __init__(self, filename, bytes_content):
        """Built from file name and content"""
        super().__init__('file')
        self.filename = filename
        self.content = bytes_content

    def build_reader(self):
        return BytesIO(self.content)

    def __detect_format_from_file_extension(self):
        ext = Path(self.filename).suffix
        if ext in ('.csv', '.tsv', '.ods', '.xls', '.xlsx'):
            return ext[1:]
        return None

    def build_tabulator_stream_args(self):
        """Uploaded file implementation"""
        options = {
            'scheme': 'stream',
            'format': self.__detect_format_from_file_extension()
        }
        return (self.build_reader(), options)
