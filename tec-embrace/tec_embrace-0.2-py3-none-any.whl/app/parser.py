import re
import logging
from datetime import datetime

import tec_embrace.settings as settings


class ParserGeneric:

    def __init__(self, file):
        self.file = file

    def openfile(self):
        with open(self.file, mode='r') as fd:
            return fd.read()

    def parser(self):  # pragma: no cover
        pass


class ParserDCB(ParserGeneric):
    """
    Parser the DCB file, which accurately provides all the bias of each PRNs (GPS and GLONASS). These values are then
    used to subtract from the relative TEC and get a more precise estimates
    """
    _regex_DCB1 = settings.REGEX_DCB_1
    _regex_DCB2 = settings.REGEX_DCB_2
    _default_regex = r'{}{}\s\s{}{}'
    obs_mgex = settings.OBS_MGEX

    def __init__(self, file):
        """
        Initiate the parsing proceduring for DCB files

        :param file: Absolute path of DBC file
        :return: The python DCB object, with all the information (prn - bias) parsed
        """
        self.parsed = {}
        super().__init__(file)

    def regex(self, part_one, part_two):
        mounted_regex = self._default_regex.format(self._regex_DCB1, part_one, part_two, self._regex_DCB2)
        return re.compile(mounted_regex)

    def find(self, pattern):
        data = self.openfile()
        tmp = {}
        for (prn, time, bias, rms) in re.findall(pattern, data):
            tmp[prn.strip()] = [float(bias.strip()), float(rms.strip())]

        return tmp

    def parser(self):
        logging.info(">> Starting DCB parsing...")
        self.parsed['path'] = self.file
        for item, constellations in self.obs_mgex:
            tmp = {}
            for letter, constellation in constellations:
                part_one, part_two = constellation
                pattern = self.regex(part_one, part_two)
                tmp.update(self.find(pattern))

            self.parsed[item] = tmp

        return self.parsed


class ParserOrbit(ParserGeneric):
    """
    Parser orbit file in the orbit python object, where the the variable stay organized in orbit type (IGR, IGL, IGU)
    and the measures
    """
    _date = []

    def __init__(self, file):
        """
        Initiate the parsing proceduring for orbit

        :param file: Absolute path to open the orbit file
        :return: The python orbit object, with all the information parsed
        """
        self.parsed = {}
        super().__init__(file)

    def openfile(self):
        with open(self.file, mode='r') as fd:
            return fd.readlines()

    def find(self):
        data = self.openfile()
        for line in data:
            self.parse_line(line)
        return None

    def parse_line(self, line):
        if line.startswith('*'):
            year, month, day, hour, minute, seconds = [(int(float(x))) for x in line.split()[1:]]
            self._date.append(datetime(year, month, day, hour, minute, seconds))
        elif line.startswith('P'):
            prn, *coord = line[1:].split()[:4]
            self.put_in_list(prn, coord)

        self.parsed['path'] = self.file
        self.parsed['date'] = self._date
        return None

    def put_in_list(self, prn, coord):
        x, y, z = coord
        if prn not in self.parsed:
            self.parsed[prn] = list()

        self.parsed[prn].append({'x': float(x), 'y': float(y), 'z': float(z)})
        return None

    def parser(self):
        logging.info(">> Starting Orbit parsing...")
        self.find()
        return self.parsed


class ParserChannels(ParserGeneric):
    """
    Parser the frequencies/channels respect to each GLONASS PRNs. These values are essentials to the calculation
        of the selective factor
    """
    _regex = settings.REGEX_GLONASS_CHANNEL

    def __init__(self, file):
        """
        Initiate the parsing proceduring for GLONASS channels

        :param file: Absolute path to open the GLONASS channels file
        :return: The python Channels object, with all the information parsed
        """
        self.parsed = {}
        super().__init__(file)

    @property
    def pattern(self):
        return re.compile(self._regex)

    def find(self):
        data = self.openfile()
        self.put_in_parsed(data)
        return None

    def put_in_parsed(self, data):
        """
        :param data: The ASCII content from https://www.glonass-iac.ru/en/CUSGLONASS/getCUSMessage.php
        :return: The python channels object, with all the information (prn - value) parsed
        """
        for prn, channel in re.findall(self.pattern, data):
            new_channel = float(channel.strip())

            f1 = settings.FREQUENCIES['R'][0] + (new_channel * 562500.0)
            f2 = settings.FREQUENCIES['R'][1] + (new_channel * 437500.0)
            f3 = settings.FREQUENCIES['R'][2]
            factor_1 = (f1 - f2) / (f1 + f2) / settings.C
            factor_2 = (f1 * f2) / (f2 - f1) / settings.C
            factor_3 = pow(f1 * f2, 2) / (f1 + f2) / (f1 - f2) / settings.A / settings.TECU

            self.parsed[prn.strip()] = [f1, f2, f3, factor_1, factor_2, factor_3]
        return None

    def parser(self):
        logging.info(">> Starting GLONASS channels parsing...")
        self.find()
        return self.parsed


class ParserRinexChannels(ParserChannels):
    """
    Parser the frequencies/channels respect to each GLONASS PRNs. These values are essentials to the calculation
        of the selective factor
    """
    _regex = settings.REGEX_GLONASS_CHANNEL_RINEX
    A = settings.A
    TECU = settings.TECU

    def __init__(self, content):
        """
        Initiate the parsing proceduring for GLONASS channels

        :param content: The ASCII content from https://www.glonass-iac.ru/en/CUSGLONASS/getCUSMessage.php, contenting the GLONASS channels
        """
        self.parsed = {}
        super().__init__(content)

    def find(self):
        data = self.file
        self.put_in_parsed(data)
        return self.parsed


