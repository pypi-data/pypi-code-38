#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import device_drivers_parent_path
device_drivers_parent_path.insert()

import base
import collections
import json
import os
import os.path
import settings
from gateway_helpers import logger


COMMAND_FILE = settings.COMMAND_FILE
COMPANYNAME = settings.COMPANYNAME
TMPDIR = settings.TMPDIR
BASE_URL = settings.BASE_URL
GATEWAY_ID = settings.GATEWAY_ID


class BaseDriver(base.BaseClient):

    """transforms instructions from the server to instrument commands

    The Transformer will request a instrument instance based on the
    instrument_type given in the configuration and passes the parameters
    to the instrument. After the run, the Transformer reads back the data
    from the instrument to package up for a Transmitter to tranmit to
    the server."""

    def __init__(self, command, instr=None, *args, **kwargs):
        base.BaseClient.__init__(self, *args, **kwargs)
        self.command = command
        self.instr = instr
        self.command_id = None
        self.trace_dict = {}
        self.timer = base.Timer()
        self.metadata = collections.defaultdict(int)

    def _write_trace_dict(self, filename=''):
        if filename == '':
            filename = 'full-trace-%s.json' % self.metadata['result_id']
        trace_file = os.path.join(TMPDIR, filename)
        logger.info("Writing full trace to file: %s" % trace_file)
        with open(trace_file, 'w') as f:
            f.write(json.dumps(self.trace_dict))
