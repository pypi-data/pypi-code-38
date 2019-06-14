#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from Homevee.Item.Status import *
from Homevee.Utils.Database import Database


class VoiceReplaceManager:
    def __init__(self):
        return

    def get_voice_replace_items(self, user, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            return Status(type=STATUS_NO_ADMIN).get_dict()

        replace_data = []

        results = db.select_all("SELECT DISTINCT REPLACE_WITH FROM VOICE_COMMAND_REPLACE WHERE USERNAME = :user",
                    {'user': user.username})

        for item in results:
            items = db.select_all("SELECT TEXT FROM VOICE_COMMAND_REPLACE WHERE REPLACE_WITH == :item AND USERNAME = :user",
                {'user': user.username, 'item': item['REPLACE_WITH']})

            replacements = []

            for replacement in items:
                replacements.append(replacement['TEXT'])

            replace_data.append({'replacewith': item['REPLACE_WITH'], 'replacearray': replacements})

        return replace_data

    def add_edit_voice_replace_item(self, user, replacewith, replaceitems, db: Database = None) -> bool:
        if db is None:
            db = Database()
        replaceitems = json.loads(replaceitems)

        try:
            db.delete("DELETE FROM VOICE_COMMAND_REPLACE WHERE REPLACE_WITH = :replacewith AND USERNAME = :user",
                        {'replacewith': replacewith, 'user': user.username})

            for item in replaceitems:
                db.insert("INSERT INTO VOICE_COMMAND_REPLACE (USERNAME, REPLACE_WITH, TEXT) VALUES (:user, :replacewith, :text)",
                            {'user': user.username, 'replacewith': replacewith, 'text': item})
            return True
        except:
            return False

    def delete_voice_replace_item(self, user, replacewith, db: Database = None) -> bool:
        if db is None:
            db = Database()
        return db.delete("DELETE FROM VOICE_COMMAND_REPLACE WHERE REPLACE_WITH = :replacewith AND USERNAME = :user",
                    {'replacewith': replacewith, 'user': user.username})