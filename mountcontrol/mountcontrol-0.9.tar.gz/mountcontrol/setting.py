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
from mountcontrol.convert import valueToFloat
from mountcontrol.convert import valueToInt


class Setting(object):
    """
    The class Setting inherits all information and handling of settings
    attributes of the connected mount and provides the abstracted interface
    to a 10 micron mount.

        >>> setting = Setting(
        >>>                     host=host,
        >>>                   )

    """

    # noinspection PyUnresolvedReferences
    __all__ = ['Setting',
               'checkFormatMAC',
               'slewRate',
               'timeToFlip',
               'timeToMeridian',
               'meridianLimitTrack',
               'meridianLimitSlew',
               'refractionTemp',
               'refractionPress',
               'trackingRate',
               'checkRateLunar',
               'checkRateSidereal',
               'checkRateSolar',
               'telescopeTempDEC',
               'statusRefraction',
               'statusUnattendedFlip',
               'statusDualTracking',
               'currentHorizonLimitHigh',
               'currentHorizonLimitLow',
               'UTCValid',
               'UTCExpire',
               'pollSetting',
               ]
    version = '0.7'
    logger = logging.getLogger(__name__)

    # 10 microns have 3492 as default port
    DEFAULT_PORT = 3492

    def __init__(self,
                 host=None,
                 ):

        self.host = host
        self._slewRate = None
        self._timeToFlip = None
        self._meridianLimitTrack = None
        self._meridianLimitSlew = None
        self._refractionTemp = None
        self._refractionPress = None
        self._trackingRate = None
        self._telescopeTempDEC = None
        self._statusRefraction = None
        self._statusUnattendedFlip = None
        self._statusDualTracking = None
        self._horizonLimitHigh = None
        self._horizonLimitLow = None
        self._UTCValid = None
        self._UTCExpire = None
        self._typeConnection = None
        self._gpsSynced = None
        self._addressLanMAC = None
        self._addressWirelessMAC = None

    @property
    def host(self):
        return self._host

    def checkFormat(self, value):
        # checking format
        if not value:
            self.logger.error('wrong host value: {0}'.format(value))
            return None
        if not isinstance(value, (tuple, str)):
            self.logger.error('wrong host value: {0}'.format(value))
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
    def slewRate(self):
        return self._slewRate

    @slewRate.setter
    def slewRate(self, value):
        self._slewRate = valueToFloat(value)

    @property
    def timeToFlip(self):
        return self._timeToFlip

    @timeToFlip.setter
    def timeToFlip(self, value):
        self._timeToFlip = valueToFloat(value)

    @property
    def meridianLimitTrack(self):
        return self._meridianLimitTrack

    @meridianLimitTrack.setter
    def meridianLimitTrack(self, value):
        self._meridianLimitTrack = valueToFloat(value)

    @property
    def meridianLimitSlew(self):
        return self._meridianLimitSlew

    @meridianLimitSlew.setter
    def meridianLimitSlew(self, value):
        self._meridianLimitSlew = valueToFloat(value)

    def timeToMeridian(self):
        if self._timeToFlip and self._meridianLimitTrack:
            return int(self._timeToFlip - self._meridianLimitTrack * 4)
        else:
            return None

    @property
    def refractionTemp(self):
        return self._refractionTemp

    @refractionTemp.setter
    def refractionTemp(self, value):
        self._refractionTemp = valueToFloat(value)

    @property
    def refractionPress(self):
        return self._refractionPress

    @refractionPress.setter
    def refractionPress(self, value):
        self._refractionPress = valueToFloat(value)

    @property
    def trackingRate(self):
        return self._trackingRate

    @trackingRate.setter
    def trackingRate(self, value):
        self._trackingRate = valueToFloat(value)

    def checkRateLunar(self):
        if self._trackingRate == 62.4:
            return True
        else:
            return False

    def checkRateSidereal(self):
        if self._trackingRate == 60.2:
            return True
        else:
            return False

    def checkRateSolar(self):
        if self._trackingRate == 60.3:
            return True
        else:
            return False

    @property
    def telescopeTempDEC(self):
        return self._telescopeTempDEC

    @telescopeTempDEC.setter
    def telescopeTempDEC(self, value):
        self._telescopeTempDEC = valueToFloat(value)

    @property
    def statusRefraction(self):
        return self._statusRefraction

    @statusRefraction.setter
    def statusRefraction(self, value):
        self._statusRefraction = bool(value)

    @property
    def statusUnattendedFlip(self):
        return self._statusUnattendedFlip

    @statusUnattendedFlip.setter
    def statusUnattendedFlip(self, value):
        self._statusUnattendedFlip = bool(value)

    @property
    def statusDualTracking(self):
        return self._statusDualTracking

    @statusDualTracking.setter
    def statusDualTracking(self, value):
        self._statusDualTracking = bool(value)

    @property
    def horizonLimitHigh(self):
        return self._horizonLimitHigh

    @horizonLimitHigh.setter
    def horizonLimitHigh(self, value):
        self._horizonLimitHigh = valueToFloat(value)

    @property
    def horizonLimitLow(self):
        return self._horizonLimitLow

    @horizonLimitLow.setter
    def horizonLimitLow(self, value):
        self._horizonLimitLow = valueToFloat(value)

    @property
    def UTCValid(self):
        return self._UTCValid

    @UTCValid.setter
    def UTCValid(self, value):
        self._UTCValid = bool(value)

    @property
    def UTCExpire(self):
        return self._UTCExpire

    @UTCExpire.setter
    def UTCExpire(self, value):
        if isinstance(value, str):
            self._UTCExpire = value
        else:
            self._UTCExpire = None

    @property
    def typeConnection(self):
        return self._typeConnection

    @typeConnection.setter
    def typeConnection(self, value):
        value = valueToInt(value)
        if not 0 < value < 5:
            value = None
        self._typeConnection = value

    @property
    def gpsSynced(self):
        return self._gpsSynced

    @gpsSynced.setter
    def gpsSynced(self, value):
        self._gpsSynced = bool(value)

    @property
    def addressLanMAC(self):
        return self._addressLanMAC

    @addressLanMAC.setter
    def addressLanMAC(self, value):
        self._addressLanMAC = self.checkFormatMAC(value)

    @property
    def addressWirelessMAC(self):
        return self._addressWirelessMAC

    @addressWirelessMAC.setter
    def addressWirelessMAC(self, value):
        self._addressWirelessMAC = self.checkFormatMAC(value)

    def checkFormatMAC(self, value):
        """
        checkFormatMAC makes some checks to ensure that the format of the string is ok for
        WOL package.

        :param      value: string with mac address
        :return:    checked string in upper cases
        """

        if not value:
            self.logger.error('wrong MAC value: {0}'.format(value))
            return None
        if not isinstance(value, str):
            self.logger.error('wrong MAC value: {0}'.format(value))
            return None
        value = value.upper()
        value = value.replace('.', ':')
        value = value.split(':')
        if len(value) != 6:
            self.logger.error('wrong MAC value: {0}'.format(value))
            return None
        for chunk in value:
            if len(chunk) != 2:
                self.logger.error('wrong MAC value: {0}'.format(value))
                return None
            for char in chunk:
                if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                                'A', 'B', 'C', 'D', 'E', 'F']:
                    self.logger.error('wrong MAC value: {0}'.format(value))
                    return None
        # now we build the right format
        value = '{0:2s}:{1:2s}:{2:2s}:{3:2s}:{4:2s}:{5:2s}'.format(*value)
        return value

    def _parseSetting(self, response, numberOfChunks):
        """
        Parsing the polling med command.

        :param response:        data load from mount
               numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks:
            self.logger.error('wrong number of chunks')
            return False
        self.slewRate = response[0]
        self.timeToFlip = response[1]
        self.meridianLimitTrack = response[2]
        self.meridianLimitSlew = response[3]
        self.refractionTemp = response[4]
        self.refractionPress = response[5]
        self.trackingRate = response[6]
        self.telescopeTempDEC = response[7]
        self.statusRefraction = (response[8][0] == '1')
        self.statusUnattendedFlip = (response[8][1] == '1')
        self.statusDualTracking = (response[8][2] == '1')
        self.horizonLimitHigh = response[8][3:6]
        self.horizonLimitLow = response[9][0:3]
        valid, expirationDate = response[10].split(',')
        self.UTCValid = (valid == 'V')
        self.UTCExpire = expirationDate
        self.typeConnection = response[11]
        self.gpsSynced = (response[12] == '1')
        self.addressLanMAC = response[13]
        # self.addressWirelessMAC = response[14]
        return True

    def pollSetting(self):
        """
        Sending the polling med command. As the mount need polling the data, I send
        a set of commands to get the data back to be able to process and store it.

        :return:    success:    True if ok, False if not
        """

        conn = Connection(self.host)
        cs1 = ':GMs#:Gmte#:Glmt#:Glms#:GRTMP#:GRPRS#:GT#:GTMP1#:GREF#:Guaf#'
        cs2 = ':Gdat#:Gh#:Go#:GDUTV#:GINQ#:gtg#:GMAC#'
        commandString = cs1 + cs2
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self._parseSetting(response, numberOfChunks)
        return suc
