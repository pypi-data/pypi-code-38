#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module that implements the Abstract backend archive for an hpss backend."""
import os
import sys
from ctypes import cdll, create_string_buffer, cast
from ctypes import c_void_p, c_char_p, c_int, c_size_t, c_long
from ...archive_utils import un_abs_path
from ...config import get_config
from ...exception import ArchiveInterfaceError
from ..abstract.archive import AbstractBackendArchive
from ...id2filename import id2filename

# Due to an update in hpss version we need to lazy load the linked
# c types.  Doing this with dlopen flags. 8 is the UNIX flag Integer for
# RTLD_DEEPBIND.
# RTLD_LAZY is defined as 1 in a Unix environment

RTLD_LAZY = 1
RTLD_DEEPBIND = 8
# pylint: disable=no-member
sys.setdlopenflags(RTLD_LAZY | RTLD_DEEPBIND)
# pylint: enable=no-member
# import cant be at top due to lazy load
# pylint: disable=wrong-import-position
from ..hpss.extended import HpssExtended  # noqa: E402
# pylint: enable=wrong-import-position

# place where hpss lib is installed on a unix machine
HPSS_LIBRARY_PATH = '/opt/hpss/lib/libhpss.so'
# HPSS Values from their documentation
HPSS_AUTHN_MECH_INVALID = 0
HPSS_AUTHN_MECH_KRB5 = 1
HPSS_AUTHN_MECH_UNIX = 2
HPSS_AUTHN_MECH_GSI = 3
HPSS_AUTHN_MECH_SPKM = 4

HPSS_RPC_CRED_SERVER = 1
HPSS_RPC_CRED_CLIENT = 2
HPSS_RPC_CRED_BOTH = 3

HPSS_RPC_AUTH_TYPE_INVALID = 0
HPSS_RPC_AUTH_TYPE_NONE = 1
HPSS_RPC_AUTH_TYPE_KEYTAB = 2
HPSS_RPC_AUTH_TYPE_KEYFILE = 3
HPSS_RPC_AUTH_TYPE_KEY = 4
HPSS_RPC_AUTH_TYPE_PASSWD = 5

SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2


def path_info_munge(filepath):
    """Munge the path for this filetype."""
    return_path = un_abs_path(id2filename(int(filepath)))
    return return_path


