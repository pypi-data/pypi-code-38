from __future__ import print_function

from os.path import expanduser
from os.path import basename

import os
import sys
import requests
import ipfshttpclient as ipfsapi

import re
# Datetime conversion to rfc1123
import locale
import datetime
import logging
import platform

from six.moves.urllib.request import urlopen
import json
from .__init__ import __version__ as ipwbVersion

from pkg_resources import parse_version

# from requests.exceptions import ConnectionError
from ipfshttpclient.exceptions import ConnectionError


IPFSAPI_HOST = 'localhost'
IPFSAPI_PORT = 5001
IPWBREPLAY_HOST = 'localhost'
IPWBREPLAY_PORT = 5000

INDEX_FILE = 'samples/indexes/salam-home.cdxj'

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


dtPattern = re.compile(r"^(\d{4})(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\d{2})?$")


def isDaemonAlive(hostAndPort="{0}:{1}".format(IPFSAPI_HOST, IPFSAPI_PORT)):
    """Ensure that the IPFS daemon is running via HTTP before proceeding"""
    client = ipfsapi.Client(f"/dns/{IPFSAPI_HOST}/tcp/{IPFSAPI_PORT}/http")

    try:
        # ConnectionError/AttributeError if IPFS daemon not running
        client.id()
        return True
    except (ConnectionError):  # exceptions.AttributeError):
        logError("Daemon is not running at http://" + hostAndPort)
        return False
    except OSError:
        logError("IPFS is likely not installed. "
                 "See https://ipfs.io/docs/install/")
        sys.exit()
    except Exception as e:
        logError('Unknown error in retrieving daemon status')
        logError(sys.exc_info()[0])


def logError(errIn):
    print(errIn, file=sys.stderr)


def isValidCDXJ(stringIn):  # TODO: Check specific strict syntax
    # Also, be sure to mind the meta headers starting with @/#, etc.
    return True


def isValidCDXJLine(cdxjLine):
    try:
        (surtURI, datetime, jsonData) = cdxjLine.split(' ', 2)

        json.loads(jsonData)
        validDatetime = len(datetime) == 14

        validSURT = True  # TODO: check valid SURT URI

        return validSURT and validDatetime
    except ValueError:  # Not valid JSON
        return False
    except NameError:
        return isCDXJMetadataRecord(cdxjLine)
    except Exception as e:
        return False


# Compare versions of software, <0 if a<b, 0 if ==, >1 if b>a
def compareVersions(versionA, versionB):
    return parse_version(versionA) < parse_version(versionB)


def isCDXJMetadataRecord(cdxjLine):
    return cdxjLine.strip()[:1] == '!'


def isLocalHosty(uri):
    # TODO: check for these SW conditions
    # (*, localhost, *); (*, 127/8, *); (*, ::1/128, *)
    localhosts = ['localhost', '127.0.0.1']
    for lh in localhosts:
        if lh in uri:
            return True
    return False


def setupIPWBInIPFSConfig():
    hostPort = getIPWBReplayConfig()
    if not hostPort:
        setIPWBReplayConfig(IPWBREPLAY_HOST, IPWBREPLAY_PORT)


def setLocale():
    currentOS = platform.system()
    if currentOS == 'Darwin':
        newLocale = 'en_US'
    elif currentOS == 'Windows':
        newLocale = 'english'
    else:  # Assume Linux
        newLocale = 'en_US.utf8'

    locale.setlocale(locale.LC_TIME, newLocale)


def digits14ToRFC1123(digits14):
    setLocale()
    d = datetime.datetime.strptime(digits14, '%Y%m%d%H%M%S')
    return d.strftime('%a, %d %b %Y %H:%M:%S GMT')


def rfc1123ToDigits14(rfc1123DateString):
    setLocale()
    d = datetime.datetime.strptime(rfc1123DateString,
                                   '%a, %d %b %Y %H:%M:%S %Z')

    # TODO: Account for conversion if TZ other than GMT not specified

    return d.strftime('%Y%m%d%H%M%S')


def iso8601ToDigits14(iso8601DateString):
    setLocale()
    d = datetime.datetime.strptime(iso8601DateString,
                                   "%Y-%m-%dT%H:%M:%SZ")

    # TODO: Account for conversion if TZ other than GMT not specified

    return d.strftime('%Y%m%d%H%M%S')


def isRFC1123Compliant(dtstr):
    try:
        datetime.datetime.strptime(dtstr, '%a, %d %b %Y %H:%M:%S GMT')
        return True
    except ValueError as err:
        return False


def getRFC1123OfNow():
    setLocale()
    d = datetime.datetime.now()
    return d.strftime('%a, %d %b %Y %H:%M:%S GMT')


