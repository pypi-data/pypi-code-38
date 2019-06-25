""" File utils base class for Linux servers. """

import os
import sys
import types
import socket
import logging
import subprocess
from functools import lru_cache

import stat as libstat

from urllib.parse import urlparse

from ... import FileUtils as FileUtilsBase

logger = logging.getLogger(__name__)

__all__ = ['FileUtils',]

if sys.platform == 'darwin':
    PING_CMD = 'ping -c 1 -W 1000 '
else:
    PING_CMD = 'ping -c 1 -w 1 '

class FileUtils(FileUtilsBase):
    DEFAULT_TIMEOUT_SECONDS = 60
    DEFAULT_COPY_TIMEOUT_SECONDS = 1200

    def close(self):
        """ Deallocate any resources being held.  """
        for child_name, child_obj in self.children.items():
            child_obj.close()

    @lru_cache(maxsize=32)
    def is_valid_ip(self, ip):
        try:
            subprocess.check_call((PING_CMD+ip).split(),
                                  stdout = subprocess.DEVNULL,
                                  stderr = subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False


    def validate_and_parse_url(self, url, calling_method):
        """
        Returns
        -------
        server name, server port, resource path
        """
        parsed_url = urlparse(url)
        if parsed_url.username:
            logger.warning("The fileutils module {} is ignoring username {} "
                "passed as part of the url {} for method {}.  "
                "This must be passed in via testbed object.".\
                format(self.__module__, parsed_url.username,
                url, calling_method))

        if parsed_url.password:
            logger.warning("The fileutils module {} is ignoring password {} "
                "passed as part of the url {} for method {}.  "
                "This must be passed in via testbed object.".\
                format(self.__module__, parsed_url.password,
                url, calling_method))

        server_name_or_ip = parsed_url.hostname

        hostname = self.get_hostname(server_name_or_ip)

        # Convert relative paths to absolute.  Allow specification of a
        # tilde ~ character to indicate home directory.
        #
        # In order to specify a local file without a preceding slash,
        # the 'file://' must be omitted, due to restrictions documented in
        # RFC3986 (sections 3.3 and 5.2).
        path = parsed_url.path
        if self.is_local(url):
            path = os.path.abspath(os.path.expanduser(path))


        return hostname, parsed_url.port, path


    def get_child(self, abstraction_scheme, **kwargs):
        """ Attempt to load a protocol implementation.

        First, attempt to load a native Python implementation.
        If none is available, then attempt to load a curl-based
        implementation.

        Raises
        ------
        `Exception`
            if the requested protocol is not supported, this
            occurs when no plugin can be found.
        """

        try:
            child = super().get_child(abstraction_scheme)
        except Exception:
            curl_abstraction_key = 'curl.'+abstraction_scheme
            logger.debug("The fileutils module {} does not implement "
                "submodule {}.  Attempting to load submodule {}.".\
                format(self.__module__, abstraction_scheme,
                curl_abstraction_key))
            try:
                child = super().get_child(curl_abstraction_key)
            except Exception as exc:
                logger.debug("The fileutils module {} does not support "
                    "protocol {}.".format(self.__module__, abstraction_scheme))
                raise Exception("The protocol {} is not supported.".\
                    format(abstraction_scheme)) from exc

        return child


    def copyfile(self, source, destination,
            timeout_seconds = DEFAULT_COPY_TIMEOUT_SECONDS,
            *args, **kwargs):

        logger.info("Copying file from {} to {} ...".\
            format(source, destination))

        parsed_source = urlparse(source)
        parsed_destination = urlparse(destination)
        from_scheme = parsed_source.scheme
        to_scheme = parsed_destination.scheme

        from_scheme_is_local = self.is_local(source)
        to_scheme_is_local = self.is_local(destination)

        if from_scheme_is_local and to_scheme_is_local:
            raise Exception("fileutils module {} does not allow "
                "copying between two local files.".format(self.__module__))

        if not from_scheme_is_local and not to_scheme_is_local:
            raise Exception("fileutils module {} does not allow "
                "copying between two remote files.".format(self.__module__))


        abstraction_scheme = to_scheme if from_scheme_is_local else from_scheme

        # Get implementation
        child = self.get_child(abstraction_scheme, **kwargs)

        # Execute copy
        return child.copyfile(source, destination, timeout_seconds,
            *args, upload=from_scheme_is_local, **kwargs)



    def dir(self, target,
             timeout_seconds=DEFAULT_TIMEOUT_SECONDS, *args, **kwargs):

        logger.info("Retrieving directory listing for {} ...".\
            format(target))

        parsed_url = urlparse(target)
        scheme = parsed_url.scheme
        if self.is_local(target):
            # Contents requested for local directory
            raise Exception("The fileutils module {} does not implement dir "
                "on a local directory.".format(self.__module__))
        else:
            # Dir requested for remote directory

            # Get implementation
            child = self.get_child(scheme, **kwargs)

            # Execute dir
            return child.dir(target, timeout_seconds,
                *args, **kwargs)


    def stat(self, target,
             timeout_seconds=DEFAULT_TIMEOUT_SECONDS, *args, **kwargs):

        logger.info("Retrieving details for file {} ...".format(target))

        parsed_url = urlparse(target)
        scheme = parsed_url.scheme
        if self.is_local(target):
            # Contents requested for local directory
            raise Exception("The fileutils module {} does not implement stat "
                "on a local directory.".format(self.__module__))
        else:
            # Stat requested for remote directory

            # Get implementation
            child = self.get_child(scheme, **kwargs)

            # Execute stat
            return child.stat(target, timeout_seconds, *args, **kwargs)


    def chmod(self, target, mode,
             timeout_seconds=DEFAULT_TIMEOUT_SECONDS, *args, **kwargs):

        logger.info("Setting permissions of file {} to {} ...".\
            format(target, libstat.filemode(mode)))

        parsed_url = urlparse(target)
        scheme = parsed_url.scheme
        if self.is_local(target):
            # Contents requested for local directory
            raise Exception("The fileutils module {} does not implement chmod "
                "on a local directory.".format(self.__module__))
        else:
            # Chmod requested for remote directory

            # Get implementation
            child = self.get_child(scheme, **kwargs)

            # Execute chmod
            return child.chmod(target, mode, timeout_seconds,
                *args, **kwargs)


    def deletefile(self, target,
             timeout_seconds=DEFAULT_TIMEOUT_SECONDS, *args, **kwargs):

        logger.info("Deleting file {} ...".format(target))

        parsed_url = urlparse(target)
        scheme = parsed_url.scheme
        if self.is_local(target):
            # Contents requested for local directory
            raise Exception("The fileutils module {} does not implement "
                "deletefile on a local directory.".format(self.__module__))
        else:
            # Delete requested for remote directory

            # Get implementation
            child = self.get_child(scheme, **kwargs)

            # Execute chmod
            return child.deletefile(target, timeout_seconds, *args, **kwargs)


    def renamefile(self, source, destination,
            timeout_seconds=DEFAULT_TIMEOUT_SECONDS, *args, **kwargs):

        logger.info("Renaming file {} to {} ...".\
            format(source, destination))

        parsed_source = urlparse(source)
        parsed_destination = urlparse(destination)
        from_scheme = parsed_source.scheme
        to_scheme = parsed_destination.scheme

        from_scheme_is_local = self.is_local(source)
        to_scheme_is_local = self.is_local(destination)

        if from_scheme_is_local and to_scheme_is_local:
            raise Exception("fileutils module {} does not allow "
                "renaming local files.".format(self.__module__))

        if from_scheme_is_local != to_scheme_is_local:
            raise Exception("fileutils module {} requires from/to files to be "
                "renamed to both be remote.  Local files are not supported".\
                format(self.__module__))

        if from_scheme != to_scheme:
            raise Exception("fileutils module {} requires from/to files to be "
                "renamed to have the same protocol.".format(self.__module__))

        scheme = from_scheme

        # Rename requested for remote directory

        # Get implementation
        child = self.get_child(scheme, **kwargs)

        # Execute chmod
        return child.renamefile(source, destination, timeout_seconds,
            *args, **kwargs)
