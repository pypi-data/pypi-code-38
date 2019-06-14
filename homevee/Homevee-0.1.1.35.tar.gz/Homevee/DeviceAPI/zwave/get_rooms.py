#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import requests

from Homevee.Helper import Logger
from Homevee.Item import Item
from Homevee.Item.Gateway import Gateway, Z_WAVE_GATEWAY
from Homevee.Utils.Database import Database


def get_rooms():
    result = {}

    gateway = Item.load_from_db(Gateway, Z_WAVE_GATEWAY, Database())

    port = ""
    if (gateway.port != None and gateway.port != ""):
        port = ":" + str(gateway.port)

    url = "http://" + gateway.key1 + ':' + gateway.key2 + '@' + gateway.ip\
          + port + "/ZAutomation/api/v1/locations/"
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    request = requests.get(url, headers=headers)
    data = request.content

    Logger.log(data)

    result = json.loads(data)

    return result