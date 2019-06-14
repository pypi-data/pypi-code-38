import errno
import logging
import os
import pickle
import re
import shutil
import tarfile
from tempfile import NamedTemporaryFile
from time import sleep
from zipfile import ZipFile

import requests
from googleapiclient.http import MediaIoBaseDownload

from businessoptics.google_drive import google_drive_service, _process_file_with_progress
from businessoptics.utils import only

log = logging.getLogger(__name__)


def isolate_cache():
    """
    Use the download cache in your home folder instead of the shared global_cache.
    """
    CachedFileGetter.only_me = True


class CachedFileGetter(object):
    only_me = False

    def __init__(self, key):
        self.key = key

    def get_and_save(self, path):
        raise NotImplementedError()

    def get_metadata(self):
        return NotImplemented

    def is_cache_valid(self, new_meta, old_meta, path):
        return new_meta == old_meta

    def cache_root_location(self):
        if os.path.isdir('/global_cache') and not self.only_me:
            base = '/global_cache'
        else:
            base = os.path.join(os.path.expanduser('~'), '.download_cache')
        return os.path.join(base, self.__class__.__name__)

    def path(self):
        base = os.path.join(self.cache_root_location(),
                            str(self.key).lstrip('/\\'))
        path = os.path.join(base, 'thefile')
        meta_path = os.path.join(base, 'meta')

        try:
            os.makedirs(base)
        except OSError as exception:
            if exception.errno != errno.EEXIST:

                raise

        new_meta = self.get_metadata()

        cached = os.path.exists(path)
        if new_meta is not NotImplemented:
            if cached:
                try:
                    with open(meta_path, 'rb') as meta_file:
                        old_meta = pickle.load(meta_file)
                except IOError:
                    pass
                else:
                    cached = self.is_cache_valid(new_meta, old_meta, path)

        if not cached:

            # Ensure that if get_and_save gets interrupted, it won't
            # be seen as cached in a future run
            try:
                os.remove(meta_path)
            except OSError as e:
                if e.errno != 2:  # doesn't exist
                    raise

            self.get_and_save(path)

            if new_meta is not NotImplemented:
                with open(meta_path, 'wb') as meta_file:
                    pickle.dump(new_meta, meta_file, protocol=2)

        return path

    def open(self, mode='rb', **kwargs):
        return open(self.path(), mode=mode, **kwargs)

    def unzip(self, member=None, password=None):
        return CachedUnzipper(self.path(), member, password)

    def untar(self, member=None):
        return CachedUnTar(self.path(), member)


class CachedTuplesCSV(CachedFileGetter):
    def __init__(self, has_tuples):
        self.meta = has_tuples.get()
        match = re.match(r'/api/v2/query/\d+/(result/.+)$', has_tuples.base_url)
        if match:
            client = has_tuples.root
            cached_query_url = client.get(self.meta['query'])['from_cache']
            if cached_query_url:
                log.debug('Using cached query at %s', cached_query_url)
                has_tuples = has_tuples.__class__.at(client / cached_query_url / match.group(1))
                self.meta = has_tuples.get()
        self.has_tuples = has_tuples
        super(CachedTuplesCSV, self).__init__(has_tuples.full_url.replace('/', '_'))

    def get_metadata(self):
        return self.meta

    def get_and_save(self, path):
        log.info('Downloading CSV of %s', self.has_tuples.full_url)
        download_url = self.has_tuples.get('external_stream_csv')['download_url']
        with NamedTemporaryFile() as temp_zip_file:
            while True:
                response = requests.get(download_url, stream=True)
                if response.status_code == 200:
                    break
                sleep(5)
            shutil.copyfileobj(response.raw, temp_zip_file)
            temp_zip_file.flush()
            with ZipFile(temp_zip_file) as zipfile:
                extracted_path = zipfile.extract(zipfile.infolist()[0])
        shutil.move(extracted_path, path)
        log.info('Finished downloading CSV')


class CachedGoogleDriveFile(CachedFileGetter):
    """
    Download a file from Google Drive.

    Accepts a file ID or a URL containing it in one of the following formats:

        - https://drive.google.com/open?id=<file ID>
          (obtained by clicking on a file and then 'Get shareable link')
        - https://drive.google.com/file/d/<file ID>/view
          (a link of the first type typically redirects to a link like this)

    Requires the file ~/.google-credentials/client_secret.json. If it's not present it
    will try to download it from S3, so having access to AWS credentials is useful.

    Using this for the first time will require opening a link in a browser, authenticating
    through Google, and pasting a code into the terminal.
    """
    def __init__(self, id_or_link):
        file_id = self.extract_file_id(id_or_link)

        super(CachedGoogleDriveFile, self).__init__(file_id)
        self.file_id = file_id
        self.service = google_drive_service()

    @staticmethod
    def extract_file_id(id_or_link):
        for pattern in [r'drive.google.com/open\?id=([\w_-]+)$',
                        r'drive.google.com/file/\w/([\w_-]+)/\w+$',
                        r'^([\w_-]+)$']:
            match = re.search(pattern, id_or_link)
            if match:
                return match.group(1)
        raise ValueError("Failed to extract file ID from %s", id_or_link)

    def get_metadata(self):
        return self.service.files().get(fileId=self.file_id, fields='md5Checksum').execute()['md5Checksum']

    def get_and_save(self, path):
        log.info('Downloading file %s from Google Drive to %s', self.file_id, path)
        request = self.service.files().get_media(fileId=self.file_id)
        with open(path, 'wb') as outfile:
            downloader = MediaIoBaseDownload(outfile, request)
            _process_file_with_progress('Download', downloader)


class CachedUnzipper(CachedFileGetter):
    def __init__(self, zip_path, member=None, password=None):
        self.zip_path = os.path.abspath(zip_path)
        self.zipfile = ZipFile(zip_path)
        if member is None:
            member = only(self.zipfile.infolist())
        else:
            member = only(m for m in self.zipfile.infolist() if m.filename == member)

        super(CachedUnzipper, self).__init__(zip_path + '/' + member.filename)
        self.member = member
        self.password = password

    def get_and_save(self, path):
        log.info('Unzipping...')
        with self.zipfile:
            outpath = self.zipfile.extract(self.member, os.path.dirname(path), self.password)
        shutil.move(outpath, path)

    def get_metadata(self):
        stat = os.stat(self.zip_path)
        m = self.member
        return (stat.st_size, stat.st_mtime,
                m.date_time, m.CRC, m.file_size)


class CachedUnTar(CachedFileGetter):
    def __init__(self, tar_path, member=None):
        self.tar_path = os.path.abspath(tar_path)
        self.tarfile = tarfile.open(tar_path)
        if member is None:
            member = only(self.tarfile.getmembers())
        else:
            member = only(m for m in self.tarfile.getmembers() if m.name == member)

        super(CachedUnTar, self).__init__(tar_path + '/' + member.name)
        self.member = member

    def get_and_save(self, path):
        log.info('Extracting tar...')
        dirname = os.path.dirname(path)
        with self.tarfile:
            self.tarfile.extractall(dirname, [self.member])
        shutil.move(os.path.join(dirname, self.member.name),
                    path)

    def get_metadata(self):
        stat = os.stat(self.tar_path)
        m = self.member
        return (stat.st_size, stat.st_mtime,
                m.size, m.mtime)
