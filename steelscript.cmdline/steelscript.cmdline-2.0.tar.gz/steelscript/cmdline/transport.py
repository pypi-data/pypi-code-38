# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import abc


class Transport(object, metaclass=abc.ABCMeta):
    """
    Abstract class to define common interfaces for a transport.

    A transport is used by Cli/Shell object to handle connection setup.
    """

    @abc.abstractmethod
    def connect(self):
        """ Abstract method to start a connection """
        pass

    @abc.abstractmethod
    def disconnect(self):
        """ Abstract method to tear down current connection """
        pass

    @abc.abstractmethod
    def is_connected(self):
        """
        Check whether a connection is established or not.

        :return: True if it is connected; returns False otherwise.
        """
        return
