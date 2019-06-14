#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Modules import VoiceModule

class VoiceCalculatorModule(VoiceModule):
    def calculator(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return {'msg_speech':"Taschenrechner", 'msg_text':"Taschenrechner"}

    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['wie', 'viel',['ist','ergibt']],
            ['was',['ist','ergibt']]
        ]

    def get_label(self):
        return "calculator"

    def get_context_key(self):
        return "CONTEXT_CALCULATOR"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.calculator(username, text, context, db)