"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import argparse
import ConfigParser
import errno
import json
import netifaces
import os
import socket
import sys
from shutil import copy
from os.path import expanduser


HOME = expanduser("~")


def WinMessageBox(text='', title='GradientOne Error', style=1):
    if sys.platform == 'win32':
        import ctypes
        return ctypes.windll.user32.MessageBoxA(0, text, title, style)
    else:
        tryprint("WinMessageBox called on a non Windows system. "
                 "attempted title, text: {}, {}".format(title, text))
        return


def tryprint(msg):
    """Wraps a print statement in a try block"""
    try:
        print(msg)
    except OSError:
        # ToDo: handle an os error
        pass
    except IOError:
        # ToDo: handle an IO error
        pass
    except Exception:
        # ToDo: handle an unexpected error
        pass


def find_file(fname):
    """
    Look for a configfile in relative Downloads directory.
    If found, copy it to a relative etc director and remove the original.
    A configfile should typcally be GradientOneConfig.txt
    (previously gradientoneone.cfg or gradientone_one.cfg)
    """
    etc = os.path.join(HOME, 'etc')
    downloads = os.path.join(HOME, 'Downloads')
    configfile = os.path.join(downloads, fname)
    if os.access(configfile, os.R_OK):
        try:
            os.mkdir(etc)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        copy(configfile, etc)
        os.remove(configfile)
    configfile = os.path.join(etc, fname)
    try:
        fp = open(configfile)
    except IOError as e:
        if e.errno == errno.EACCES:
            # default data:
            DIRPATH = os.path.dirname(os.path.realpath("__file__"))
            default_file = os.path.join(DIRPATH, fname)
            tryprint("Using default data file in {}".format(default_file))
            return default_file
        # Not a permission error.
        raise
    else:
        fp.close()
        return configfile


def build_config_parser(filename='GradientOneConfig.txt'):
    """Builds a ConfigParser from config file info

    Parameters:
        filename: the filename of the config file. This gets passed
            the find_file function to

    """
    cfg = ConfigParser.ConfigParser(dict_type=dict)
    cfg.optionxform = str
    cfgfile = None
    try:
        cfgfile = find_file(filename)
    except IOError:
        raise ValueError("Could find the config file. Please download a "
                         "config file for this machine")
    try:
        cfg.read(cfgfile)
    except IOError:
        raise ValueError("Could read the config file. Please download a "
                         "config file for this machine")
    return cfg


try:
    cfg = build_config_parser()
except ValueError as e:
    if sys.platform == 'win32':
        WinMessageBox('GradientOne Error', str(e), 1)
    raise

try:
    COMMON_SETTINGS = cfg._sections['common']
    CLIENT_SETTINGS = cfg._sections['client']
except KeyError as e:
    msg = ("Encountered a KeyError when reading config file.\n\n"
           "This is most likely due to missing data in the config file. "
           "Please check the config file in ~/etc or ~/Downloads for "
           "'common' and for 'client' sections.\n\nExiting client now.")
    if sys.platform == 'win32':
        WinMessageBox(msg)
    else:
        tryprint(msg)
    sys.exit(1)


AUTH_TOKEN = CLIENT_SETTINGS['AUTH_TOKEN']
COMPANYNAME = COMMON_SETTINGS['COMPANYNAME']


try:
    val = int(COMMON_SETTINGS['CONNECTION_REFUSED_RETRY_SLEEP'])
    CONNECTION_REFUSED_RETRY_SLEEP = val
except KeyError:
    # not in the config file
    CONNECTION_REFUSED_RETRY_SLEEP = 180
except ValueError:
    # bad value, like None
    CONNECTION_REFUSED_RETRY_SLEEP = 180
except TypeError:
    # likely unable to convert invalid string, e.g. "TwoHundred"
    CONNECTION_REFUSED_RETRY_SLEEP = 180


try:
    val = int(COMMON_SETTINGS['UNEXPECTED_SOCKET_ERROR_SLEEP'])
    UNEXPECTED_SOCKET_ERROR_SLEEP = val
except KeyError:
    # not in the config file
    UNEXPECTED_SOCKET_ERROR_SLEEP = 20
except ValueError:
    # bad value, like None
    UNEXPECTED_SOCKET_ERROR_SLEEP = 20
except TypeError:
    # likely unable to convert invalid string, e.g. "TwoHundred"
    UNEXPECTED_SOCKET_ERROR_SLEEP = 20


def get_linkaddr():
    linkaddr = None
    for iface in netifaces.interfaces():
        ifaddrs = netifaces.ifaddresses(iface)
        if netifaces.AF_LINK in ifaddrs:
            linkaddr = ifaddrs[netifaces.AF_LINK][0]['addr']
            if linkaddr:
                return linkaddr
    # if no linkaddr is returned in the loop above, warn and exit
    tryprint("Unable to get address with netifaces")
    sys.exit(1)

# The id of the client machine communicating w/ GradientOne
GATEWAY_ID = socket.gethostname() + ":" + get_linkaddr()

