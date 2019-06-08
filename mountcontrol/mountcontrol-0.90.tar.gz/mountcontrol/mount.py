############################################################
# -*- coding: utf-8 -*-
#
# MOUNTCONTROL
#
# Python-based Tool for interaction with the 10micron mounts
#
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
import wakeonlan
# local imports
from mountcontrol.firmware import Firmware
from mountcontrol.setting import Setting
from mountcontrol.obsSite import ObsSite
from mountcontrol.model import Model


__all__ = ['Mount',
           ]


class Mount(object):
    """
    The Mount class is the main interface for interacting with the mount computer.
    The user could:
        setup / change the interface to the mount
        start / stop cyclic tasks to poll data from mount
        send and get data from mount
        has signals for interfacing to external GUI's for data updates

        >>> settings = Mount(
        >>>                     host=host,
        >>>                     MAC=MAC,
        >>>                     pathToData=pathToData,
        >>>                     expire=expire,
        >>>                     verbose=verbose,
        >>>                 )

    """

    __all__ = ['Mount',
               ]
    version = '0.90'
    logger = logging.getLogger(__name__)

    # 10 microns have 3492 as default port
    DEFAULT_PORT = 3492

    def __init__(self,
                 host=None,
                 MAC=None,
                 pathToData=None,
                 expire=None,
                 verbose=None,
                 ):

        self._host = self.checkFormatHost(host)
        self._MAC = MAC
        self.pathToData = pathToData
        self.expire = expire
        self.verbose = verbose
        # signal handling
        self.mountUp = False

        # instantiating the data classes
        self.fw = Firmware(self.host)
        self.sett = Setting(self.host)
        self.model = Model(self.host)
        self.obsSite = ObsSite(self.host,
                               pathToData=self.pathToData,
                               expire=self.expire,
                               verbose=self.verbose,
                               )

    def checkFormatHost(self, value):
        """
        checkFormatHost ensures that the host ip and port is in correct format to enable
        socket connection later on. if no port is given, the default port for the mount
        will be added automatically

        :param      value: host value
        :return:    host value as tuple including port
        """

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

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        value = self.checkFormatHost(value)
        self._host = value
        # now setting to subclasses
        self.fw.host = value
        self.sett.host = value
        self.model.host = value
        self.obsSite.host = value

    @property
    def MAC(self):
        return self._MAC

    @MAC.setter
    def MAC(self, value):
        value = self.sett.checkFormatMAC(value)
        self._MAC = value

    def resetData(self):
        """
        resetData deletes all data already stored in classes just by redefining the
        classes. it send as well a signal, when the data is cleared.

        :return: nothing
        """
        del self.fw
        del self.sett
        del self.model
        del self.obsSite

        self.fw = Firmware(self.host)
        self.sett = Setting(self.host)
        self.model = Model(self.host)
        self.obsSite = ObsSite(self.host,
                               pathToData=self.pathToData,
                               expire=self.expire,
                               verbose=self.verbose,
                               )

    def bootMount(self):
        """
        bootMount tries to boot the mount via WOL with a given MAC address

        :return:    True if success
        """

        if self.MAC is not None:
            wakeonlan.send_magic_packet(self.MAC)
            return True
        else:
            return False

    def shutdownMount(self):
        """

        :return:
        """

        self.mountUp = False
        suc = self.app.mount.obsSite.shutdown()
        return suc
