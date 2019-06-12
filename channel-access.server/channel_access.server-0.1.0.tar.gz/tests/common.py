import os
import pytest
import subprocess

import channel_access.common as ca



INT_TYPES = [
    ca.Type.CHAR,
    ca.Type.SHORT,
    ca.Type.LONG
]
FLOAT_TYPES = [
    ca.Type.FLOAT,
    ca.Type.DOUBLE
]


EPICS_CA_ADDR = '127.0.0.1'
EPICS_CA_SERVER_PORT = '9123'
EPICS_CA_REPEATER_PORT = '9124'


class CagetError(RuntimeError):
    pass
class CaputError(RuntimeError):
    pass

def cacmd(args):
    environment = {
        'PATH': os.environ.get('PATH'),
        'EPICS_BASE': os.environ.get('EPICS_BASE'),
        'EPICS_HOST_ARCH': os.environ.get('EPICS_HOST_ARCH'),
        'EPICS_CA_ADDR_LIST': EPICS_CA_ADDR,
        'EPICS_CA_AUTO_ADDR_LIST': 'NO',
        'EPICS_CA_SERVER_PORT': EPICS_CA_SERVER_PORT,
        'EPICS_CA_REPEATER_PORT': EPICS_CA_REPEATER_PORT
    }
    return subprocess.check_output(args,
        stdin=subprocess.DEVNULL,
        env=environment,
        universal_newlines=True).strip()

def caget(pv, as_string=False, array=False):
    args = []
    if not as_string:
        args.append('-n')
    try:
        result = cacmd(['caget', '-t', '-w', '0.1'] + args + [ pv ])
    except subprocess.CalledProcessError:
        raise CagetError
    if array:
        # Remove first entry (length of array)
        return result.split()[1:]
    else:
        return result


def caput(pv, value):
    args = []
    if isinstance(value, list) or isinstance(value, tuple):
        args.append('-a')
        values = [ str(len(value)) ] + [ str(x) for x in value ]
    else:
        values = [ str(value) ]
    try:
        return cacmd(['caput', '-t', '-w', '0.1'] + args + [ pv ] + values)
    except subprocess.CalledProcessError:
        raise CaputError
