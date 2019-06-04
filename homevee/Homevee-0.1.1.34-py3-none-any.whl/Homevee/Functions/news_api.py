#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Utils.Database import Database


def get_news(user, db: Database = None):
    if db is None:
        db = Database()
    return []