def padDigits14(dtstr, validate=False):
    '''Pad datetime to make a 14-digit string and optionally validate it'''
    match = dtPattern.match(dtstr)
    if match:
        Y = match.group(1)
        m = match.group(2) or '01'
        d = match.group(3) or '01'
        H = match.group(4) or '00'
        M = match.group(5) or '00'
        S = match.group(6) or '00'
        dtstr = '{}{}{}{}{}{}'.format(Y, m, d, H, M, S)
    if validate:
        datetime.datetime.strptime(dtstr, '%Y%m%d%H%M%S')
    return dtstr


def fetchRemoteFile(path):
    try:
        r = requests.get(path)
        return r.text
    except ConnectionError:
        logError('File at {0} is unavailable.'.format(path))
    except Exception as E:
        logError('An unknown error occurred trying to fetch {0}'.format(path))
        logError(sys.exc_info()[0])
    return None


# IPFS Config manipulation from here on out.
def readIPFSConfig():
    ipfsConfigPath = expanduser("~") + '/.ipfs/config'
    if 'IPFS_PATH' in os.environ:
        ipfsConfigPath = os.environ.get('IPFS_PATH') + '/config'

    try:
        with open(ipfsConfigPath, 'r') as f:
            return json.load(f)
    except IOError:
        logError("IPFS config not found.")
        logError("Have you installed ipfs and run ipfs init?")
        sys.exit()


def writeIPFSConfig(jsonToWrite):
    ipfsConfigPath = expanduser("~") + '/.ipfs/config'
    if 'IPFS_PATH' in os.environ:
        ipfsConfigPath = os.environ.get('IPFS_PATH') + '/config'

    with open(ipfsConfigPath, 'w') as f:
        f.write(json.dumps(jsonToWrite, indent=4, sort_keys=True))


def getIPFSAPIHostAndPort(ipfsJSON=None):
    if not ipfsJSON:
        ipfsJSON = readIPFSConfig()

    (scheme, host, protocol, port) = (
        ipfsJSON['Addresses']['API'][1:].split('/')
    )
    return host + ':' + port


def getIPWBReplayConfig(ipfsJSON=None):
    if not ipfsJSON:
        ipfsJSON = readIPFSConfig()
    port = None
    if ('Ipwb' in ipfsJSON and 'Replay' in ipfsJSON['Ipwb'] and
       'Port' in ipfsJSON['Ipwb']['Replay']):
        host = ipfsJSON['Ipwb']['Replay']['Host']
        port = ipfsJSON['Ipwb']['Replay']['Port']
        return (host, port)
    else:
        return None


def setIPWBReplayConfig(Host, Port, ipfsJSON=None):
    if not ipfsJSON:
        ipfsJSON = readIPFSConfig()
    ipfsJSON['Ipwb'] = {}
    ipfsJSON['Ipwb']['Replay'] = {
      u'Host': Host,
      u'Port': Port
    }
    writeIPFSConfig(ipfsJSON)


def setIPWBReplayIndexPath(cdxj):
    if cdxj is None:
        cdxj = INDEX_FILE
    ipfsJSON = readIPFSConfig()
    ipfsJSON['Ipwb']['Replay']['Index'] = cdxj
    writeIPFSConfig(ipfsJSON)
    return


def getIPWBReplayIndexPath():
    ipfsJSON = readIPFSConfig()
    if 'Ipwb' not in ipfsJSON:
        setIPWBReplayConfig(IPWBREPLAY_HOST, IPWBREPLAY_PORT)
        ipfsJSON = readIPFSConfig()

    if 'Index' in ipfsJSON['Ipwb']['Replay']:
        return ipfsJSON['Ipwb']['Replay']['Index']
    else:
        return ''


# From pywb 2.0.4
def unsurt(surt):
    try:
        index = surt.index(')/')
        parts = surt[0:index].split(',')
        parts.reverse()
        host = '.'.join(parts)
        host += surt[index+1:]
        return host

    except ValueError:
        # May not be a valid surt
        return surt


def compareCurrentAndLatestIPWBVersions():
    try:
        resp = urlopen('https://pypi.python.org/pypi/ipwb/json')
        jResp = json.loads(resp.read())
        latestVersion = jResp['info']['version']
        currentVersion = re.sub(r'\.0+', '.', ipwbVersion)
        return (currentVersion, latestVersion)
    except Exception as e:
        return (None, None)


def checkForUpdate():
    (current, latest) = compareCurrentAndLatestIPWBVersions()

    if current != latest and current is not None:
        print('This version of ipwb is outdated.'
              ' Please run pip install --upgrade ipwb.')
        print('* Latest version: {0}'.format(latest))
        print('* Installed version: {0}'.format(current))
