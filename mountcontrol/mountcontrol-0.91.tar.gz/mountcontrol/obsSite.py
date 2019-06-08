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
import skyfield.api as api
import skyfield.starlib as starlib
# local imports
from .connection import Connection
from .convert import stringToDegree
from .convert import stringToAngle
from .convert import valueToFloat
from .convert import valueToInt
from .convert import valueToAngle


class ObsSite(object):
    """
    The class Site inherits all information and handling of site data
    attributes of the connected mount and provides the abstracted interface
    to a 10 micron mount. as the mount's time base is julian date, we use this
    value as time base as well. for that reason we should remind how the mount
    calculates the julian date. it is derived from utc. to basically on the timeJD
    for skyfield we calculate julian date from ut1 based on julian date from mount
    based on utc and the value delta utc, ut1 also given from the mount.

        >>> site = ObsSite(
        >>>             host=host,
        >>>             pathToData=pathToData,
        >>>             verbose=verbose,
        >>>             expire=expire,
        >>>             location=(0, 0, 0),
        >>>             )

    The Site class needs as parameter a ts object from skyfield.api to
    be able to make all the necessary calculations about time from and to mount
    """

    __all__ = ['ObsSite',
               'location',
               'timeJD',
               'timeSidereal',
               'raJNow',
               'decJNow',
               'pierside',
               'Alt',
               'Az',
               'status',
               'statusText',
               'statusSlew',
               'pollSetting',
               'pollPointing',
               'slewAltAz',
               'slewRaDec',
               'shutdown',
               'setLocation',
               'setLatitude',
               'setLongitude',
               'setElevation',
               'setSlewRate',
               'setRefractionParam',
               'setRefractionTemp',
               'setRefractionPress',
               'setRefraction',
               'setUnattendedFlip',
               'setDualAxisTracking',
               'setMeridianLimitTrack',
               'setMeridianLimitSlew',
               'setHorizonLimitHigh',
               'setHorizonLimitLow',
               'startTracking',
               'stopTracking',
               'setLunarTracking',
               'setSiderealTracking',
               'setSolarTracking',
               'park',
               'unpark',
               'stop',
               'flip',
               ]
    version = '0.6'
    logger = logging.getLogger(__name__)

    # 10 microns have 3492 as default port
    DEFAULT_PORT = 3492

    STAT = {
        '0': 'Tracking',
        '1': 'Stopped after STOP',
        '2': 'Slewing to park position',
        '3': 'Unparking',
        '4': 'Slewing to home position',
        '5': 'Parked',
        '6': 'Slewing or going to stop',
        '7': 'Tracking Off no move',
        '8': 'Motor low temperature',
        '9': 'Tracking outside limits',
        '10': 'Following Satellite',
        '11': 'User OK Needed',
        '98': 'Unknown Status',
        '99': 'Error',
    }

    def __init__(self,
                 host=None,
                 pathToData=None,
                 verbose=None,
                 expire=None,
                 location=None,
                 ):

        self.host = host
        self._expire = expire
        self.pathToData = pathToData
        self.verbose = verbose
        self._location = location
        self.ts = None
        self._timeJD = None
        self._utc_ut1 = None
        self._timeSidereal = None
        self._raJNow = None
        self._decJNow = None
        self._pierside = None
        self._Alt = None
        self._Az = None
        self._status = None
        self._statusSlew = None

        self.loadData()

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

    def loadData(self):
        # generate timescale data
        if self.pathToData:
            # normally there should be a path given
            load = api.Loader(self.pathToData,
                              verbose=self.verbose,
                              expire=self.expire,
                              )
            self.ts = load.timescale()
        else:
            self.ts = api.load.timescale()
            self.logger.info('No path for timescale given, using default')

    @property
    def expire(self):
        return self._expire

    @expire.setter
    def expire(self, value):
        self._expire = bool(value)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if isinstance(value, api.Topos):
            self._location = value
            return
        if not isinstance(value, (list, tuple)):
            self._location = None
            self.logger.error('Malformed value: {0}'.format(value))
            return
        if len(value) != 3:
            self._location = None
            self.logger.error('Malformed value: {0}'.format(value))
            return
        lat, lon, elev = value
        lat = stringToAngle(lat, preference='degrees')
        lon = stringToAngle(lon, preference='degrees')
        elev = valueToFloat(elev)
        if not lat or not lon or not elev:
            self._location = None
            self.logger.error('Malformed value: {0}'.format(value))
            return
        self._location = api.Topos(longitude=lon,
                                   latitude=lat,
                                   elevation_m=elev)

    @property
    def timeJD(self):
        if self._timeJD is None:
            return self.ts.now()
        else:
            return self._timeJD

    @timeJD.setter
    def timeJD(self, value):
        value = valueToFloat(value)
        if value and self._utc_ut1 is not None:
            self._timeJD = self.ts.ut1_jd(value - self._utc_ut1)
        else:
            self._timeJD = None

    @property
    def utc_ut1(self):
        return self._utc_ut1

    @utc_ut1.setter
    def utc_ut1(self, value):
        value = valueToFloat(value)
        if value is not None:
            # delta is stored based on day, because of calculation of julian date
            self._utc_ut1 = value / 86400
        else:
            self._utc_ut1 = None

    @property
    def timeSidereal(self):
        return self._timeSidereal

    @timeSidereal.setter
    def timeSidereal(self, value):
        # testing the format
        if not isinstance(value, str):
            self._timeSidereal = None
            return
        if stringToDegree(value) is None:
            self._timeSidereal = None
        else:
            self._timeSidereal = value

    @property
    def raJNow(self):
        return self._raJNow

    @raJNow.setter
    def raJNow(self, value):
        if isinstance(value, api.Angle):
            self._raJNow = value
            return
        self._raJNow = valueToAngle(value, preference='hours')

    @property
    def decJNow(self):
        return self._decJNow

    @decJNow.setter
    def decJNow(self, value):
        if isinstance(value, api.Angle):
            self._decJNow = value
            return
        self._decJNow = valueToAngle(value, preference='degrees')

    @property
    def pierside(self):
        return self._pierside

    @pierside.setter
    def pierside(self, value):
        if value in ['E', 'W', 'e', 'w']:
            value = value.capitalize()
            self._pierside = value
        else:
            self._pierside = None
            self.logger.error('Malformed value: {0}'.format(value))

    @property
    def Alt(self):
        return self._Alt

    @Alt.setter
    def Alt(self, value):
        if isinstance(value, api.Angle):
            self._Alt = value
            return
        self._Alt = valueToAngle(value, preference='degrees')

    @property
    def Az(self):
        return self._Az

    @Az.setter
    def Az(self, value):
        if isinstance(value, api.Angle):
            self._Az = value
            return
        self._Az = valueToAngle(value, preference='degrees')

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = valueToInt(value)
        if self._status not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 98, 99]:
            self._status = None

    def statusText(self):
        if self._status is None:
            return None
        reference = '{0:d}'.format(self._status)
        if reference in self.STAT:
            return self.STAT[reference]
        else:
            return None

    @property
    def statusSlew(self):
        return self._statusSlew

    @statusSlew.setter
    def statusSlew(self, value):
        self._statusSlew = bool(value)

    def _parseLocation(self, response, numberOfChunks):
        """
        Parsing the polling slow command.

        :param response:        data load from mount
               numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks:
            self.logger.error('Wrong number of chunks')
            return False
        elev = response[0]
        # due to compatibility to LX200 protocol east is negative, so we change that
        # in class we would like to keep the correct sign for east is positive
        lon = None
        if '-' in response[1]:
            lon = response[1].replace('-', '+')
        if '+' in response[1]:
            lon = response[1].replace('+', '-')
        lat = response[2]
        # storing it to the skyfield Topos unit
        self.location = [lat, lon, elev]
        return True

    def getLocation(self):
        """
        Sending the polling command. As the mount need polling the data, I send
        a set of commands to get the data back to be able to process and store it.

        :return: success:   True if ok, False if not
        """

        conn = Connection(self.host)
        commandString = ':U2#:Gev#:Gg#:Gt#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self._parseLocation(response, numberOfChunks)
        return suc

    def _parsePointing(self, response, numberOfChunks):
        """
        Parsing the polling fast command.

        :param response:        data load from mount
               numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks:
            self.logger.error('Wrong number of chunks')
            return False
        self.timeSidereal = response[0]
        # remove the leap seconds flag if present
        self.utc_ut1 = response[1].replace('L', '')
        responseSplit = response[2].split(',')
        self.raJNow = responseSplit[0]
        self.decJNow = responseSplit[1]
        self.pierside = responseSplit[2]
        self.Az = responseSplit[3]
        self.Alt = responseSplit[4]
        self.timeJD = responseSplit[5]
        self.status = responseSplit[6]
        self.statusSlew = (responseSplit[7] == '1')
        return True

    def pollPointing(self):
        """
        Sending the polling fast command. As the mount need polling the data, I send
        a set of commands to get the data back to be able to process and store it.

        :return: success:   True if ok, False if not
        """

        conn = Connection(self.host)
        commandString = ':U2#:GS#:GDUT#:Ginfo#:'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self._parsePointing(response, numberOfChunks)
        return suc

    def _slewingCommand(self, slewType='normal'):
        """
        _slewingCommand issues the final slew command to the mount after the target
        coordinates were set. before issuing the slewing command it automatically unpark
        the mount as well.

        the slew commands are:
            :MS#  :MA#  :MSap#  :MSao#

        and return:
            0 no error
                if the target is below the lower limit: the string
            “1Object Below Horizon #”
                if the target is above the high limit: the string
            “2Object Below Higher #”
                if the slew cannot be performed due to another cause: the string
            “3Cannot Perform Slew #”
                if the mount is parked: the string
            “4Mount Parked #”
                if the mount is restricted to one side of the meridian and the object
                is on the other side: the string
            “5Object on the other side #”

            the types of slew is:
        - 'normal'      slew to coordinates and tracking on
        - 'notrack':    slew to coordinates and tracking off
        - 'polar':      slew to coordinates and miss for polar alignment
        - 'ortho':      slew to coordinates and miss for orthogonal alignment


        :param slewType:
        :return:
        """

        slewTypes = {
            'normal': ':MS#',
            'notrack': ':MA#',
            'polar': ':MSap#',
            'ortho': ':MSao#',
        }

        if slewType not in slewTypes:
            return False

        conn = Connection(self.host)

        # start slewing with first unpark and slew command
        commandString = ':PO#' + slewTypes[slewType]
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0].count('#') > 0:
            self.logger.error('Slew could not be done, {0}'.format(response))
            return False
        return True

    def slewAltAz(self,
                  alt=None, az=None,
                  alt_degrees=None, az_degrees=None,
                  slewType='normal'):
        """
        Slew AltAz unpark the mount sets the targets for alt and az and then
        issue the slew command.

        the unpark command is:
            :PO#
        and returns nothing

        setting alt target is the following:
            :SzDDD*MM# or :SzDDD*MM:SS# or :SzDDD*MM:SS.S#, we use the last one
            :SzDDD*MM:SS.S#

        setting az target is the following:
            :SasDD*MM# or :SasDD*MM:SS# or :SasDD*MM:SS.S#, we use the last one
            :SasDD*MM:SS.S#

        the slew command moves the mount and keeps tracking at the end of the move.
        in the command protocol it is written, that the targets should be ra / dec,
        but it works for targets defined with alt / az commands

        :param alt:     altitude in type Angle
        :param az:      azimuth in type Angle
        :param alt_degrees:     altitude in degrees float
        :param az_degrees:      azimuth in degrees float
        :param slewType:  command type for slewing
        :return:        success
        """

        hasAngles = isinstance(alt, api.Angle) and isinstance(az, api.Angle)
        hasFloats = isinstance(alt_degrees, (float, int)) and isinstance(az_degrees, (float, int))
        if hasAngles:
            pass
        elif hasFloats:
            alt = api.Angle(degrees=alt_degrees)
            az = api.Angle(degrees=az_degrees)
        else:
            return False
        if alt.preference != 'degrees':
            return False
        if az.preference != 'degrees':
            return False

        conn = Connection(self.host)
        # conversion, as we only have positive alt, we set the '+' as standard.
        altFormat = ':Sa{sign}{0:02.0f}*{1:02.0f}:{2:04.1f}#'
        setAlt = altFormat.format(*alt.signed_dms()[1:4],
                                  sign='+' if alt.degrees > 0 else '-')
        azFormat = ':Sz{0:03.0f}*{1:02.0f}:{2:04.1f}#'
        setAz = azFormat.format(*az.dms())
        commandString = setAlt + setAz
        # set coordinates
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0].count('0') > 0:
            self.logger.error('Coordinates could not be set, {0}'.format(response))
            return False
        suc = self._slewingCommand(slewType=slewType)
        return suc

    def slewRaDec(self,
                  ra=None, dec=None,
                  ra_hours=None, dec_degrees=None,
                  target=None, slewType='normal'):
        """
        Slew RaDec unpark the mount sets the targets for ra and dec and then
        issue the slew command.

        the unpark command is:
            :PO#
        and returns nothing

        setting ra target is the following:
            :SrHH:MM.T# or :SrHH:MM:SS# or :SrHH:MM:SS.S# or :SrHH:MM:SS.SS#
                , we use the last one
            :SrHH:MM:SS.SS#

        setting dec target is the following:
            :SdsDD*MM# or :SdsDD*MM:SS# or :Sd sDD*MM:SS.S#, we use the last one
            :SdsDD*MM:SS.S#

        the slew command moves the mount and keeps tracking at the end of the move.
        in the command protocol it is written, that the targets should be ra / dec,
        but it works for targets defined with alt / az commands

        :param ra:     right ascension in type Angle
        :param dec:    declination in type Angle preference 'hours'
        :param ra_hours: right ascension in float hours
        :param dec_degrees: declination in float degrees
        :param target:  star in type skyfield.Star
        :param slewType:  command type for slewing
        :return:       success
        """

        hasTarget = isinstance(target, starlib.Star)
        hasAngles = isinstance(ra, api.Angle) and isinstance(dec, api.Angle)
        hasFloats = isinstance(ra_hours, (float, int)) and isinstance(dec_degrees, (float, int))
        if hasTarget:
            ra = target.ra
            dec = target.dec
        elif hasAngles:
            pass
        elif hasFloats:
            ra = api.Angle(hours=ra_hours, preference='hours')
            dec = api.Angle(degrees=dec_degrees)
        else:
            return False
        if ra.preference != 'hours':
            return False
        if dec.preference != 'degrees':
            return False

        conn = Connection(self.host)
        # conversion, we have to find out the sign
        raFormat = ':Sr{0:02.0f}:{1:02.0f}:{2:05.2f}#'
        setRa = raFormat.format(*ra.hms())
        decFormat = ':Sd{sign}{0:02.0f}*{1:02.0f}:{2:04.1f}#'
        setDec = decFormat.format(*dec.signed_dms()[1:4],
                                  sign='+' if dec.degrees > 0 else '-')
        commandString = setRa + setDec
        # set coordinates
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0].count('0') > 0:
            self.logger.error('Coordinates could not be set, {0}'.format(response))
            return False
        suc = self._slewingCommand(slewType=slewType)
        return suc

    def shutdown(self):
        """
        shutdown send the shutdown command to the mount. if succeeded it takes about 20
        seconds before you could switch off the power supply. please check red LED at mount

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':shutdown#')
        if not suc:
            return False
        if response[0] == '0':
            return False
        return True

    def setLocation(self, obs):
        """
        set SiteCoordinates sets the value in the mount to the given parameters.
        the longitude will be set for east negative, because that's the definition
        from the LX200 protocol, which the 10micron mount supports. internally we use
        the standard east positive.

        the site parameters could be set be the following commands:

        longitude (we will use the last one with the highest precision):

            :SgsDDD*MM# or :SgsDDD*MM:SS# or :SgsDDD*MM:SS.S#

            Set current site’s longitude to sDDD*MM (sign, degrees, arcminutes),
            sDDD*MM:SS (sign, degrees, arcminutes, arcseconds) or
            sDDD*MM:SS.S (sign, degrees, arcminutes, arcseconds and tenths of arcsecond).
            Note: East Longitudes are expressed as negative.
            Returns:
            0   invalid
            1   valid

        latitude (we will use the last one with the highest precision):

            :StsDD*MM# or :StsDD*MM:SS# or :StsDD*MM:SS.S#

            Sets the current site latitude to sDD*MM (sign, degrees, arcminutes),
            sDD*MM:SS (sign, degrees, arcminutes, arcseconds), or
            sDD*MM:SS.S (sign, degrees, arcminutes, arcseconds and tenths of arcsecond)

            Returns:
            0   invalid
            1   valid

        elevation:

            :SevsXXXX.X#

            Set current site’s elevation to sXXXX.X (sign, metres) in the
            range -1000.0 to 9999.9.
            Returns:
            0   invalid
            1   valid

        :param      obs:        skyfield.api.Topos of site
        :return:    success
        """

        if not isinstance(obs, api.Topos):
            return False

        conn = Connection(self.host)
        # conversion, we have to find out the sign
        lonFormat = ':Sg{sign}{0:03.0f}*{1:02.0f}:{2:04.1f}#'
        setLon = lonFormat.format(*obs.longitude.signed_dms()[1:4],
                                  sign='+' if obs.longitude.degrees < 0 else '-')

        latFormat = ':St{sign}{0:02.0f}*{1:02.0f}:{2:04.1f}#'
        setLat = latFormat.format(*obs.latitude.signed_dms()[1:4],
                                  sign='+' if obs.latitude.degrees > 0 else '-')

        setElev = ':Sev{sign}{0:06.1f}#'.format(obs.elevation.m,
                                                sign='+' if obs.elevation.m > 0 else '-')

        commandString = setLon + setLat + setElev
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if '0' in response[0]:
            return False
        return True

    def setLatitude(self, lat=None, lat_degrees=None):
        """
        setLatitude sets the value in the mount to the given parameters.
        the site parameters could be set be the following commands:
        latitude (we will use the last one with the highest precision):

            :StsDD*MM# or :StsDD*MM:SS# or :StsDD*MM:SS.S#

            Sets the current site latitude to sDD*MM (sign, degrees, arcminutes),
            sDD*MM:SS (sign, degrees, arcminutes, arcseconds), or
            sDD*MM:SS.S (sign, degrees, arcminutes, arcseconds and tenths of arcsecond)

            Returns:
            0   invalid
            1   valid

        :param      lat:  coordinates as Angle
        :param      lat_degrees:  coordinates as float
        :return:    success
        """

        hasAngle = isinstance(lat, api.Angle)
        hasFloat = isinstance(lat_degrees, (float, int))
        if hasAngle:
            pass
        elif hasFloat:
            lat = valueToAngle(lat_degrees, preference='degrees')
        else:
            return False

        conn = Connection(self.host)

        latFormat = ':St{sign}{0:02.0f}*{1:02.0f}:{2:04.1f}#'
        setLat = latFormat.format(*lat.signed_dms()[1:4],
                                  sign='+' if lat.degrees > 0 else '-')

        commandString = setLat
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if '0' in response[0]:
            return False
        return True

    def setLongitude(self, lon=None, lon_degrees=None):
        """
        setLongitude sets the value in the mount to the given parameters.
        the longitude will be set for east negative, because that's the definition
        from the LX200 protocol, which the 10micron mount supports. internally we use
        the standard east positive.

        the site parameters could be set be the following commands:
        longitude (we will use the last one with the highest precision):

            :SgsDDD*MM# or :SgsDDD*MM:SS# or :SgsDDD*MM:SS.S#

            Set current site’s longitude to sDDD*MM (sign, degrees, arcminutes),
            sDDD*MM:SS (sign, degrees, arcminutes, arcseconds) or
            sDDD*MM:SS.S (sign, degrees, arcminutes, arcseconds and tenths of arcsecond).
            Note: East Longitudes are expressed as negative.
            Returns:
            0   invalid
            1   valid

        :param      lon:  coordinates as Angle
        :param      lon_degrees:  coordinates as float
        :return:    success
        """

        hasAngle = isinstance(lon, api.Angle)
        hasFloat = isinstance(lon_degrees, (float, int))
        if hasAngle:
            pass
        elif hasFloat:
            lon = valueToAngle(lon_degrees, preference='degrees')
        else:
            return False

        conn = Connection(self.host)

        lonFormat = ':Sg{sign}{0:03.0f}*{1:02.0f}:{2:04.1f}#'
        setLon = lonFormat.format(*lon.signed_dms()[1:4],
                                  sign='+' if lon.degrees < 0 else '-')

        commandString = setLon
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if '0' in response[0]:
            return False
        return True

    def setElevation(self, elev):
        """
        setElevation sets the value in the mount to the given parameters.
        the site parameters could be set be the following commands:
        elevation:

            :SevsXXXX.X#

            Set current site’s elevation to sXXXX.X (sign, metres) in the
            range -1000.0 to 9999.9.
            Returns:
            0   invalid
            1   valid

        :param      elev:        string with elevation in meters
        :return:    success
        """

        if not isinstance(elev, (str, int, float)):
            return False
        elev = valueToFloat(elev)
        if elev is None:
            return False

        conn = Connection(self.host)

        setElev = ':Sev{sign}{0:06.1f}#'.format(abs(elev),
                                                sign='+' if elev > 0 else '-')

        commandString = setElev
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if '0' in response[0]:
            return False
        return True

    def setSlewRate(self, value):
        """
        setSlewRate sends the command for setting the max slew rate to the mount.

        :param value:   float for max slew rate in degrees per second
        :return:        success
        """

        if value is None:
            return False
        if not isinstance(value, (int, float)):
            return False
        if value < 2:
            return False
        elif value > 15:
            return False
        conn = Connection(self.host)
        commandString = ':Sw{0:02.0f}#'.format(value)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setRefractionParam(self, temperature=None, pressure=None):
        """
        setRefractionParam sends the command for setting the temperature and pressure
        to the mount. the limits are set to -40 to +75 for temp and 500 to 1300 hPa for
        pressure, but there is not real documented limit.

        :param          temperature:    float for temperature correction in Celsius
        :param          pressure:       float for pressure correction in hPa
        :return:        success
        """

        if temperature is None:
            return False
        if pressure is None:
            return False
        if temperature < -40:
            return False
        elif temperature > 75:
            return False
        if pressure < 500:
            return False
        elif pressure > 1300:
            return False
        conn = Connection(self.host)
        commandString = ':SRTMP{0:+06.1f}#:SRPRS{1:06.1f}#'.format(temperature, pressure)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '11':
            return False
        return True

    def setRefractionTemp(self, value):
        """
        setRefractionTemp sends the command for setting the temperature to the mount. the
        limit is set to -40 to +75, but there is not real documented limit.

        :param value:   float for temperature correction in Celsius
        :return:        success
        """

        if value is None:
            return False
        if value < -40:
            return False
        elif value > 75:
            return False
        conn = Connection(self.host)
        commandString = ':SRTMP{0:+06.1f}#'.format(value)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setRefractionPress(self, value):
        """
        setRefractionPress sends the command for setting the pressure to the mount. the
        limit is set from 500 to 1300 hPa. no limit give from the mount. limits here are
        relevant over 5000m height

        :param value:   float for pressure correction
        :return:        success
        """

        if value is None:
            return False
        if value < 500:
            return False
        elif value > 1300:
            return False
        conn = Connection(self.host)
        commandString = ':SRPRS{0:06.1f}#'.format(value)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setRefraction(self, status):
        """
        setRefraction sends the command to the mount.

        :param status:  bool for enable or disable refraction correction
        :return:        success
        """

        conn = Connection(self.host)
        commandString = ':SREF{0:1d}#'.format(1 if status else 0)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setUnattendedFlip(self, status):
        """
        setUnattendedFlip sends the  command to the mount. the command returns nothing.

        :param status:  bool for enable or disable unattended flip
        :return:        success
        """

        conn = Connection(self.host)
        commandString = ':Suaf{0:1d}#'.format(1 if status else 0)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        return True

    def setDualAxisTracking(self, status):
        """
        setDualAxisTracking sends the  command to the mount.

        :param status:  bool for enable or disable dual tracking
        :return:        success
        """

        conn = Connection(self.host)
        commandString = ':Sdat{0:1d}#'.format(1 if status else 0)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setMeridianLimitTrack(self, value):
        """
        setMeridianLimitTrack sends the command for setting flip limit to the mount.
        the limit is set from -20 to 20 degrees

        :param value:   float for degrees
        :return:        success
        """

        if value < -20:
            return False
        elif value > 20:
            return False
        conn = Connection(self.host)
        value = int(value)
        commandString = ':Slmt{0:02d}#'.format(value)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setMeridianLimitSlew(self, value):
        """
        setMeridianLimitSlew sends the command for setting flip limit to the mount.
        the limit is set to -20 to 20 degrees

        :param value:   float / int for degrees
        :return:        success
        """

        if value < -20:
            return False
        elif value > 20:
            return False
        conn = Connection(self.host)
        value = int(value)
        commandString = ':Slms{0:02d}#'.format(value)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setHorizonLimitHigh(self, value):
        """
        setHorizonLimitHigh sends the command for setting the limit to the mount.
        the limit is set from 0 to 90 degrees

        :param value:   float / int for degrees
        :return:        success
        """

        if value < 0:
            return False
        elif value > 90:
            return False
        conn = Connection(self.host)
        value = int(value)
        commandString = ':Sh+{0:02d}#'.format(value)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setHorizonLimitLow(self, value):
        """
        setHorizonLimitLow sends the command for setting the limit to the mount. the limit
        has to be between -5 and +45 degrees

        :param value:   float / int for degrees
        :return:        success
        """

        if value < -5:
            return False
        elif value > 45:
            return False
        conn = Connection(self.host)
        value = int(value)
        commandString = ':So{0:+02d}#'.format(value)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def startTracking(self):
        """
        startTracking sends the start command to the mount. the command returns nothing.
        it is necessary to make that direct to unpark first, than start tracking

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':PO#:AP#')
        if not suc:
            return False
        return True

    def stopTracking(self):
        """
        stopTracking sends the start command to the mount. the command returns nothing.

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':RT9#')
        if not suc:
            return False
        return True

    def setLunarTracking(self):
        """
        setLunar sends the command for lunar tracking speed to the mount. the command
        returns nothing.

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':RT0#')
        if not suc:
            return False
        return True

    def setSiderealTracking(self):
        """
        setLunar sends the command for sidereal tracking speed to the mount. the command
        returns nothing.

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':RT2#')
        if not suc:
            return False
        return True

    def setSolarTracking(self):
        """
        setLunar sends the command for solar tracking speed to the mount. the command
        returns nothing.

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':RT1#')
        if not suc:
            return False
        return True

    def park(self):
        """
        park sends the park command to the mount. the command returns nothing.

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':hP#')
        if not suc:
            return False
        return True

    def unpark(self):
        """
        unpark sends the unpark command to the mount.

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':PO#')
        if not suc:
            return False
        return True

    def stop(self):
        """
        stop sends the stop command to the mount. the command returns nothing.

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':STOP#')
        if not suc:
            return False
        return True

    def flip(self):
        """
        flip sends the flip command to the mount.

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':FLIP#')
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True
