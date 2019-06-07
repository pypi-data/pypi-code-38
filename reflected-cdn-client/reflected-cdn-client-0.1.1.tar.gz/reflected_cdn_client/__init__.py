import os
import time
import pathlib
import ftplib
from io import BytesIO


__all__ = 'retry', 'CDNFile', 'CDNDir', 'CDNClient', 'upload_dir', 'upload_file'


def retry(fn, retries=10, delay=0.2, **kwargs):
    def apply(*a, **kw):
        attempts = 0
        while True:
            attempts += 1
            try:
                return fn(*a, **kw)
            except ftplib.all_errors as e:
                print(f'[Error] {e}')
                time.sleep(delay)
                if attempts == retries:
                    raise e
    return apply


class CDNFile(object):
    __slots__ = 'cdn', 'file', 'path',

    def __init__(self, cdn, file, fn, **kw):
        self.path = pathlib.PurePath(fn)
        self.file = file
        self.cdn = cdn

    def delete(self):
        return self.cdn.delete(str(self.path))

    def rename(self, to):
        return self.cdn.rename(str(self.path), to)

    def delete_local(self):
        return self.path.unlink()


class CDNDir(object):
    __slots__ = 'cdn', 'files', 'path',

    def __init__(self, cdn, files, path, **kw):
        self.path = pathlib.PurePath(path)
        self.files = files
        self.cdn = cdn

    def __iter__(self):
        return iter(self.files)

    def delete(self):
        return self.cdn.delete(str(self.path))

    def rename(self, to):
        return self.cdn.rename(str(self.path), to)

    def delete_local(self):
        for file in self.files:
            file.delete_local()
        return self.path.rmdir()


class CDNClient(ftplib.FTP):
    def __init__(
        self,
        host='',
        user='',
        passwd='',
        acct='',
        timeout=None,
        source_address=None,
        origin='',
        **kw
    ):
        super().__init__(
            host=host,
            user=user,
            passwd=passwd,
            acct=acct,
            timeout=timeout,
            source_address=source_address,
        )
        self.origin = pathlib.PurePath(origin)
        self._cache = set()

    def has_dir(self, dir):
        filelist = []
        self.retrlines('LIST', filelist.append)

        for f in filelist:
            if f.split()[-1] == dir and f.lower().startswith('d'):
                return True

        return False

    def make_dirs(self, ftp_path):
        pwd = self.pwd()
        dirs = [d for d in ftp_path.split('/') if d != '']

        for dir in dirs:
            next_pwd = self.pwd()
            cache_key = os.path.join(next_pwd, dir)

            if cache_key in self._cache:
                found = True
            else:
                found = self.has_dir(dir)

            if not found:
                try:
                    self.mkd(dir)
                    self.sendcmd(f'SITE CHMOD 755 {next_pwd}/{dir}')
                except ftplib.error_perm:
                    pass

            self._cache.add(cache_key)
            self.cwd(dir)

        self.cwd(pwd)

    def upload_fileobj(self, fileobj, fn, buffer_size=10 * 1000 * 1024):
        fn = str(self.origin.joinpath(fn))
        self.make_dirs('/'.join(fn.split('/')[:-1]))
        self.storbinary(f'STOR {fn}', fileobj, blocksize=buffer_size)
        return CDNFile(self, fileobj, fn)

    def upload(self, fn, relative_to=None):
        if relative_to is not None:
            relative_to = pathlib.PurePath(str(relative_to))

        with open(fn, 'rb') as file:
            loc_path = pathlib.PurePath(fn)
            cdn_path = str(loc_path.relative_to(relative_to or loc_path.parent))
            return self.upload_fileobj(file, cdn_path)

    def upload_dir(self, dir, relative_to=None, ignore=None):
        if relative_to is not None:
            relative_to = pathlib.PurePath(str(relative_to))

        dir = pathlib.Path(dir)
        cdn_files = []
        add_file = cdn_files.append

        for root, dirs, files in os.walk(str(dir)):
            root = pathlib.PurePath(root)
            if len(files):
                for fn in files:
                    if ignore is not None:
                        if any(fn.endswith(ignoreable) for ignoreable in ignore):
                            continue
                    local_path = root.joinpath(fn)
                    cdn_path = local_path.relative_to(relative_to or dir.parent)
                    with open(str(local_path), 'rb') as file:
                        add_file(self.upload_fileobj(file, str(cdn_path)))

        return CDNDir(self, cdn_files, dir)

    def delete(self, fn):
        if fn and len(fn.strip()):
            parts = fn.split('/')
            if len(parts) > 1 and '.' in parts[-1]:
                fn = self.origin.joinpath(fn)
                return super().delete(str(fn))


def upload_dir(
    dir,
    relative_to=None,
    ignore=None,
    host=None,
    user=None,
    passwd=None,
    origin=None,
    **kw
):
    with CDNClient(host, origin=origin, user=user, passwd=passwd) as cdn:
        return retry(cdn.upload_dir)(dir, relative_to=relative_to, ignore=ignore)


def upload_file(fn, relative_to, host=None, user=None, passwd=None, origin=None, **kw):
    with CDNClient(host, origin=origin, user=user, passwd=passwd) as cdn:
        return retry(cdn.upload)(fn, relative_to)
