############################################################
# -*- coding: utf-8 -*-
#
# MOUNTCONTROL
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
############################################################
# standard libraries
import logging
# external packages
# local imports
from mountcontrol.connection import Connection
from mountcontrol.convert import valueToInt


class Firmware(object):
    """
    The class Firmware inherits all information and handling of firmware
    attributes of the connected mount and provides the abstracted interface
    to a 10 micron mount.

        >>> fw = Firmware(
        >>>                 host=host
        >>>              )
    """

    __all__ = ['Firmware',
               'productName',
               'numberString',
               'hwVersion',
               'fwtime',
               'fwdate',
               'checkNewer'
               'number',
               'pollSetting',
               ]
    version = '0.5'
    logger = logging.getLogger(__name__)

    # 10 microns have 3492 as default port
    DEFAULT_PORT = 3492

    def __init__(self,
                 host=None,
                 ):

        self.host = host
        self._productName = None
        self._numberString = None
        self._hwVersion = None
        self._fwdate = None
        self._fwtime = None

    @property
    def host(self):
        return self._host

    def checkFormat(self, value):
        # checking format
        if not value:
            self.logger.error('Wrong host value: {0}'.format(value))
            return None
        if not isinstance(value, (tuple, str)):
            self.logger.error('Wrong host value: {0}'.format(value))
            return None
        # now we got the right format
        if isinstance(value, str):
            value = (value, self.DEFAULT_PORT)
        return value

    @host.setter
    def host(self, value):
        value = self.checkFormat(value)
        self._host = value

    @property
    def productName(self):
        return self._productName

    @productName.setter
    def productName(self, value):
        self._productName = value

    @property
    def numberString(self):
        return self._numberString

    @numberString.setter
    def numberString(self, value):
        if not isinstance(value, str):
            self._numberString = None
            return
        if not value.count('.') > 0:
            self._numberString = None
            return
        if not all(valueToInt(x) for x in value.split('.')):
            self._numberString = None
            return
        self._numberString = value

    @property
    def hwVersion(self):
        return self._hwVersion

    @hwVersion.setter
    def hwVersion(self, value):
        self._hwVersion = value

    @property
    def fwdate(self):
        return self._fwdate

    @fwdate.setter
    def fwdate(self, value):
        self._fwdate = value

    @property
    def fwtime(self):
        return self._fwtime

    @fwtime.setter
    def fwtime(self, value):
        self._fwtime = value

    def number(self):
        if not self._numberString:
            return None
        parts = self._numberString.split('.')
        try:
            if len(parts) == 3:
                value = int(parts[0]) * 10000 + int(parts[1]) * 100 + int(parts[2])
            elif len(parts) == 2:
                value = int(parts[0]) * 10000 + int(parts[1]) * 100
            else:
                value = None
        except Exception as e:
            self.logger.error('error: {0}, malformed value: {1}'.format(e, parts))
            return None
        else:
            return value

    def checkNewer(self, compare):
        """
        Checks if the provided FW number is newer than the one of the mount

        :param compare:     fw number to test as int
        :return:            True if newer / False
        """

        value = self.number()
        if value:
            return compare > value
        else:
            return None

    def _parse(self, response, numberOfChunks):
        """
        Parsing the polling slow command.

        :param response:        data load from mount
               numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks:
            self.logger.error('wrong number of chunks')
            return False
        self.fwdate = response[0]
        self.numberString = response[1]
        self.productName = response[2]
        self.fwtime = response[3]
        self.hwVersion = response[4]
        return True

    def poll(self):
        """
        Sending the polling slow command. As the mount need polling the data, I send
        a set of commands to get the data back to be able to process and store it.

        :return: success:   True if ok, False if not
        """

        conn = Connection(self.host)
        commandString = ':U2#:GVD#:GVN#:GVP#:GVT#:GVZ#'
        suc, response, chunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self._parse(response, chunks)
        return suc
