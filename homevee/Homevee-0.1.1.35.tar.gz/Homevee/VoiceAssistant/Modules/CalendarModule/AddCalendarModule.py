#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Modules.CalendarModule import VoiceCalendarModule


class VoiceAddCalendarModule(VoiceCalendarModule):
    def get_context_key(self):
        return "VOICE_ADD_CALENDAR"

    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['erinnere', 'mich']
        ]

    def get_label(self):
        return "addcalendar"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.add_calendar(username, text, context, db)

    def add_calendar(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return {'msg_speech': 'Add Calendar', 'msg_text': 'Add Calendar'}