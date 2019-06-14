#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import urllib.error
import urllib.error
import urllib.parse
import urllib.parse
import urllib.request
import urllib.request

from Homevee.Helper import Logger
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant import Helper
from Homevee.VoiceAssistant.Modules import VoiceModule


class VoiceGetActivitiesModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            [['mir', 'uns'], 'ist', 'langweilig'],
            ['was', ['kann', 'können'], ['ich', 'wir'], ['tun', 'machen', 'unternehmen']]
        ]

    def get_label(self):
        return "activity"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.get_activities(username, text, context, db)

    def get_activities(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        try:
            url = Helper.SMART_API_PATH + "/?action=activity&text=" + urllib.parse.quote(text.encode('utf8'))
            Logger.log(url)

            response = urllib.request.urlopen(url)
            data = response.read()

            data = data.decode('utf-8')

            if data is not None:
                return {'msg_speech': data, 'msg_text': data}
            else:
                output = self.get_error()
        except urllib.error.HTTPError as e:
            output = self.get_error()

        return {'msg_speech': output, 'msg_text': output}

    def get_error(self):
        return random.choice([
            'Mir fällt gerade nichts ein, was du tun könntest.'
        ])