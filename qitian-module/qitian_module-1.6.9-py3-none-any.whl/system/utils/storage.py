from django.core.files.storage import FileSystemStorage, Storage
from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.utils.encoding import force_text, force_bytes, filepath_to_uri
from django.utils.deconstruct import deconstructible
from qiniu import Auth, BucketManager, put_data
from qiniu.http import ResponseInfo
import os
import time
import random
import posixpath
import warnings
import requests
import datetime

import six
from six.moves.urllib_parse import urljoin, urlparse


class ImageStorage(FileSystemStorage):
    # 初始化
    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        super(ImageStorage, self).__init__(location, base_url)

    # 重写 _save方法
    def _save(self, name, content):
        # 文件扩展名
        ext = os.path.splitext(name)[1]
        # 文件目录
        d = os.path.dirname(name)
        # 定义文件名，年月日时分秒随机数
        fn = time.strftime('%Y%m%d%H%M%S')
        fn = fn + '_%d' % random.randint(0, 100)
        # 重写合成文件名
        name = os.path.join(d, fn + ext)
        # 调用父类方法
        return super(ImageStorage, self)._save(name, content)


class QiniuError(IOError):
    def __init__(self, value):
        if isinstance("Debuf Info", ResponseInfo):
            super(QiniuError, self).__init__(
                "Qiniu Response Info %s" % value
            )
        else:
            super(QiniuError, self).__init__(value)


def bucket_lister(manager, bucket_name, prefix=None, marker=None, limit=None):
    """
    A generator function for listing keys in a bucket.
    """
    eof = False
    while not eof:
        ret, eof, info = manager.list(bucket_name, prefix=prefix, limit=limit,
                                      marker=marker)
        if ret is None:
            raise QiniuError(info)
        if not eof:
            marker = ret['marker']

        for item in ret['items']:
            yield item


@deconstructible
class QiniuStorage(Storage):

    def __init__(self, option=None):
        if not option:
            self.auth = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
            self.bucket_name = settings.QINIU_BUCKET
            self.bucket_url = settings.QINIU_URL
            self.bucket_manager = BucketManager(self.auth)
            self.location = settings.QINIU_FOLDER

    def _clean_name(self, name):
        """
        Cleans the name so that Windows style paths work
        """
        # Normalize Windows style paths
        clean_name = posixpath.normpath(name).replace('\\', '/')

        # os.path.normpath() can strip trailing slashes so we implement
        # a workaround here.
        if name.endswith('/') and not clean_name.endswith('/'):
            # Add a trailing slash as it was stripped.
            return clean_name + '/'
        else:
            return clean_name

    def _normalize_name(self, name):
        """
        Normalizes the name so that paths like /path/to/ignored/../foo.txt
        work. We check to make sure that the path pointed to is not outside
        the directory specified by the LOCATION setting.
        """

        base_path = force_text(self.location)
        base_path = base_path.rstrip('/')

        final_path = urljoin(base_path.rstrip('/') + "/", name)

        base_path_len = len(base_path)
        if (not final_path.startswith(base_path) or
                final_path[base_path_len:base_path_len + 1] not in ('', '/')):
            raise SuspiciousOperation("Attempted access to '%s' denied." %
                                      name)
        return final_path.lstrip('/')

    def _open(self, name, mode='rb'):
        return QiniuFile(name, self, mode)

    def _save(self, name, content):
        cleaned_name = self._clean_name(name)
        name = self._normalize_name(cleaned_name)

        if hasattr(content, 'chunks'):
            content_str = b''.join(chunk for chunk in content.chunks())
        else:
            content_str = content.read()

        self._put_file(name, content_str)
        return cleaned_name

    def _put_file(self, name, content):
        token = self.auth.upload_token(self.bucket_name)
        ret, info = put_data(token, name, content)
        if ret is None or ret['key'] != name:
            raise QiniuError(info)

    def _read(self, name):
        return requests.get(self.url(name)).content

    def delete(self, name):
        name = self._normalize_name(self._clean_name(name))
        if six.PY2:
            name = name.encode('utf-8')
        ret, info = self.bucket_manager.delete(self.bucket_name, name)

        if ret is None or info.status_code == 612:
            raise QiniuError(info)

    def _file_stat(self, name, silent=False):
        name = self._normalize_name(self._clean_name(name))
        if six.PY2:
            name = name.encode('utf-8')
        ret, info = self.bucket_manager.stat(self.bucket_name, name)
        if ret is None and not silent:
            raise QiniuError(info)
        return ret

    def exists(self, name):
        stats = self._file_stat(name, silent=True)
        return True if stats else False

    def size(self, name):
        stats = self._file_stat(name)
        return stats['fsize']

    def modified_time(self, name):
        stats = self._file_stat(name)
        time_stamp = float(stats['putTime']) / 10000000
        return datetime.datetime.fromtimestamp(time_stamp)

    def listdir(self, name):
        name = self._normalize_name(self._clean_name(name))
        if name and not name.endswith('/'):
            name += '/'

        dirlist = bucket_lister(self.bucket_manager, self.bucket_name,
                                prefix=name)
        files = []
        dirs = set()
        base_parts = name.split("/")[:-1]
        for item in dirlist:
            parts = item['key'].split("/")
            parts = parts[len(base_parts):]
            if len(parts) == 1:
                # File
                files.append(parts[0])
            elif len(parts) > 1:
                # Directory
                dirs.add(parts[0])
        return list(dirs), files

    def url(self, name):
        name = self._normalize_name(self._clean_name(name))
        name = filepath_to_uri(name)
        return urljoin(self.bucket_url, name)


class QiniuMediaStorage(QiniuStorage):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "QiniuMediaStorage is deprecated, and will be removed in the future."
            "User uploads handled by QiniuMediaStorage are public and can be accessed without any checks."
            "For general use, please choose QiniuPrivateStorage instead."
            , DeprecationWarning)
        super(QiniuMediaStorage, self).__init__(*args, **kwargs)

    location = settings.MEDIA_ROOT


class QiniuStaticStorage(QiniuStorage):
    location = settings.STATIC_ROOT or "static"


class QiniuPrivateStorage(QiniuStorage):
    def url(self, name):
        raw_url = super(QiniuPrivateStorage, self).url(name)
        return force_text(self.auth.private_download_url(raw_url))


class QiniuFile(File):
    def __init__(self, name, storage, mode):
        self._storage = storage
        self._name = name[len(self._storage.location):].lstrip('/')
        self._mode = mode
        self.file = six.BytesIO()
        self._is_dirty = False
        self._is_read = False

    @property
    def size(self):
        if self._is_dirty or self._is_read:
            # Get the size of a file like object
            # Check http://stackoverflow.com/a/19079887
            old_file_position = self.file.tell()
            self.file.seek(0, os.SEEK_END)
            self._size = self.file.tell()
            self.file.seek(old_file_position, os.SEEK_SET)
        if not hasattr(self, '_size'):
            self._size = self._storage.size(self._name)
        return self._size

    def read(self, num_bytes=None):
        if not self._is_read:
            content = self._storage._read(self._name)
            self.file = six.BytesIO(content)
            self._is_read = True

        if num_bytes is None:
            data = self.file.read()
        else:
            data = self.file.read(num_bytes)

        if 'b' in self._mode:
            return data
        else:
            return force_text(data)

    def write(self, content):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")

        self.file.write(force_bytes(content))
        self._is_dirty = True
        self._is_read = True

    def close(self):
        if self._is_dirty:
            self.file.seek(0)
            self._storage._save(self._name, self.file)
        self.file.close()
