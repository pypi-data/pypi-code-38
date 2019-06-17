"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

"""
The bscopepost module supplies one class, BitScope.  For example,

>>> from bscopepost import BitScope
>>> bits = BitScope(acq_dict)
>>> bits.transmit()
"""

import time
import datetime
import math
import itertools
import json
import requests
import os, sys, stat
import csv
import grequests
#import urllib3
#from urllib3.poolmanager import PoolManager
#from requests_toolbelt.multipart.encoder import MultipartEncoder

class Script:
    """Send script config to server.
    """
    global COMPANYNAME
    global GATEWAY_ID
    COMPANYNAME = 'Acme'
    GATEWAY_ID = 'Tahoe'

    def __init__(self, config, name, instrument_ivi_type):
        self.config = config
        self.name = name
        self.instrument_ivi_type = instrument_ivi_type

    def transmit_config(self):
        config = self.config
        name = self.name
        instrument_ivi_type = self.instrument_ivi_type
        print(config)
        config['key_name'] = name
        config['instrument_ivi_type'] = instrument_ivi_type
        out = json.dumps(config)
        url = "http://localhost:18080/scriptconfig"
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=out, headers=headers)
        print("r.reason=",r.reason)
        print("r.status_code=",r.status_code)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
















