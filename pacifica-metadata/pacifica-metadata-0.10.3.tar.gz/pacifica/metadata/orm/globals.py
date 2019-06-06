#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Globals module for orm module."""
from playhouse.db_url import connect
from ..config import get_config

DB = connect(get_config().get('database', 'peewee_url'))
