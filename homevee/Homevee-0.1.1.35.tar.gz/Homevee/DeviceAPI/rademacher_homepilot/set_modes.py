#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.error
import urllib.parse
import urllib.request

from Homevee.Item.Gateway import *


def set_modes(id, mode, db: Database = None):
    if db is None:
        db = Database()
    gateway = Item.load_from_db(Gateway, RADEMACHER_HOMEPILOT)

    url = "http://" + gateway.ip + "/deviceajax.do?cid=9&did=10001&goto=" + str(mode) + "&command=0"

    response = urllib.request.urlopen(url).read()