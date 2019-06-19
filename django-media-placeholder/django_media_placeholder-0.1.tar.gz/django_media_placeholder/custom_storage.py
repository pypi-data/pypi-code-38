from urllib.parse import urljoin
from urllib.request import urlopen

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.validators import get_available_image_extensions

from django_media_placeholder.utils import extract_extension


class OverwritingStorage(FileSystemStorage):
    """
    File storage that allows overwriting of stored files.
    """

    def get_remote_file(self, name):
        try:
            file_url = urljoin(settings.ALTERNATIVE_MEDIA_URL, name)
            file_content = urlopen(file_url)
            self.save(name, file_content, 999)

        except Exception as e:
            return e

        return True

    def check_remote_download(self, name):
        ext = extract_extension(name)[1:]
        return ext in get_available_image_extensions()

    def open(self, name, mode='rb'):
        """
        Retrieves the specified file from storage.
        """

        if self.exists(name):
            return self._open(name, mode)

        elif self.check_remote_download():
            self.get_remote_file(name)
        
        return self._open(name, mode)