try:
    REFRESH_TOKEN = CLIENT_SETTINGS['REFRESH_TOKEN']
except:
    REFRESH_TOKEN = AUTH_TOKEN

TMPDIR = os.path.join(HOME, 'tmp')
ETCDIR = os.path.join(HOME, 'etc')

if not os.path.exists(TMPDIR):
    try:
        os.makedirs(TMPDIR)
    except Exception as e:
        tryprint("Exception in retry of TMPDIR, e: %s" % e)


# command filename
COMMAND_FILE = "__current_command__"
if "COMMAND_FILE" in COMMON_SETTINGS:
    COMMAND_FILE = COMMON_SETTINGS["COMMAND_FILE"]
elif "COMMAND_FILENAME" in COMMON_SETTINGS:
    COMMAND_FILE = COMMON_SETTINGS["COMMAND_FILENAME"]
COMMAND_FILE = os.path.join(TMPDIR, COMMAND_FILE)

# instrument states file
STATES_FILE = "__instrument_states__"
if "STATES_FILE" in COMMON_SETTINGS:
    STATES_FILE = COMMON_SETTINGS["STATES_FILE"]
STATES_FILE = os.path.join(TMPDIR, STATES_FILE)

# for recording an error
ERROR_FILE = "__gradientone_error__"
if "ERROR_FILE" in COMMON_SETTINGS:
    ERROR_FILE = COMMON_SETTINGS["ERROR_FILE"]
ERROR_FILE = os.path.join(TMPDIR, ERROR_FILE)

# instruction filename
fname = "__current_instruction__"
INSTRUCTION_FILENAME = os.path.join(TMPDIR, fname)

# simulate instrument configuration file
fname = 'simulated_instrument.json'
SIMULATED_INSTRUMENT_CFG_FILE = os.path.join(ETCDIR, fname)

# Set globals
SECONDS_BTW_HEALTH_UPDATES = 180
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
MAX_VALID_MEAS_VAL = 1000000000

try:
    DIRPATH = os.path.dirname(os.path.realpath(__file__))
except NameError:  # We are the main py2exe script, not a module
    DIRPATH = os.path.dirname(os.path.abspath(sys.argv[0]))

try:
    DOMAINNAME = COMMON_SETTINGS['DOMAINNAME']
except KeyError:
    try:
        DOMAINNAME = COMMON_SETTINGS['DOMAIN']  # legacy config files
    except:
        DOMAINNAME = "localhost"

if DOMAINNAME.find("localhost") == 0 or DOMAINNAME.find("127.0.0.1") == 0:
    BASE_URL = "http://" + DOMAINNAME
else:
    BASE_URL = "https://" + DOMAINNAME

COMMAND_URL = BASE_URL + '/commands'
DEFAULT_TEK_TYPE = 'TektronixMDO3012'

try:
    DEFAULT_LOGFILE = CLIENT_SETTINGS['DEFAULT_LOGFILE']
except KeyError:
    DEFAULT_LOGFILE = "info.log"

try:
    ELIGIBLE_LOGFILE_SIZE = CLIENT_SETTINGS["ELIGIBLE_LOGFILE_SIZE"]
except KeyError:
    ELIGIBLE_LOGFILE_SIZE = 2000000

try:
    USE_LOOPBACK = cfg.getboolean('common', 'USE_LOOPBACK')
except:
    USE_LOOPBACK = False

try:
    SIMULATED = cfg.getboolean('client', 'SIMULATED')
except:
    SIMULATED = False

try:
    MAX_LENGTH_FOR_BROWSER = CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER']
except:
    MAX_LENGTH_FOR_BROWSER = 50000

try:
    DISABLE_DISCOVERY = cfg.getboolean('common', 'DISABLE_DISCOVERY')
except:
    DISABLE_DISCOVERY = False

IDENTITY_STRING = ''
if "IDENTITY_STRING" in COMMON_SETTINGS:
    IDENTITY_STRING = COMMON_SETTINGS["IDENTITY_STRING"]

SCOPE_ADDRESS = ''
if "SCOPE_ADDRESS" in COMMON_SETTINGS:
    SCOPE_ADDRESS = COMMON_SETTINGS["SCOPE_ADDRESS"]


# If the machine running the gateway client also happens to be
# an instrument, as is the case with a scope running Windows
# embedded on the instrument itself, the GATEWAY_IS_INSTRUMENT
# is set to True. Otherwise it is assumed to be False
GATEWAY_IS_INSTRUMENT = False
if "GATEWAY_IS_INSTRUMENT" in COMMON_SETTINGS:
    GATEWAY_IS_INSTRUMENT = COMMON_SETTINGS["GATEWAY_IS_INSTRUMENT"]


if sys.platform == 'win32':
    ARGS = ''
else:
    parser = argparse.ArgumentParser(description='Update to given version')
    parser.add_argument('-v', '--verbosity', type=str, default="info",
                        help='Verbosity for logs to console')
    parser.add_argument('-c', '--client', type=str,
                        help='Specific client to run', default="default")
    parser.add_argument('--update', dest='update', action='store_true')
    parser.add_argument('--no-update', dest='update', action='store_false')
    parser.set_defaults(update=True)
    ARGS = parser.parse_args()


