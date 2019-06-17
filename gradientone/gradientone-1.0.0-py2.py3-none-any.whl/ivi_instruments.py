#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""
import base
import collections
import json
import usb
import ivi
import socket
import settings
import time
import vxi11
from base import c_diagnostic_logger as clogger


COMPANYNAME = settings.COMPANYNAME
COMMON_SETTINGS = settings.COMMON_SETTINGS
CLIENT_SETTINGS = settings.CLIENT_SETTINGS
TMPDIR = settings.TMPDIR
BASE_URL = settings.BASE_URL
USE_LOOPBACK = settings.USE_LOOPBACK
KNOWN_INSTRUMENTS = settings.KNOWN_INSTRUMENTS


logger = base.logger


class NoInstrument(Exception):
    pass


class SimulatedInstrument(ivi.rigol.rigolBaseScope.rigolBaseScope):
    """A better simulated instrument for testing

    Returns a class for simulating different instrument behavior

    >>> from ivi_instruments import SimulatedInstrument
    >>> options = {'fetch_screenshot_broken': True}
    >>> sim = SimulatedInstrument(options)
    Simulating; ignoring resource
    >>> sim._display_fetch_screenshot()
    I'm broken

    """
    def __init__(self, options={}, *args, **kwargs):
        super(SimulatedInstrument, self).__init__(simulate=True)
        self.name = 'simulated'
        self.channels[0].enabled = True
        self.options = collections.defaultdict(str, options)
        self._add_method('display.fetch_screenshot',
                         self._display_fetch_screenshot)
        self._add_method('measurement.fetch_waveform',
                         self._measurement_fetch_waveform)
        self._add_method('system.fetch_setup',
                         self._system_fetch_setup)

    def _display_fetch_screenshot(self):
        if self.options['fetch_screenshot_broken']:
            time.sleep(20)
        else:
            return super(SimulatedInstrument, self)._display_fetch_screenshot()

    def _measurement_fetch_waveform(self, index):
        if self.options['empty_waveform']:
            return []
        else:
            return [[1,1], [2,2]]

    def _system_fetch_setup(self):
        if self.options['broken_raw_setup']:
            time.sleep(20)
        else:
            return super(SimulatedInstrument, self)._system_fetch_setup()

    def apply_simulated_options(self):
        with open(settings.SIMULATED_INSTRUMENT_CFG_FILE) as f:
            options = json.loads(f.read())
        self.options.update(options)

    def _get_channel_enabled(self, index):
        if self.options['read_settings_failure']:
            raise base.ReadSettingsError()
        elif self.options['no_channel']:
            return False
        else:
            return super(SimulatedInstrument, self)._get_channel_enabled(index)


