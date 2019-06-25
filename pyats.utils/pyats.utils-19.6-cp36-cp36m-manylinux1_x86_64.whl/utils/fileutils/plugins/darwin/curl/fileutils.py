""" Base class for Linux Curl File Utilities.
NOTE : The author is expected to subclass all base class operations
not supported by this protocol and raise a NotImplementedError.
"""

__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. " \
    "All rights reserved."

__author__ = "Myles Dear <pyats-support@cisco.com>"

__all__ = []

import shlex
import logging
import subprocess

from ..fileutils import FileUtils as FileUtilsLinuxBase

logger = logging.getLogger(__name__)


class FileUtilsLinuxCurlBase(FileUtilsLinuxBase):
    """ Base class for all FileUtils curl-based implementations.
    """

    def execute_in_subprocess(self, command, timeout_seconds, **kwargs):
        """ Executes a command in a subprocess.

        Parameters
        ----------
            command : `str`
                The command to run

            timeout_seconds : `int`
                The maximum number of seconds to wait before aborting the
                command execution.

            kwargs : `dict`
                Extra arguments to pass to Popen constructor


        Returns
        -------
            `None`

        Raises
        ------
            `subprocess.CalledProcessError` if error is encountered.

            `subprocess.TimeoutExpired` if the timeout expires before the
            command returns a result.
        """
        if command:
            logger.info("Executing command %s" % command)
            args = shlex.split(command)
            subprocess.check_call(args, timeout=timeout_seconds, shell=False,
                **kwargs)


    def copyfile(self, source, destination,
            timeout_seconds, *args, **kwargs):
        """ Copy a single file.

        Copy a single file either from local to remote, or remote to local.
        Remote to remote transfers are not supported.  Users are expected
        to make two calls to this API to do this.

        Raises
        ------
            Exception : When a remote to remote transfer is requested.
        """
        raise NotImplementedError("The fileutils module {} "
            "does not implement copyfile.".format(self.__module__))


    def dir(self, target, timeout_seconds, *args, **kwargs):
        """ Retrieve filenames contained in a directory.

        Do not recurse into subdirectories, only list files at the top level
        of the given directory.

        Parameters
        ----------
            target : `str`
                The URL of the file whose details are to be retrieved.

            timeout_seconds : `int`
                The number of seconds to wait before aborting the operation.

        Returns
        -------
            `list` : List of filename URLs.  Directory names are ignored.
        """
        raise NotImplementedError("The fileutils module {} "
            "does not implement dir.".format(self.__module__))


    def stat(self, target, timeout_seconds, *args, **kwargs):
        """ Retrieve file details such as length and permissions.

        Parameters
        ----------
            target : `str`
                The URL of the file whose details are to be retrieved.

            timeout_seconds : `int`
                The number of seconds to wait before aborting the operation.

        Returns
        -------
            `os.stat_result` : Filename details including size.

        Raises
        ------
            Exception : timeout exceeded

            Exception : File was not found
        """

        raise NotImplementedError("The fileutils module {} "
            "does not implement stat.".format(self.__module__))


    def chmod(self, target, mode, timeout_seconds, *args, **kwargs):
        """ Change file permissions

        Parameters
        ----------
            target : `str`
                The URL of the file whose permissions are to be changed.

            mode : `int`
                Same format as os.chmod

            timeout_seconds : `int`
                Maximum allowed amount of time for the operation.

        Returns
        -------
            `None` if operation succeeded.

        """

        raise NotImplementedError("The fileutils module {} "
            "does not implement chmod.".format(self.__module__))


    def deletefile(self, target, timeout_seconds, *args, **kwargs):
        """ Delete a file

        Parameters
        ----------
            target : `str`
                The URL of the file to be deleted.

            timeout_seconds : `int`
                Maximum allowed amount of time for the operation.

        """

        raise NotImplementedError("The fileutils module {} "
            "does not implement deletefile.".format(self.__module__))


    def renamefile(self, source, destination,
            timeout_seconds, *args, **kwargs):
        """ Rename a file

        Parameters
        ----------
            source : `str`
                The URL of the file to be renamed.

            destination : `str`
                The URL of the new file name.

            timeout_seconds : `int`
                Maximum allowed amount of time for the operation.

        """

        raise NotImplementedError("The fileutils module {} "
            "does not implement renamefile.".format(self.__module__))
