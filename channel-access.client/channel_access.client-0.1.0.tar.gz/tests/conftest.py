import os
import pytest

import channel_access.client as cac
import channel_access.server as cas
from . import common



@pytest.fixture(scope='function')
def server():
    os.environ.update({
        'EPICS_CAS_INTF_ADDR_LIST': common.EPICS_CA_ADDR,
        'EPICS_CA_SERVER_PORT': common.EPICS_CA_SERVER_PORT,
        'EPICS_CA_REPEATER_PORT': common.EPICS_CA_REPEATER_PORT
    })
    server = cas.Server()
    yield server
    server.shutdown()

@pytest.fixture(scope='function')
def client():
    os.environ.update({
        'EPICS_CA_ADDR_LIST': common.EPICS_CA_ADDR,
        'EPICS_CA_AUTO_ADDR_LIST': 'NO',
        'EPICS_CA_SERVER_PORT': common.EPICS_CA_SERVER_PORT,
        'EPICS_CA_REPEATER_PORT': common.EPICS_CA_REPEATER_PORT
    })
    client = cac.Client()
    yield client
    client.shutdown()
