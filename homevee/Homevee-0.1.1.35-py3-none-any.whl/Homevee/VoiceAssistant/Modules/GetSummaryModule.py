#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Modules import VoiceModule

class VoiceGetSummaryModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        #todo declare pattern for summary
        return []

    def get_label(self):
        return "getsummary"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        pass

    def get_voice_summary(username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return {'msg_speech': 'Get Summary', 'msg_text': 'Get Summary'}