DEFAULT_INSTRUMENT_TYPE = ''
IVI_INSTRUMENTS_DICT = {
    'simulated': SimulatedInstrument,
    'AgilentU2000': ivi.agilent.agilentU2001A,
    'TektronixMDO4104': ivi.tektronix.tektronixMDO4104,
    'TektronixMDO3012': ivi.tektronix.tektronixMDO3012,
    'TektronixMDO3022': ivi.tektronix.tektronixMDO3022,
    'TektronixMDO3032': ivi.tektronix.tektronixMDO3032,
    'TektronixMDO3052': ivi.tektronix.tektronixMDO3052,
    'TektronixMDO3102': ivi.tektronix.tektronixMDO3102,
    'TektronixMDO3014': ivi.tektronix.tektronixMDO3014,
    'TektronixMDO3024': ivi.tektronix.tektronixMDO3024,
    'TektronixMDO3034': ivi.tektronix.tektronixMDO3034,
    'TektronixMDO3054': ivi.tektronix.tektronixMDO3054,
    'TektronixMDO3104': ivi.tektronix.tektronixMDO3104,
    'TektronixMSO2002B': ivi.tektronix.tektronixMSO2002B,
    'TektronixMSO2012': ivi.tektronix.tektronixMSO2012,
    'TektronixMSO2012B': ivi.tektronix.tektronixMSO2012B,
    'TektronixMSO2022B': ivi.tektronix.tektronixMSO2022B,
    'TektronixMSO2004B': ivi.tektronix.tektronixMSO2004B,
    'TektronixMSO2014': ivi.tektronix.tektronixMSO2014,
    'TektronixMSO2014B': ivi.tektronix.tektronixMSO2014B,
    'TektronixMSO2024': ivi.tektronix.tektronixMSO2024,
    'TektronixMSO2024B': ivi.tektronix.tektronixMSO2024,  # re-use 2024 python-ivi driver
    'TektronixMSO5204B': ivi.tektronix.tektronixMSO5204B,
    'TektronixDPO2012': ivi.tektronix.tektronixDPO2012,
    'TektronixDPO2012B': ivi.tektronix.tektronixDPO2012B,
    'TektronixDPO2014B': ivi.tektronix.tektronixDPO2014B,
    'TektronixDPO2022B': ivi.tektronix.tektronixDPO2022B,
    'TektronixDPO2004B': ivi.tektronix.tektronixDPO2004B,
    'TektronixDPO2014': ivi.tektronix.tektronixDPO2014,
    'TektronixDPO2024': ivi.tektronix.tektronixDPO2024,
    'TektronixDPO2024B': ivi.tektronix.tektronixDPO2024B,
    'TektronixDPO3014': ivi.tektronix.tektronixDPO3014,
    'TektronixDPO3034': ivi.tektronix.tektronixDPO3034,
    'KeysightMSO9104A': ivi.agilent.agilentMSO9104A,
    'KeysightMSO9064A': ivi.agilent.agilentMSO9064A,
    'RigolDS1054Z': ivi.rigol.rigolDS1054Z,
    'RigolDS1074Z': ivi.rigol.rigolDS1054Z, #re-use DS1054z python-ivi driver
    'RigolDS1104Z': ivi.rigol.rigolDS1054Z, #re-use DS1054z python-ivi driver
    'RigolDS1074Z Plus': ivi.rigol.rigolDS1074ZPlus,
    'RigolDS1104Z Plus': ivi.rigol.rigolDS1074ZPlus, #re-use DS1074ZPlus python-ivi driver
    'RigolMSO1074Z': ivi.rigol.rigolMSO1074Z,
    'RigolMSO1104Z': ivi.rigol.rigolMSO1074Z, #re-use MSO1074Z python-ivi driver
    'RigolDS2072A': ivi.rigol.rigolDS2072A,
    'RigolDS2102A': ivi.rigol.rigolDS2072A, #re-use DS2072A python-ivi driver
    'RigolDS2202A': ivi.rigol.rigolDS2072A, #re-use DS2072A python-ivi driver
    'RigolDS2302A': ivi.rigol.rigolDS2072A, #re-use DS2072A python-ivi driver
    'RigolMSO2072A': ivi.rigol.rigolMSO2072A,
    'RigolMSO2102A': ivi.rigol.rigolMSO2072A, #re-use MSO2072A python-ivi driver
    'RigolMSO2202A': ivi.rigol.rigolMSO2072A, #re-use MSO2072A python-ivi driver
    'RigolMSO2302A': ivi.rigol.rigolMSO2072A, #re-use MSO2072A python-ivi driver
    'RigolMSO5072': ivi.rigol.rigolMSO5072,
    'RigolMSO5074': ivi.rigol.rigolMSO5074,
    'RigolMSO5102': ivi.rigol.rigolMSO5072, #re-use MSO5072 python-ivi driver
    'RigolMSO5104': ivi.rigol.rigolMSO5074, #re-use MSO5074 python-ivi driver
    'RigolMSO5204': ivi.rigol.rigolMSO5074, #re-use MSO5074 python-ivi driver
    'RigolMSO5354': ivi.rigol.rigolMSO5074, #re-use MSO5074 python-ivi driver
    'RigolDS7014': ivi.rigol.rigolDS7014,
    'RigolDS7024': ivi.rigol.rigolDS7014, #re-use DS7014 python-ivi driver
    'RigolDS7034': ivi.rigol.rigolDS7014, #re-use DS7014 python-ivi driver
    'RigolDS7054': ivi.rigol.rigolDS7014, #re-use DS7014 python-ivi driver
    'RigolMSO7014': ivi.rigol.rigolMSO7014,
    'RigolMSO7024': ivi.rigol.rigolMSO7014, #re-use MSO7014 python-ivi driver
    'RigolMSO7034': ivi.rigol.rigolMSO7014, #re-use MSO7014 python-ivi driver
    'RigolMSO7054': ivi.rigol.rigolMSO7014, #re-use MSO7014 python-ivi driver
    'RigolMSO8064': ivi.rigol.rigolMSO8064,
    'RigolMSO8104': ivi.rigol.rigolMSO8064, #re-use MSO8064 python-ivi driver
    'RigolMSO8204': ivi.rigol.rigolMSO8064, #re-use MSO8064 python-ivi driver
}


