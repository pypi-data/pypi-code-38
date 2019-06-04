#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import requests

from Homevee.Item import Item
from Homevee.Item.Gateway import Gateway, Z_WAVE_GATEWAY
from Homevee.Utils.Database import Database


def do_zwave_request(path, db: Database = None):
    if db is None:
        db = Database()
    try:
        gateway = Item.load_from_db(Gateway, Z_WAVE_GATEWAY, db)
        port = ""
        if (gateway.port != None and gateway.port != ""):
            port = ":" + str(gateway.port)

        url = "http://" + gateway.key1 + ':' + gateway.key2 + '@' + gateway.ip + port + path

        #print url

        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        request = requests.get(url, headers=headers)
        data = request.content

        #print data

        json_data = json.loads(data)

        #print url, json_data

        return json_data
    except:
        return None