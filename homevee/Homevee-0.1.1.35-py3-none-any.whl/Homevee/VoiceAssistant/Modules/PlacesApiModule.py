#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Modules import VoiceModule

class VoicePlacesApiModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            [['wo', 'was'], 'ist', ['der', 'die', 'das'], ['nähste', 'nächste']]
        ]

    def get_label(self):
        return "placesapi"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.get_places(username, text, context, db)

    def get_places(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return {'msg_speech': 'Places', 'msg_text': 'Places'}