class InstrumentFinder(object):
    """Discovers instruments and instantiates them

    Discovery only suppored with vxi11 instruments

    Instrument instantiation with either vxi11 or usb
    """
    def __init__(self, *args):
        # keys will be identity strings, values vxi11 addresses
        self.vxi11_addr_dict = collections.defaultdict(str)

    def _build_address(self, info_dict):
        """Builds and address from a given info dict

        The address will be used by _get_instrument to instantiate
        the instrument object for passing commands. If no address
        is found in the info, this will return None and the client
        will use the address from the config file.
        """
        if 'address' in info_dict and info_dict['address']:
            return info_dict['address']  # easy case of an address present
        else:
            addr = ''
            ip_addr = str(info_dict['instrument_ip_address'])
            device_id = manf_id = None
            manf_id = str(info_dict['usb_manufacturer_id'])
            device_id = str(info_dict['usb_device_id'])
            simulated = False
            simulated = settings.SIMULATED
            if simulated:
                logger.debug("Using simulated instrument type", exc_info=True)
            elif ip_addr:
                addr = "TCPIP0::" + ip_addr + "::INSTR"
            elif device_id and manf_id:
                addr = "USB::" + manf_id + "::" + device_id + "::INSTR"
            else:
                logger.debug("No address info, using defaults for instrument")
            return addr

    def identity_string_to_dict(self, identity_string, connection='eth0'):
        """Returns a defaultdict with the instrument data

        If no instrument data can be found, this returns an empty defaultdict
        """
        defdict = collections.defaultdict(str)
        known_manf_dict = settings.KNOWN_MANF_DICT
        identity_parts = identity_string.split(',')
        if len(identity_parts) < 3:
            logger.warning("Invalid identity data %s" % identity_parts)
            return defdict

        manf_key = identity_parts[0].title()
        if manf_key not in known_manf_dict:
            logger.warning("Unknown manufacturer {}".format(identity_parts))
            return defdict
        else:
            manufacturer = known_manf_dict[manf_key]
        model = identity_parts[1]
        instrument_dict = {
            'instrument_type': manufacturer + model,
            'manufacturer': manufacturer,
            'model': model,
            'connection': connection,
            'serial': identity_parts[2],
            'id': manufacturer + model + ':' + identity_parts[2]
        }
        if settings.USE_LOOPBACK:
            instrument_dict['address'] = 'TCPIP::127.0.0.1::INSTR'
        elif connection == 'eth0':
            instrument_dict['address'] = self.vxi11_addr_dict[identity_string]
        logger.info("identity_string_to_dict: instrument_dict=" + str(instrument_dict))
        defdict.update(instrument_dict)
        return defdict

    def find_instrument_by_string(self, identity_string):
        instrument_data = self.identity_string_to_dict(identity_string)
        if not instrument_data:
            logger.info("No instrument matching parameters")
            raise NoInstrument("No instrument matching parameters")
        else:
            return self.find_instrument_by_data(instrument_data)

    def _validate_instrument_data(self, instrument_data):
        """Validates that instrument data has what it needs.

        If something is missing the method raises an exception

        Raises:
            NoInstrument - when no instrument would match input

        Returns:
            instrument_data - if no errors, returns instrument_data
                with the address to use for the instrument
        """
        instrument_type = instrument_data['instrument_type']
        if not instrument_type:
            raise NoInstrument("No instrument_type provided for "
                               "find_instrument_by_data, returning None")
        logger.info("find_instrument: instrument_type=" + str(instrument_type))
        address = self._build_address(instrument_data)
        if not address:
            raise NoInstrument("No address for the instrument, nothing to "
                               "instantiate")
        if not address:
            raise NoInstrument("Unknown instrument type '%s' "
                               "unable to create instance"
                               % instrument_type)
        return instrument_data

    def find_instrument_by_data(self, instrument_data={}):
        """Finds an instrument from input

        Returns an ivi instance of the instrument
        """
        logger.info("find_instrument_by_data: instrument_data={}"
                    .format(instrument_data))
        try:
            validated = self._validate_instrument_data(instrument_data)
        except NoInstrument:
            raise
        instrument_type = validated['instrument_type']
        logger.info("Attempting to instantiate {} with address {}"
                    .format(instrument_type, validated['address']))
        address = str(validated['address'])
        # instantiate the instrument with the validated data
        ivi_instrument = IVI_INSTRUMENTS_DICT[instrument_type](address)
        if ivi_instrument:
            logger.info("Instantion succeeded. Setting driver_operation.cache"
                        " to False")
            # set driver_operation.cache to avoid cache errors
            ivi_instrument.driver_operation.cache = False
            return ivi_instrument
        else:
            logger.warning("Unable to instantiate {} w/ instrument_data {}"
                           .format(instrument_type, instrument_data))
            return None

    def _discover_vxi11_addresses(self):
        vxi11_addresses = []
        for bcast_addr in get_broadcasts():
            bcast_addr = str(bcast_addr)
            logger.info("_discover_vxi11_addresses(): bcast_addr {}"
                        .format(bcast_addr))
            try:
                vxi11_addresses += vxi11.list_resources(bcast_addr)
            except AttributeError as e:
                logger.warning("Wrong version of vxi11 installed. "
                               "AttributeError: {}".format(e))
            except Exception as e:
                logger.warning("Unable to list vxi11 resources. Unexpected "
                               "error: {}".format(e))
        return vxi11_addresses

    def _ask_for_vxi11_identity_strings(self, vxi11_addresses):
        """Iterates through addresses to ask *IDN for identity"""
        identity_strings = []
        if vxi11_addresses:
            clogger.info("These vxi11 addresses were found via the broadcast check %s" % vxi11_addresses)
        else:
            clogger.info("No vxi11 addresses were found")
        for addr in vxi11_addresses:
            if addr == 'TCPIP::127.0.0.1::INSTR':
                continue
            # # check if address matches address of instrument objects we already have
            # if addr in vxi11_instruments_dict:
            #     continue
            vxi11_instr = None
            try:
                vxi11_instr = vxi11.Instrument(addr)
            # ToDo: identify and handle more specific exceptions
            except Exception as e:
                logger.warning("Unexpected error creating Instrument with "
                               "addr: {}; err: {};".format(addr, e))
            if vxi11_instr:
                clogger.info("A vxi11_instr was instantiated over TCP at this address %s with this client_id %s" % (vxi11_instr.host, vxi11_instr.client_id))
            else:
                clogger.info("A vxi11_instr was not found at this address %s ", addr)
                continue  # cannot ask *IDN, move on to next address
            identity_string = ''
            try:
                identity_string = vxi11_instr.ask("*IDN?")
            except Exception as e:
                logger.warning("Unexpected error creating Instrument with "
                               "addr: {}; err: {};".format(addr, e))
            # done with the vxi11_instr, close it
            vxi11_instr.close()
            if identity_string:
                clogger.info("A new identity string was found: %s at this address: %s " % (identity_string, vxi11_instr.host))
                self.vxi11_addr_dict[identity_string] = addr
                identity_strings.append(identity_string)
            else:
                clogger.info("No new identity string was found for addreess %s " % addr)
        if identity_strings:
            clogger.info("These new identity strings were returned %s" % identity_strings)
        else:
            clogger.info("No new identity strings were returned")
        return identity_strings  # use self.vxi11_addr_dict.keys() instead

    def get_loopback_id_string(self):
        """Gets a loopback identity string from the instrument

        Summary:
            Instantiates the instrument and asks "*IDN?" for the
            identity string. If a socket error is encountered,
            the function waits depending on the error. The seconds
            to sleep can be set in the config file for settings.
        """
        addr = 'TCPIP::127.0.0.1::INSTR'
        logger.info("vxi11 discovery: USE_LOOPBACK addr {}".format(addr))
        id_string = None
        try:
            device = vxi11.Instrument(addr)
            id_string = device.ask("*IDN?")
            logger.info("id string is %s  " % id_string)
        except socket.error as e:
            logger.warning("Socket err {} in get_loopback_id_string".format(e))
            device.close()
            if e.errno == 10061:
                seconds_to_sleep = settings.CONNECTION_REFUSED_RETRY_SLEEP
                logger.warning("Connection Refused. Waiting {} seconds for "
                               "instrument to start".format(seconds_to_sleep))
            else:
                seconds_to_sleep = settings.UNEXPECTED_SOCKET_ERROR_SLEEP
                logger.warning("Unexpected Socket Error. Waiting {} seconds "
                               "before retrying".format(seconds_to_sleep))
            time.sleep(seconds_to_sleep)
        except Exception as e:
            logger.warning("Unexpected err {} in get_loopback_id_string "
                           "and id_string will return as None".format(e))
            return None
        if id_string:
            return id_string
        try:
            device = vxi11.Instrument(addr)  # probably don't need to instantiate again.  try taking this line out and see if it still works.
            id_string = device.ask("*IDN?")
        except Exception as e:
            logger.warning("Second try failed with {}".format(e))
        if id_string:
            return id_string


    def discover_vxi11_instruments(self):
        """Discovers connected vxi11 instrument instances

        Summary:
            Builds a list of identity strings, id_strings, either with
            _discover_vxi11_addresses and _ask_for_vxi11_identity_strings
            or with get_loopback_id_string if USE_LOOPBACK is True.
            Then for each id_string of id_strings, append and instrument
            object to list instruments if an instrument is found for
            that id_string

        Returs:
            instruments - a list of vxi11 instrument objects
        """
        instruments = []
        id_strings = []
        if settings.USE_LOOPBACK:
            id_string = self.get_loopback_id_string()
            if id_string:
                id_strings.append(id_string)
            else:
                logger.warning("Unable to get loopback ID string")
        else:
            new_addresses = self._discover_vxi11_addresses()
            id_strings = self._ask_for_vxi11_identity_strings(new_addresses)
        for id_string in id_strings:
            instrument = self.find_instrument_by_string(id_string)
            if instrument:
                instruments.append(instrument)
            else:
                logger.info("Unable to get instrument for id_string {}"
                            .format(id_string))
        self._log_discovery_results(instruments)
        return instruments

    def _log_discovery_results(self, instruments):
        logger.info("Discovered vxi11 instruments: {}".format(instruments))
        if settings.USE_LOOPBACK and instruments:
            clogger.info("Loopback instrument is %s" % instruments[0])
        elif instruments:
            clogger.info("These instruments were discovered %s" % instruments)
        else:
            clogger.info("No new instruments were discovered")


