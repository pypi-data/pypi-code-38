#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from Homevee.Item.Status import *
from Homevee.Utils.Database import Database


def get_voice_replace_items(user, db: Database = None):
    if db is None:
        db = Database()
    if not user.has_permission("admin"):
        return Status(type=STATUS_NO_ADMIN).get_dict()

    replace = []

    results = db.select_all("SELECT DISTINCT REPLACE_WITH FROM VOICE_COMMAND_REPLACE WHERE USERNAME = :user",
                {'user': user.username})

    for item in results:
        items = db.select_all("SELECT TEXT FROM VOICE_COMMAND_REPLACE WHERE REPLACE_WITH == :item AND USERNAME = :user",
            {'user': user.username, 'item': item['REPLACE_WITH']})

        replacements = []

        for replacement in items:
            replacements.append(replacement['TEXT'])

        replace.append({'replacewith': item['REPLACE_WITH'], 'replacearray': replacements})

    return {'replacedata': replace}

def add_edit_voice_replace_item(user, replacewith, replaceitems, db: Database = None):
    if db is None:
        db = Database()
    replaceitems = json.loads(replaceitems)

    db.delete("DELETE FROM VOICE_COMMAND_REPLACE WHERE REPLACE_WITH = :replacewith AND USERNAME = :user",
                {'replacewith': replacewith, 'user': user.username})

    for item in replaceitems:
        db.insert("INSERT INTO VOICE_COMMAND_REPLACE (user, REPLACE_WITH, TEXT) VALUES (:user, :replacewith, :text)",
                    {'user': user.username, 'replacewith': replacewith, 'text': item})

    return Status(type=STATUS_OK).get_dict()

def delete_voice_replace_item(user, replacewith, db: Database = None):
    if db is None:
        db = Database()
    db.delete("DELETE FROM VOICE_COMMAND_REPLACE WHERE REPLACE_WITH = :replacewith AND USERNAME = :user",
                {'replacewith': replacewith, 'user': user.username})
    return Status(type=STATUS_OK).get_dict()