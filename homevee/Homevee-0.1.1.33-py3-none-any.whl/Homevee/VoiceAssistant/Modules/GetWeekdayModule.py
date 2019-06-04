#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import re

from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Helper import generate_string
from Homevee.VoiceAssistant.Modules import VoiceModule


class VoiceGetWeekdayModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['was', 'ist', 'für', ['tag', 'wochentag']]
        ]

    def get_label(self):
        return "getweekday"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.get_weekday(username, text, context, db)

    def get_weekday(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        wochentage = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

        month_replacements = [
            ['. januar ', '.01.'],
            ['. februar ', '.02.'],
            ['. märz ', '.03.'],
            ['. april ', '.04.'],
            ['. mai ', '.05.'],
            ['. juni ', '.06.'],
            ['. juli ', '.07.'],
            ['. august ', '.08.'],
            ['. september ', '.09.'],
            ['. oktober ', '.10.'],
            ['. november ', '.11.'],
            ['. dezember ', '.12.'],
        ]

        for replacement in month_replacements:
            text = text.replace(replacement[0], replacement[1])

        date = re.search('\d{2}\.\d{2}\.\d{4}', text)
        if(date is None):
            answer_data = [
                ['Du hast kein Datum ', ['gesagt', 'genannt'],'.'],
                ['Du musst', [' mir ', ' '], ['zuerst', 'erst', 'erst einmal'], ' ein Datum ', ['nennen', 'sagen'], '.']
            ]

            output = generate_string(answer_data)
        else:
            date_formatted = str(datetime.datetime.strptime(date.group(), '%d.%m.%Y').date())

            date_data = date_formatted.split('-')
            time = datetime.datetime(int(date_data[0]), int(date_data[1]), int(date_data[2]))
            wochentag = wochentage[time.weekday()]

            answer_data = [
                [[['Der ', date_formatted], 'Das'], ' ist ein ', wochentag, [', '+username, ''], '.']
            ]

            output = generate_string(answer_data)

        return {'msg_speech': output, 'msg_text': output}