#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from Homevee.Manager.CalendarManager import CalendarManager
from Homevee.VoiceAssistant.Helper import *
from Homevee.VoiceAssistant.Modules.CalendarModule import VoiceCalendarModule


class VoiceGetCalendarModule(VoiceCalendarModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['was', 'steht', 'an'],
            ['was', 'habe', 'ich', 'vor'],
            ['habe', 'ich', 'termine']
        ]

    def get_label(self):
        return "getcalendar"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.get_calendar(username, text, context, db)

    def get_calendar(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        # find date

        date_word, date = self.find_date(text)

        # date = "2018-05-23"

        calendar_entries = CalendarManager().get_calendar_day_items(username, date, db)['calendar_entries']

        entries = []

        for entry in calendar_entries:
            start = datetime.datetime.strptime(entry['start'], '%H:%M')
            dnow = datetime.datetime.now()

            if (dnow.time() > start.time()):
                continue

            entries.append(entry)

        if len(entries) > 0:
            calendar_string = None

            for i in range(0, len(entries)):
                if calendar_string is None:
                    calendar_string = entry['name'] + ' um ' + entry['start'] + ' Uhr'
                elif i == len(entries):
                    calendar_string = ' und ', entry['name'] + ' um ' + entry['start'] + ' Uhr'
                else:
                    calendar_string += ', ' + entry['name'] + ' um ' + entry['start'] + ' Uhr'

            if len(entries) > 1:
                answer_data = [
                    ['Du hast ', date_word, ' ', len(entries), ' ',
                     ['Termine', 'Kalendereinträge', 'Einträge im Kalender'], ': ',
                     calendar_string]
                ]
            else:
                answer_data = [
                    ['Du hast ', date_word, ' einen', ' ', ['Termin', 'Kalendereintrag', 'Eintrag im Kalender'], ': ',
                     calendar_string]
                ]
        else:
            answer_data = [
                ['Du hast ', date_word, ' keine ', ' ', ['Termine', 'Kalendereinträge', 'Einträge im Kalender'], '.']
            ]

        output = generate_string(answer_data)

        return {'msg_speech': output, 'msg_text': output}