def get_instrument(inst_data):
    """Tries to get an instrument instance

    If function encounters a USBError it will sleep 3 seconds
    and then try again.
    """
    instrument_finder = InstrumentFinder()
    try:
        return instrument_finder.find_instrument_by_data(inst_data)
    except usb.core.USBError:
        time.sleep(3)
    except Exception as e:
        logger.info("Unexpected error in get_instrument(): {}".format(e),
                    exc_info=True)
        return
    try:
        return instrument_finder.find_instrument_by_data(inst_data)
    except usb.core.USBError:
        logger.warning("USBError occurred twice. Unable to get instrument")
        return
    except Exception as e:
        logger.info("Unexpected error in get_instrument(): {}".format(e),
                    exc_info=True)
        return


def get_broadcasts():
    import netifaces

    interfaces = [netifaces.ifaddresses(interface)
                  for interface in netifaces.interfaces()
                  ]
    bcasts = [af_inet_info['broadcast']
              if 'broadcast' in af_inet_info
              else af_inet_info['peer']

              for interface in interfaces
              if netifaces.AF_INET in interface
              for af_inet_info in interface[netifaces.AF_INET]
              ]

    return bcasts


def get_connected_vxi11_instruments():
    logger.info("checking for connected vxi11 instruments")
    disable_discovery = settings.DISABLE_DISCOVERY
    inst_finder = InstrumentFinder()
    if disable_discovery:
        clogger.info("Discovery is disabled, getting connected vxi11 instruments using manual instrument settings")
        inst_finder.vxi11_addr_dict[settings.IDENTITY_STRING] = settings.SCOPE_ADDRESS
        instr = inst_finder.find_instrument_by_string(settings.IDENTITY_STRING)
        logger.info("get_connected_vxi11_instruments: DISABLE_DISCOVERY: "
                    "instr=" + str(instr))
        if instr:
            return [instr]
        else:
            return []
    else:
        clogger.info("Using discovery feature to get connected vxi11 instruments")
        return inst_finder.discover_vxi11_instruments()