class HpssBackendArchive(AbstractBackendArchive):
    """The HPSS implementation of the backend archive."""

    def __init__(self, prefix):
        """Constructor for the HPSS Backend Archive."""
        super(HpssBackendArchive, self).__init__(prefix)
        self._prefix = prefix
        self._sitename = get_config().get('hpss', 'sitename')
        self._file = None
        self._filepath = None
        self._hpsslib = None
        self._latency = 5  # number not significant
        # need to load  the hpss libraries/ extensions
        try:
            self._hpsslib = cdll.LoadLibrary(HPSS_LIBRARY_PATH)
        except Exception as ex:
            err_str = "Can't load hpss libraries with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        # need to authenticate with hpss
        try:
            self.authenticate()
        except Exception as ex:
            err_str = "Can't authenticate with hpss, error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    @staticmethod
    def _check_rcode(rcode, msg):
        """Check if rcode is < 0 and raise error."""
        if rcode < 0:
            raise ArchiveInterfaceError(msg)

    def open(self, filepath, mode):
        """Open an hpss file."""
        # want to close any open files first
        self.close()
        try:
            fpath = un_abs_path(filepath)
            self._filepath = filename = os.path.join(
                self._prefix, path_info_munge(fpath))
            hpss = HpssExtended(self._filepath, self._latency)
            hpss.ping_core(self._sitename)
            hpss.makedirs()
            hpss_fopen = self._hpsslib.hpss_Fopen
            hpss_fopen.restype = c_long
            hpss_fopen.argtypes = [c_char_p, c_char_p]
            self._file = hpss_fopen(filename.encode('utf8'), mode.encode('utf8'))
            self._check_rcode(
                self._file,
                'Failed opening Hpss File, code: ' + str(self._file)
            )
            if self._file == 0:
                raise ArchiveInterfaceError('NULL File returned on open')

            # this stops a race where open seems to start a read async,
            # and then if you delete the file we get a sigabort
            # seeking throws away all the buffers..
            hpss_fseek = self._hpsslib.hpss_Fseek
            hpss_fseek.restype = c_long
            hpss_fseek.argtypes = [c_void_p, c_long, c_int]
            hpss_fseek(self._file, SEEK_SET, 0)

            return self
        except Exception as ex:
            err_str = "Can't open hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def close(self):
        """Close an HPSS File."""
        try:
            if self._file:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core(self._sitename)
                hpss_fflush = self._hpsslib.hpss_Fflush
                hpss_fflush.restype = c_int
                hpss_fflush.argtypes = [c_void_p]
                rcode = hpss_fflush(self._file)
                self._check_rcode(
                    rcode,
                    'Failed to flush hpss file with code: ' + str(rcode)
                )
                hpss_fclose = self._hpsslib.hpss_Fclose
                hpss_fclose.restype = c_int
                hpss_fclose.argtypes = [c_void_p]
                rcode = hpss_fclose(self._file)
                self._check_rcode(
                    rcode,
                    'Failed to close hpss file with code: ' + str(rcode)
                )
                self._file = None
        except Exception as ex:
            err_str = "Can't close hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def read(self, blocksize):
        """Read a file from the hpss archive."""
        try:
            if self._filepath:
                buf = create_string_buffer(blocksize)
                hpss_fread = self._hpsslib.hpss_Fread
                hpss_fread.restype = c_size_t
                hpss_fread.argtypes = [c_void_p, c_size_t, c_size_t, c_void_p]
                rcode = hpss_fread(buf, 1, blocksize, self._file)
                self._check_rcode(
                    rcode,
                    'Failed During HPSS Fread, return value is: ' + str(rcode)
                )
                return buf.raw[:rcode]
        except Exception as ex:
            err_str = "Can't read hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        err_str = 'Internal file path invalid'
        raise ArchiveInterfaceError(err_str)

    def write(self, buf):
        """Write a file to the hpss archive."""
        try:
            if self._filepath:
                buf_char_p = cast(buf, c_char_p)
                hpss_fwrite = self._hpsslib.hpss_Fwrite
                hpss_fwrite.restype = c_size_t
                hpss_fwrite.argtypes = [c_void_p, c_size_t, c_size_t, c_void_p]
                rcode = hpss_fwrite(buf_char_p, 1, len(buf), self._file)
                if rcode != len(buf):
                    raise ArchiveInterfaceError('Short write for hpss file')
        except Exception as ex:
            err_str = "Can't write hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def stage(self):
        """Stage an hpss file to the top level drive."""
        try:
            if self._filepath:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core(self._sitename)
                hpss.stage()
        except Exception as ex:
            err_str = "Can't stage hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def status(self):
        """Get the status of a file in the hpss archive."""
        try:
            if self._filepath:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core(self._sitename)
                return hpss.status()
        except Exception as ex:
            err_str = "Can't get hpss status with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        err_str = 'Internal file path invalid'
        raise ArchiveInterfaceError(err_str)

    def set_mod_time(self, mod_time):
        """Set the mod time for an hpss archive file."""
        try:
            if self._filepath:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core(self._sitename)
                hpss.set_mod_time(mod_time)
        except Exception as ex:
            err_str = "Can't set hpss file mod time with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def set_file_permissions(self):
        """Set the file permissions for an hpss archive file."""
        try:
            if self._filepath:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core(self._sitename)
                rcode = self._hpsslib.hpss_Chmod(self._filepath.encode('utf8'), 0o444)
                self._check_rcode(
                    rcode,
                    'Failed to chmod hpss file with code: ' + str(rcode)
                )
        except Exception as ex:
            err_str = "Can't set hpss file permissions with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def authenticate(self):
        """Authenticate the user with the hpss system."""
        user = get_config().get('hpss', 'user')
        auth = get_config().get('hpss', 'auth')
        rcode = self._hpsslib.hpss_SetLoginCred(
            user.encode('utf8'), HPSS_AUTHN_MECH_UNIX,
            HPSS_RPC_CRED_CLIENT, HPSS_RPC_AUTH_TYPE_KEYTAB, auth.encode('utf8')
        )
        self._check_rcode(
            rcode,
            'Could Not Authenticate, error code is:' + str(rcode) + ' User: ' + user + ' Auth: ' + auth
        )

    def patch(self, file_id, old_path):
        """Move a hpss file."""
        try:
            fpath = un_abs_path(file_id)
            # want to open the hpss file first so that it creates the dirs
            self.open(fpath, 'w')
            new_filepath = self._filepath
            self.close()  # close the file so we can do the rename
            hpss_rename = self._hpsslib.hpss_Rename
            hpss_rename.restype = c_int
            hpss_rename.argtypes = [c_char_p, c_char_p]
            ret_val = hpss_rename(str(old_path), str(new_filepath))
            self._check_rcode(
                ret_val,
                'Hpss rename error. Return val is: ' + str(ret_val)
            )
        except Exception as ex:
            err_str = 'Can not rename hpss file {} to {} with error: {}'.format(
                old_path, new_filepath, str(ex)
            )
            raise ArchiveInterfaceError(err_str)

    def remove(self):
        """Remove the file for an HPSS file."""
        try:
            if self._filepath:
                buf_char_p = cast(self._filepath.encode(), c_char_p)
                rcode = self._hpsslib.hpss_Chmod(buf_char_p, 0o644)
                self._check_rcode(rcode, 'Error chmoding hpss file: {}'.format(rcode))

                hpss_unlink = self._hpsslib.hpss_Unlink
                hpss_unlink.restype = c_int
                hpss_unlink.argtypes = [c_char_p]
                buf_char_p = cast(self._filepath.encode(), c_char_p)
                rcode = hpss_unlink(buf_char_p)
                self._check_rcode(rcode, 'Error removing hpss file: {}'.format(rcode))
            self._filepath = None
        except Exception as ex:
            err_str = "Can't remove hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
