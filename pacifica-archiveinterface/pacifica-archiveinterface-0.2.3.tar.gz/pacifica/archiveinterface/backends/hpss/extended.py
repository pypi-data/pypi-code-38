#!/usr/bin/python
# -*- coding: utf-8 -*-
"""HPSS Extended File Module.

Module that holds the class to the interface for the hpss c extensions.
"""
from os.path import dirname
# c extension import not picked up by pylint, so disabling
# pylint: disable=import-error
# pylint: disable=no-name-in-module
try:
    from ..hpss import _hpssExtensions
except ImportError:
    pass
# pylint: enable=import-error
# pylint: enable=no-name-in-module
from .status import HpssStatus
from ...exception import ArchiveInterfaceError


class HpssExtended(object):
    """Provide the interface for the hpss ctypes."""

    def __init__(self, filepath, accept_latency=5):
        """Constructor for the HPSS Extended File type."""
        self._accept_latency = accept_latency
        self._latency = None
        self._filepath = filepath

    def ping_core(self, sitename):
        """Ping the Core server to see if its still active."""
        # Define acceptable latency in seconds
        acceptable_latency = self._accept_latency
        latency_tuple = _hpssExtensions.hpss_ping_core(sitename)
        # Get the latency
        latency = self.parse_latency(latency_tuple)

        if latency > acceptable_latency:
            err_str = 'The archive core server is slow to respond'\
                      ' Latency is: ' + str(latency) + ' second(s)'
            raise ArchiveInterfaceError(err_str)

    def parse_latency(self, latency_tuple):
        """Parse the latency tuple.

        Parse the tuple returned by the c extension into
        the correct latency.
        """
        # Get the latency
        # LatencyTuple[0] = time the core server responded
        # LatencyTuple[1] = microseconds relative to core server
        # LatencyTuple[2] = time before pinging core server
        # LatencyTuple[3] = microseconds relative before ping

        lat_seconds = float(latency_tuple[0])
        lat_microseconds = (float(latency_tuple[1]) / 1000000)
        response_time = lat_seconds + lat_microseconds
        before_ping_seconds = float(latency_tuple[2])
        before_ping_microseconds = (float(latency_tuple[3]) / 1000000)
        before_ping_time = before_ping_seconds + before_ping_microseconds
        latency = response_time - before_ping_time
        self._latency = latency
        return latency

    def status(self):
        """Get the status of a file.

        If it is on tape or disk
        Found the documentation for this in the hpss programmers reference
        section 2.3.6.2.8 "Get Extanded Attributes".
        """
        mtime = ''
        ctime = ''
        bytes_per_level = ''
        filesize = ''
        try:
            mtime = _hpssExtensions.hpss_mtime(self._filepath)
            ctime = _hpssExtensions.hpss_ctime(self._filepath)
            bytes_per_level = _hpssExtensions.hpss_status(self._filepath)
            filesize = _hpssExtensions.hpss_filesize(self._filepath)
            status = HpssStatus(mtime, ctime, bytes_per_level, filesize)
            status.set_filepath(self._filepath)
        except Exception as ex:
            # Push the excpetion up the chain to the response
            err_str = 'Error using c extensions for hpss status'\
                      ' exception: ' + str(ex)
            raise ArchiveInterfaceError(err_str)
        return status

    def stage(self):
        """Stage an hpss file.

        Do this to move the file to disk
        doesnt need to return anything.  will throw
        exception on error however.
        """
        try:
            _hpssExtensions.hpss_stage(self._filepath)

        except Exception as ex:
            # Push the excpetion up the chain to the response
            err_str = 'Error using c extension for hpss stage'\
                      ' exception: ' + str(ex)
            raise ArchiveInterfaceError(err_str)

    def set_mod_time(self, mod_time):
        """Use extensions to set the mod time on an hpss file."""
        try:
            _hpssExtensions.hpss_utime(self._filepath, int(mod_time))

        except Exception as ex:
            # Push the excpetion up the chain to the response
            err_str = 'Error using c extension for hpss utime'\
                      ' exception: ' + str(ex)
            raise ArchiveInterfaceError(err_str)

    def makedirs(self):
        """Recursively make the directories for the filepath."""
        try:
            _hpssExtensions.hpss_makedirs(dirname(self._filepath))
        except Exception as ex:
            # Push the excpetion up the chain to the response
            err_str = 'Error using c extension for hpss makedirs'\
                      ' exception: ' + str(ex)
            raise ArchiveInterfaceError(err_str)
