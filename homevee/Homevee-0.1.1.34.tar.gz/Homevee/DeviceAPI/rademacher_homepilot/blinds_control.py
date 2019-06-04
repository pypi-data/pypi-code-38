#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib.error
import urllib.parse
import urllib.request

from Homevee.Helper import Logger
from Homevee.Item.Gateway import *
from Homevee.Item.Status import *


def control_blinds(id, goto, db: Database = None):
    if db is None:
        db = Database()
    gateway = Item.load_from_db(Gateway, RADEMACHER_HOMEPILOT)

    url = "http://"+gateway.ip+"/deviceajax.do?cid=9&did="+str(id)+"&goto="+str(goto)+"&command=0"

    Logger.log(url)

    response = urllib.request.urlopen(url).read()

    data = json.loads(response)

    if(data['status'] != 'uisuccess'):
        return Status(type=STATUS_ERROR).get_dict()

    Logger.log(response)

    db.update("UPDATE HOMEPILOT_BLIND_CONTROL SET LAST_POS = :pos WHERE ID == :id",
                {'pos': goto, 'id': id})
    return Status(type=STATUS_OK).get_dict()