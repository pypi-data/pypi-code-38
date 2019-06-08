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
import numpy
import skyfield.api
# local imports
from mountcontrol.connection import Connection
from mountcontrol.convert import stringToDegree
from mountcontrol.convert import valueToFloat
from mountcontrol.convert import valueToInt
from mountcontrol.convert import valueToAngle


class Model(object):
    """
    The class Model inherits all information and handling of the actual
    alignment model used by the mount and the data, which models are stored
    in the mount and provides the abstracted interface to a 10 micron mount.

        >>> settings = Model(
        >>>                     host=host,
        >>>                 )

    """

    __all__ = ['Model',
               'starList',
               'numberStars',
               'numberNames',
               'addStar',
               'delStar',
               'addName',
               'delName',
               'checkStarListOK',
               'checkNameListOK',
               'pollNames',
               'pollStars',
               'pollNames',
               'pollStars',
               'pollCount',
               'clearAlign',
               'deletePoint',
               'storeName',
               'loadName',
               'deleteName',
               'programAlign',
               ]
    version = '0.6'
    logger = logging.getLogger(__name__)

    # 10 microns have 3492 as default port
    DEFAULT_PORT = 3492

    def __init__(self,
                 host=None,
                 ):

        self.host = host
        self.numberNames = None
        self.numberStars = None
        self._starList = list()
        self._nameList = list()
        self._altitudeError = None
        self._azimuthError = None
        self._polarError = None
        self._positionAngle = None
        self._orthoError = None
        self._altitudeTurns = None
        self._azimuthTurns = None
        self._terms = None
        self._errorRMS = None

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
    def altitudeError(self):
        return self._altitudeError

    @altitudeError.setter
    def altitudeError(self, value):
        self._altitudeError = valueToAngle(value)

    @property
    def azimuthError(self):
        return self._azimuthError

    @azimuthError.setter
    def azimuthError(self, value):
        self._azimuthError = valueToAngle(value)

    @property
    def polarError(self):
        return self._polarError

    @polarError.setter
    def polarError(self, value):
        self._polarError = valueToAngle(value)

    @property
    def positionAngle(self):
        return self._positionAngle

    @positionAngle.setter
    def positionAngle(self, value):
        if isinstance(value, skyfield.api.Angle):
            self._positionAngle = value
            return
        self._positionAngle = valueToAngle(value)

    @property
    def orthoError(self):
        return self._orthoError

    @orthoError.setter
    def orthoError(self, value):
        self._orthoError = valueToAngle(value)

    @property
    def altitudeTurns(self):
        return self._altitudeTurns

    @altitudeTurns.setter
    def altitudeTurns(self, value):
        self._altitudeTurns = valueToFloat(value)

    @property
    def azimuthTurns(self):
        return self._azimuthTurns

    @azimuthTurns.setter
    def azimuthTurns(self, value):
        self._azimuthTurns = valueToFloat(value)

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, value):
        # qci mount don't deliver this value
        if value == '':
            self.logger.error('QCI mount does not provide terms')
        self._terms = valueToFloat(value)

    @property
    def errorRMS(self):
        return self._errorRMS

    @errorRMS.setter
    def errorRMS(self, value):
        if value == '':
            self.logger.error('QCI mount does not provide RMS')
            return
        self._errorRMS = valueToFloat(value)

    @property
    def starList(self):
        return self._starList

    @starList.setter
    def starList(self, value):
        if not isinstance(value, list):
            self._starList = list()
            return
        if all([isinstance(x, AlignStar) for x in value]):
            self._starList = value
        else:
            self._starList = list()

    @property
    def numberStars(self):
        return self._numberStars

    @numberStars.setter
    def numberStars(self, value):
        if value is None:
            self._numberStars = None
        else:
            self._numberStars = valueToInt(value)

    def addStar(self, value):
        """
        Adds a star to the list of stars. Type of name should be class AlignStar.

        :param      value:  name as type AlignStar
        :return:    nothing
        """

        if isinstance(value, AlignStar):
            self._starList.insert(len(self._starList), value)
            return
        if not isinstance(value, (list, str)):
            self.logger.error('malformed value: {0}'.format(value))
            return
        if isinstance(value, str):
            value = value.split(',')
        if len(value) == 5:
            ha, dec, err, angle, number = value
            value = AlignStar(coord=(ha, dec),
                              errorRMS=err,
                              errorAngle=angle,
                              number=number)
            self._starList.insert(len(self._starList), value)

    def delStar(self, value):
        """
        Deletes a name from the list of stars at position value. The numbering
        is from 0 to len -1 of list.

        :param value: position as int
        """

        value = valueToInt(value)
        if value < 0 or value > len(self._starList) - 1:
            self.logger.error('invalid value: {0}'.format(value))
            return
        self._starList.pop(value)

    def checkStarListOK(self):
        """
        Make a check if the actual alignment star count by polling gets the same
        number of stars compared to the number of stars in the list.
        Otherwise something was changed.

        :return: True if same size
        """

        if not self._numberStars:
            return False
        if self._numberStars == len(self._starList):
            return True
        else:
            return False

    @property
    def nameList(self):
        return self._nameList

    @nameList.setter
    def nameList(self, value):
        if not isinstance(value, list):
            self._nameList = list()
            return
        if all([isinstance(x, str) for x in value]):
            self._nameList = value
        else:
            self._nameList = list()

    @property
    def numberNames(self):
        return self._numberNames

    @numberNames.setter
    def numberNames(self, value):
        if value is None:
            self._numberNames = None
        else:
            self._numberNames = valueToInt(value)

    def addName(self, value):
        """
        Adds a name to the list of names. Type of name should be str.

        :param value: name as str
        :return: nothing
        """

        if not isinstance(value, str):
            self.logger.error('malformed value: {0}'.format(value))
            return
        self._nameList.insert(len(self._nameList), value)

    def delName(self, value):
        """
        Deletes a name from the list of names at position value. The numbering
        is from 0 to len -1 of list.

        :param value: position as int
        :return: nothing
        """

        value = valueToInt(value)
        if value < 0 or value > len(self._nameList) - 1:
            self.logger.error('invalid value: {0}'.format(value))
            return
        self._nameList.pop(value)

    def checkNameListOK(self):
        """
        Make a check if the actual model name count by polling gets the same
        number of names compared to the number of names in the list.
        Otherwise something was changed.

        :return: True if same size
        """
        if not self._numberNames:
            return False
        if self._numberNames == len(self._nameList):
            return True
        else:
            return False

    def _parseNames(self, response, numberOfChunks):
        """
        Parsing the model names cluster. The command <:modelnamN#> returns:
            - the string "#" if N is not valid
            - the name of model N, terminated by the character "#"

        :param response:        data load from mount
               numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks:
            self.logger.error('wrong number of chunks')
            return False
        for name in response:
            if not name:
                continue
            self.addName(name)
        return True

    def _parseNumberNames(self, response, numberOfChunks):
        """
        Parsing the model star number. The command <:modelcnt#> returns:
            - the string "nnn#", where nnn is the number of models available

        :param response:        data load from mount
               numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks:
            self.logger.error('wrong number of chunks')
            return False
        if len(response) != 1:
            self.logger.error('wrong number of chunks')
            return False
        self.numberNames = response[0]
        return True

    def pollNames(self):
        """
        Sending the polling ModelNames command. It collects for all the known names
        the string. The number of names have to be collected first, than it gathers
        all name at once.

        :return: success:   True if ok, False if not
        """

        conn = Connection(self.host)
        # alternatively we know already the number, and skip the gathering
        commandString = ':modelcnt#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self._parseNumberNames(response, numberOfChunks)
        if not suc:
            return False
        # now the real gathering of names
        commandString = ''
        for i in range(1, self.numberNames + 1):
            commandString += (':modelnam{0:d}#'.format(i))
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        self._nameList = list()
        suc = self._parseNames(response, numberOfChunks)
        return suc

    def _parseStars(self, response, numberOfChunks):
        """
        Parsing the model names cluster. The command <:getalpN#> returns:
            - the string "E#" if N is out of range
            - otherwise a string formatted as follows
                "HH:MM:SS.SS,+dd*mm:ss.s,eeee.e,ppp#"
        where
        -   HH:MM:SS.SS is the hour angle of the alignment star in hours, minutes, seconds
            and hundredths of second (from 0h to 23h59m59.99s),
        -   +dd*mm:ss.s is the declination of the alignment star in degrees, arcminutes,
            arcseconds and tenths of arcsecond, eeee.e is the error between the star and
            the alignment model in arcseconds,
        -   ppp is the polar angle of the measured star with respect to the modeled star
            in the equatorial system in degrees from 0 to 359 (0 towards the north pole,
            90 towards east)

        :param response:        data load from mount
               numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks:
            self.logger.error('Wrong number of chunks')
            return False
        for number, starData in enumerate(response):
            if not starData:
                continue
            # mount counts stars from 1 beginning and adding the number (which is not
            # provided by the response, but counted in the mount computer
            # for reference reasons
            modelStar = '{0:s}, {1}'.format(starData, number + 1)
            self.addStar(modelStar)
        return True

    def _parseNumberStars(self, response, numberOfChunks):
        """
        Parsing the model star number. The command <:getalst#> returns:
            - the number of alignment stars terminated by '#'

        :param response:        data load from mount
               numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks or len(response) == 0:
            self.logger.error('Wrong number of chunks')
            return False
        self.numberStars = response[0]
        # else we have to process the second chunk as well
        if numberOfChunks < 2:
            self.logger.error('Wrong number of chunks')
            return False
        responseSplit = response[1].split(',')
        if response == ['0', 'E']:
            responseSplit = [None] * 9
        if len(responseSplit) != 9:
            self.logger.error('Wrong number of chunks in getain')
            return False
        self.altitudeError = responseSplit[0]
        self.azimuthError = responseSplit[1]
        self.polarError = responseSplit[2]
        self.positionAngle = responseSplit[3]
        self.orthoError = responseSplit[4]
        self.azimuthTurns = responseSplit[5]
        self.altitudeTurns = responseSplit[6]
        self.terms = responseSplit[7]
        self.errorRMS = responseSplit[8]
        return True

    def pollStars(self):
        """
        Sending the polling ModelNames command. It collects for all the known names
        the string. The number of names have to be collected first, than it gathers
        all name at once.

        :return:    success:    True if ok, False if not
        """

        conn = Connection(self.host)
        commandString = ':getalst#:getain#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self._parseNumberStars(response, numberOfChunks)
        if not suc:
            return False
        # now the real gathering of names
        commandString = ''
        for i in range(1, self.numberStars + 1):
            commandString += (':getalp{0:d}#'.format(i))
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        self._starList = list()
        suc = self._parseStars(response, numberOfChunks)
        return suc

    def pollCount(self):
        """
        pollSetting counts collects the data of number of alignment stars and number of model
        names and updates them in the model class

        :return:    success
        """

        conn = Connection(self.host)
        # alternatively we know already the number, and skip the gathering
        commandString = ':modelcnt#:getalst#'

        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if len(response) != numberOfChunks:
            self.logger.error('Wrong number of chunks')
            return False
        if len(response) != 2:
            self.logger.error('Wrong number of chunks')
            return False
        self.numberNames = response[0]
        self.numberStars = response[1]
        return True

    def clearAlign(self):
        """
        clear model sends the clear command to the mount and deletes the current alignment
        model and alignment stars

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':delalig#')
        if not suc:
            return False
        if response[0] != '':
            return False
        return True

    def deletePoint(self, number):
        """
        deletePoint deletes the point with number from the actual alignment model. the
        model will be recalculated by the mount computer afterwards. number has to be an
        existing point in the database. the counting is from 1 to N.

        :param      number: number of point in int / float
        :return:    success
        """

        if not isinstance(number, (int, float)):
            return False
        number = int(number)
        if 0 > number < self._numberStars:
            return False
        conn = Connection(self.host)
        commandString = ':delalst{0:d}#'.format(number)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def storeName(self, name):
        """
        storeName saves the actual alignment model to the database of the mount computer
        under the given name. the name is context sensitive and does contain maximum 15
        characters.

        :param      name: name of model as string
        :return:    success
        """

        if not isinstance(name, str):
            return False
        if len(name) > 15:
            return False
        conn = Connection(self.host)
        # as the mount does raise an error, if the name already exists, we delete it
        # anyway before saving to a name
        commandString = ':modeldel0{0}#:modelsv0{1}#'.format(name, name)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            self.logger.info('model >{0}< overwritten'.format(name))
        if response[1] != '1':
            return False
        return True

    def loadName(self, name):
        """
        loadName loads from the database of the mount computer the model under the given
        name as the actual alignment model . the name is context sensitive and does contain
        maximum 15 characters.

        :param      name: name of model as string
        :return:    success
        """

        if not isinstance(name, str):
            return False
        if len(name) > 15:
            return False
        conn = Connection(self.host)
        commandString = ':modelld0{0}#'.format(name)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def deleteName(self, name):
        """
        deleteName deletes the model from the database of the mount computer under the
        given name. the name is context sensitive and does contain maximum 15 characters.

        :param      name: name of model as string
        :return:    success
        """

        if not isinstance(name, str):
            return False
        if len(name) > 15:
            return False
        conn = Connection(self.host)
        commandString = ':modeldel0{0}#'.format(name)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def programAlign(self, build):
        """
        programAlign builds a new alignment model in the mount computer by transferring
        the necessary data to the mount. the command is:

            :newalptMRA,MDEC,MSIDE,PRA,PDEC,SIDTIME#

        where the parameters are
            MRA     – the mount-reported right ascension, expressed as HH:MM:SS.S
            MDEC    – the mount-reported declination, expressed as sDD:MM:SS
            MSIDE   – the mount-reported pier side (the letter 'E' or 'W'), as reported
                        by the :pS# command)
            PRA     – the plate-solved right ascension (i.e. the right ascension the
                        telescope was effectively pointing to), expressed as HH:MM:SS.S
            PDEC    – the plate-solved declination (i.e. the declination the telescope
                        was effectively pointing to), expressed as sDD:MM:SS
            SIDTIME – the local sidereal time at the time of the measurement of the
                        point, expressed as HH:MM:SS.S
            Returns:
                the string "nnn#" if the point is valid, where nnn is the current number
                    of points in the alignment specification (including this one)
                the string "E#" if the point is not valid

        :param      build: list of aPoint
        :return:    success
        """

        if not isinstance(build, list):
            return False
        if not all([isinstance(x, APoint) for x in build]):
            return False

        conn = Connection(self.host)
        # formatting:
        # conversion, we have to find out the sign
        raFormat = '{0:02.0f}:{1:02.0f}:{2:04.1f}'
        decFormat = '{sign}{0:02.0f}*{1:02.0f}:{2:03.0f}'

        # writing new model
        commandString = ':newalig#'
        # getting star info in
        for aPoint in build:
            if not aPoint.sCoord or not aPoint.mCoord:
                continue
            ra = raFormat.format(*aPoint.mCoord.ra.hms())
            dec = decFormat.format(*aPoint.mCoord.dec.signed_dms()[1:4],
                                   sign='+' if aPoint.mCoord.dec.degrees > 0 else '-')

            pierside = aPoint.pierside

            raSolve = raFormat.format(*aPoint.sCoord.ra.hms())
            decSolve = decFormat.format(*aPoint.sCoord.dec.signed_dms()[1:4],
                                        sign='+' if aPoint.sCoord.dec.degrees > 0 else '-')

            sidereal = aPoint.sidereal

            comFormat = ':newalpt{0},{1},{2},{3},{4},{5}#'
            value = comFormat.format(ra,
                                     dec,
                                     pierside,
                                     raSolve,
                                     decSolve,
                                     sidereal,
                                     )
            commandString += value
        # closing command
        commandString += ':endalig#'

        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if 'E' in response:
            return False
        return True


class AlignStar(object):
    """
    The class AlignStar inherits all information and handling of one star in
    the alignment model used by the mount and the data in the mount and provides the
    abstracted interface to a 10 micron mount.
    The coordinates are in JNow topocentric

        >>> settings = AlignStar(
        >>>                     coord=None,
        >>>                     errorRMS=0,
        >>>                     errorAngle=0,
        >>>                     number=0,
        >>>                     )

    point could be from type skyfield.api.Star or just a tuple of (ha, dec) where
    the format should be float or the 10micron string format.

    Command protocol (from2.8.15 onwards):
    "HH:MM:SS.SS,+dd*mm:ss.s,eeee.e,ppp#" where HH:MM:SS.SS is the hour angle of the
    alignment star in hours, minutes, seconds and hundredths of second (from 0h to
    23h59m59.99s), +dd*mm:ss.s is the declination of the alignment star in degrees,
    arcminutes, arcseconds and tenths of arcsecond, eeee.e is the error between the star
    and the alignment model in arcseconds, ppp is the polar angle of the measured star
    with respect to the modeled star in the equatorial system in degrees from 0 to 359
    (0 towards the north pole, 90 towards east).
    """

    __all__ = ['AlignStar',
               'coord',
               'errorRMS',
               'errorAngle',
               'errorRA',
               'errorDEC',
               'number',
               ]
    version = '0.51'
    logger = logging.getLogger(__name__)

    def __init__(self,
                 coord=None,
                 errorRMS=None,
                 errorAngle=None,
                 number=None,
                 ):

        self.coord = coord
        self.errorRMS = errorRMS
        self.errorAngle = errorAngle
        self.number = number

    @property
    def coord(self):
        return self._coord

    @coord.setter
    def coord(self, value):
        if isinstance(value, skyfield.api.Star):
            self._coord = value
            return
        if not isinstance(value, (tuple, list)):
            self._coord = None
            return
        if len(value) != 2:
            self._coord = None
            return
        ha, dec = value
        ha = stringToDegree(ha)
        dec = stringToDegree(dec)
        if not ha or not dec:
            self._coord = None
            self.logger.error('Malformed value: {0}'.format(value))
            return
        self._coord = skyfield.api.Star(ra_hours=ha,
                                        dec_degrees=dec)

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        self._number = valueToInt(value)

    @property
    def errorRMS(self):
        return self._errorRMS

    @errorRMS.setter
    def errorRMS(self, value):
        self._errorRMS = valueToFloat(value)

    @property
    def errorAngle(self):
        return self._errorAngle

    @errorAngle.setter
    def errorAngle(self, value):
        if isinstance(value, skyfield.api.Angle):
            self._errorAngle = value
            return
        self._errorAngle = valueToAngle(value)

    def errorRA(self):
        if self._errorRMS and self._errorAngle:
            return self._errorRMS * numpy.sin(self._errorAngle.radians)
        else:
            return None

    def errorDEC(self):
        if self._errorRMS and self._errorAngle:
            return self._errorRMS * numpy.cos(self._errorAngle.radians)
        else:
            return None

    def __gt__(self, other):
        if other > self._errorRMS:
            return True
        else:
            return False

    def __ge__(self, other):
        if other >= self._errorRMS:
            return True
        else:
            return False

    def __lt__(self, other):
        if other < self._errorRMS:
            return True
        else:
            return False

    def __le__(self, other):
        if other <= self._errorRMS:
            return True
        else:
            return False


class APoint(object):
    """
    The class APoint inherits all information and handling of the coordinates of
    a pointing direction of the nominal mount coordinates and the plate solved
    coordinates, which were derived from a taken image at the scope
    the coordinates both are in JNow topocentric

        >>> settings = APoint(
        >>>                     )

    coordinates could be from type skyfield.api.Star or just a tuple of (ha, dec) where
    the format should be float or the 10micron string format.

    """

    __all__ = ['APoint',
               'mCoord',
               'pierside',
               'sCoord',
               'sidereal',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    def __init__(self,
                 mCoord=None,
                 pierside=None,
                 sCoord=None,
                 sidereal=None,
                 ):

        self.mCoord = mCoord
        self.pierside = pierside
        self.sCoord = sCoord
        self.sidereal = sidereal

    @property
    def mCoord(self):
        return self._mCoord

    @mCoord.setter
    def mCoord(self, value):
        if isinstance(value, skyfield.api.Star):
            self._mCoord = value
            return
        if not isinstance(value, (tuple, list)):
            self._mCoord = None
            return
        if len(value) != 2:
            self._mCoord = None
            return
        ha, dec = value
        ha = stringToDegree(ha)
        dec = stringToDegree(dec)
        if not ha or not dec:
            self._mCoord = None
            self.logger.error('Malformed value: {0}'.format(value))
            return
        self._mCoord = skyfield.api.Star(ra_hours=ha,
                                         dec_degrees=dec)

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
    def sCoord(self):
        return self._sCoord

    @sCoord.setter
    def sCoord(self, value):
        if isinstance(value, skyfield.api.Star):
            self._sCoord = value
            return
        if not isinstance(value, (tuple, list)):
            self._sCoord = None
            return
        if len(value) != 2:
            self._sCoord = None
            return
        ha, dec = value
        ha = stringToDegree(ha)
        dec = stringToDegree(dec)
        if not ha or not dec:
            self._sCoord = None
            self.logger.error('Malformed value: {0}'.format(value))
            return
        self._sCoord = skyfield.api.Star(ra_hours=ha,
                                         dec_degrees=dec)

    @property
    def sidereal(self):
        return self._sidereal

    @sidereal.setter
    def sidereal(self, value):
        if not isinstance(value, str):
            self._sidereal = None
            return
        self._sidereal = value
