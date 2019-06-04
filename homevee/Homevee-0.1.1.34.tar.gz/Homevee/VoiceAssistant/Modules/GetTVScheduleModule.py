#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Modules import VoiceModule


class VoiceGetTvScheduleModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['was',['kommt','ist','gibt','läuft'],['tv','fernsehen','fernseher']]
        ]

    def get_label(self):
        return "gettvschedule"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.get_tv(username, text, context, db)

    def get_tv(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return {'msg_speech':'TV-Programm', 'msg_text':'TV-Programm'}