def get_connected_usb_instruments():
    known_addresses = [i['address'] for i in KNOWN_INSTRUMENTS]
    clogger.info("Looking for new USB devices")
    devices = base.get_usb_devices()
    connected_usb_instruments = []
    inst_finder = InstrumentFinder()
    for device in devices:
        nums = device['usb_id'].split(':')
        address = 'USB::0x' + nums[0] + '::0x' + nums[1] + '::INSTR'
        if address in known_addresses:
            idx = known_addresses.index(address)
            device.update(KNOWN_INSTRUMENTS[idx])
            device['connection'] = 'usb'
            instrument = inst_finder.find_instrument_by_data(device)
            if instrument:
                connected_usb_instruments.append(instrument)
            else:
                logger.info("Unable to get instrument from device info {}"
                            .format(device))
    logger.info("Known connected usb instruments: %s"
                % connected_usb_instruments)
    if connected_usb_instruments:
        clogger.info("These USB instruments were found %s " % connected_usb_instruments)
    else:
        clogger.info("No USB instruments were found")
    return connected_usb_instruments


def get_connected_scopes():
    """Returns a list of connected scopes as ivi objects
    """
    if settings.SIMULATED:
        logger.info("Simulated mode active. Returning SimulatedInstrument")
        return [SimulatedInstrument()]
    scopes = []
    # try block below should be phased out.  It guarantees that USB support won't work.
    try:
        scopes.extend(get_connected_usb_instruments())
    except Exception as e:
        logger.warning(e, exc_info=True)
    scopes.extend(get_connected_vxi11_instruments())
    logger.info("get_connected_scopes: scopes = " + str(scopes))
    return scopes


def update_settings(cfg_settings={}):
    """Updates the settings used for finding ivi instruments

    Summary:
        This is used for configuring custom settings for finding ivi
        instruments, mainly for testing and debugging purposes

    Parameters:
        cfg_settings: custom cfg settings to use for checking for scopes.
            if cfg_settings is {} then the regular settings from settings.py
            will be used.
    """
    if cfg_settings:
        if 'use_loopback' in cfg_settings:
            logger.info("Setting USE_LOOPBACK: was {}, now {}"
                        .format(settings.USE_LOOPBACK,
                            cfg_settings['use_loopback'])
                        )
            settings.USE_LOOPBACK = cfg_settings['use_loopback']
        if 'disable_discovery' in cfg_settings:
            logger.info("Setting DISABLE_DISCOVERY: was {}, now {}"
                        .format(settings.DISABLE_DISCOVERY,
                            cfg_settings['disable_discovery'])
                        )
            settings.DISABLE_DISCOVERY = cfg_settings['disable_discovery']