KNOWN_INSTRUMENTS = [
    {
        'instrument_type': 'TektronixMSO5204B',
        'address': 'TCPIP::192.168.1.200::INSTR',
    },
    {
        'instrument_type': 'KeysightMSO9064A',
        'address': 'TCPIP::192.168.1.77::INSTR',
    },
    {
        'instrument_type': 'KeysightMSO9104A',
        'address': 'TCPIP::192.168.1.94::INSTR',
    },
    {
        'instrument_type': 'AGILENTU2000',
        'address': 'USB::0x0957::0x2b18::INSTR',
    },
    {
        'instrument_type': 'TektronixMDO4104',
        'address': 'TCPIP::192.168.1.108::INSTR',
    },
    {
        'instrument_type': 'TektronixMDO3012',
        'address': 'USB::0x0699::0x0408::INSTR',
    },
    {
        'instrument_type': 'TektronixMSO2024',
        'address': 'USB::0x0699::0x03a4::INSTR',
    },
    {
        'instrument_type': 'TektronixMSO2024B',
        'address': 'USB::0x0699::0x03a4::INSTR',
    },
    {
        'instrument_type': 'TektronixMSO2022B',
        'address': 'USB::0x0699::0x03a2::INSTR',
    },
    {
        'instrument_type': 'TektronixMSO2014',
        'address': 'USB::0x0699::0x0377::INSTR',
    },
    {
        'instrument_type': 'TektronixMSO2014B',
        'address': 'USB::0x0699::0x03a0::INSTR',
    },
    {
        'instrument_type': 'TektronixMSO2012',
        'address': 'USB::0x0699::0x0376::INSTR',
    },
    {
        'instrument_type': 'TektronixMSO2012B',
        'address': 'USB::0x0699::0x039e::INSTR',
    },
    {
        'instrument_type': 'TektronixMSO2004B',
        'address': 'USB::0x0699::0x039c::INSTR',
    },
    {
        'instrument_type': 'TektronixMSO2002B',
        'address': 'USB::0x0699::0x039a::INSTR',
    },
    {
        'instrument_type': 'TektronixDPO2024',
        'address': 'USB::0x0699::0x0374::INSTR',
    },
    {
        'instrument_type': 'TektronixDPO2024B',
        'address': 'USB::0x0699::0x03a3::INSTR',
    },
    {
        'instrument_type': 'TektronixDPO2002B',
        'address': 'USB::0x0699::0x0399::INSTR'
    },
    {
        'instrument_type': 'TektronixDPO2022B',
        'address': 'USB::0x0699::0x03a1::INSTR'
    },
    {
        'instrument_type': 'TektronixDPO2014',
        'address': 'USB::0x0699::0x0373::INSTR'
    },
    {
        'instrument_type': 'TektronixDPO2012B',
        'address': 'USB::0x0699::0x039D::INSTR'
    },
    {
        'instrument_type': 'TektronixDPO2004B',
        'address': 'USB::0x0699::0x039B::INSTR'
    },
    {
        'instrument_type': 'GENERIC_SCOPE',
        'address': 'USB::0x0699::0x03a4::INSTR'
    },
    {
        'instrument_type': 'TektronixDPO2012',
        'address': 'USB::0x0699::0x0372::INSTR'
    },
    {
        'instrument_type': 'TektronixDPO2014B',
        'address': 'USB::0x0699::0x039f::INSTR'
    },
    {
        'instrument_type': 'TektronixDPO3014',
        'address': 'USB::0x0699::0x0411::INSTR',
    },
    {
        'instrument_type': 'TektronixDPO3034',
        'address': 'TCPIP::10.1.1.100::INSTR',
    },
]


# keys of known instrument_manufacturer strings with
# values of GradientOne manufacturer strings
KNOWN_MANF_DICT = {
    'Rigol': 'Rigol',
    'Rigol Technologies': 'Rigol',
    'Keysight': 'Keysight',
    'Keysight Technologies': 'Keysight',
    'Copley': 'Copley',
    'Tektronix': 'Tektronix',
    'Agilent': 'Agilent',
    'Agilent Technologies': 'Agilent',
    'simulate': 'simulate',
}

SIMULATED_INSTRUMENT_TYPE = 'RigolDS1054Z'


if __name__ == '__main__':
    cfg = ConfigParser.ConfigParser(dict_type=dict)
    cfg.optionxform = str
    cfgfile = find_file('GradientOneConfig.txt')
    tryprint("Outputting config file details:")
    tryprint("cfgfile =", cfgfile)
    try:
        LOGDIR = CLIENT_SETTINGS["LOGDIR"]
    except:
        LOGDIR = os.path.join(HOME, 'logs')
    if not os.path.exists(LOGDIR):
        try:
            os.makedirs(LOGDIR)
        except Exception as e:
            tryprint("Exception creating log directory, e: %s" % e)
    tryprint("LOGDIR: %s" % LOGDIR)
