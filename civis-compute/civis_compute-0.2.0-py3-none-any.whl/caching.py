from __future__ import print_function
from __future__ import division

import os
import sys
import hashlib
import datetime
import sqlite3
import dateutil.parser

import civis

from .defaults import FILEIDCACHE_FILE


class FileIDCache(object):
    """A persistent cache of file IDs on Civis Platform.

    Parameters
    ----------
    cache_file : str, optional
        The location to put the cache. The default location is
        in `civiscompute.defaults`.

    Methods
    -------
    list : list all the files in the cache
    get_fileid : get the file ID for a file
    """
    def __init__(self, client=None, cache_file=FILEIDCACHE_FILE):
        self._cache_file = os.path.expandvars(os.path.expanduser(cache_file))
        self._init_cache()
        self.client = civis.APIClient(resources='all')

    def _hash_func(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _init_cache(self):
        """setup the cache database"""
        if not os.path.exists(self._cache_file):
            pth, name = os.path.split(self._cache_file)
            # suppress any errors if the `~/.civiscompute` directory
            # already exists
            try:
                os.makedirs(pth)
            except OSError:
                pass
            init_db = True
        else:
            init_db = False

        self._conn = sqlite3.connect(self._cache_file, isolation_level=None)

        if init_db:
            self._conn.execute("CREATE TABLE FILES(\n"
                               "HASH TEXT PRIMARY KEY NOT NULL,\n"
                               "ID INT DEFAULT -1,\n"
                               "NAME TEXT DEFAULT NULL,\n"
                               "EXPDATE TEXT DEFAULT NULL);")

    def list(self):
        """List the files in the cache."""
        rows = self._conn.execute(
            'SELECT id, hash, expdate, name from files;').fetchall()
        fmt = "%- 25s %- 32s %- 32s %s"
        print(fmt % ("file id", "hash", "expiration date", "name"))
        for r in rows:
            print(fmt % r)

    def get_fileid(self, fname):
        """Get the file ID for a file.

        If the file is not in the cache or is going to expire in less than 14
        days, it is cached again.

        Parameters
        ----------
        fname : str
            The full path to the file.

        Returns
        -------
        file_id : int
            The file ID.
        """
        file_hash = self._hash_func(fname)
        d = self._conn.execute(
            "SELECT id, expdate from "
            "files where hash='%s';" % file_hash).fetchall()
        if len(d) == 0:
            file_id = self._insert_file(fname, file_hash)
        else:
            file_id = int(d[0][0])
            t_exp = d[0][1]

            # Re-upload if it is going to expire soon.
            if ((dateutil.parser.parse(t_exp) -
                 datetime.datetime.utcnow()) <
                    datetime.timedelta(days=14)):
                try:
                    with open(fname, 'rb') as fp:
                        file_id = civis.io.file_to_civis(
                            fp, 'file', client=self.client)

                    t_exp = self.client.files.get(file_id)['expires_at']

                    self._conn.execute(
                        "UPDATE files SET id=%d, expdate='%s' "
                        "WHERE hash='%s';" % (file_id, t_exp, file_hash))

                except Exception as e:
                    print(
                        "Could not upload file %s and put it into the "
                        "local cache: %s.%s: %s" % (
                            fname, e.__module__, e.__class__.__name__, e),
                        file=sys.stderr)
                    # Passing here since the file is in the files endpoint
                    # so we can still continue with the job
                    pass

        return file_id

    def _insert_file(self, fname, file_hash=None):
        """insert a file"""
        file_hash = file_hash or self._hash_func(fname)
        try:
            with open(fname, 'rb') as fp:
                file_id = civis.io.file_to_civis(
                    fp, 'file', client=self.client)

            t_exp = self.client.files.get(file_id)['expires_at']

            self._conn.execute(
                "INSERT INTO files VALUES ('%s', %d, '%s', '%s');" % (
                    file_hash, file_id, os.path.abspath(fname), t_exp))

        except Exception as e:
            print(
                "Could not upload file %s and put it into the "
                "local cache: %s.%s: %s" % (
                    fname, e.__module__, e.__class__.__name__, e),
                file=sys.stderr)
            sys.exit(-1)

        return file_id
