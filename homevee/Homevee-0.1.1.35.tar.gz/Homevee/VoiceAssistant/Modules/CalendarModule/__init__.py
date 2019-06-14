#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import re

from Homevee.VoiceAssistant.Helper import *
from Homevee.VoiceAssistant.Modules import VoiceModule


class VoiceCalendarModule(VoiceModule):
    def find_date(self, text):
        now = datetime.datetime.now()

        try:
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

                ['.januar ', '.01.'],
                ['.februar ', '.02.'],
                ['.märz ', '.03.'],
                ['.april ', '.04.'],
                ['.mai ', '.05.'],
                ['.juni ', '.06.'],
                ['.juli ', '.07.'],
                ['.august ', '.08.'],
                ['.september ', '.09.'],
                ['.oktober ', '.10.'],
                ['.november ', '.11.'],
                ['.dezember ', '.12.'],
            ]

            for replacement in month_replacements:
                text = text.replace(replacement[0], replacement[1])

            date = re.search('\d{2}\.\d{2}\.\d{4}', text)
            date_formatted = datetime.datetime.strptime(date.group(), '%d.%m.%Y').date()

            return 'am ' + date_formatted.strftime("%d.%m.%Y"), date_formatted.strftime("%Y-%m-%d")
        except Exception as e:
            Logger.log("No date found")

            try:
                month_replacements = [
                    ['. januar ', '.01. '],
                    ['. februar ', '.02. '],
                    ['. märz ', '.03. '],
                    ['. april ', '.04. '],
                    ['. mai ', '.05. '],
                    ['. juni ', '.06. '],
                    ['. juli ', '.07. '],
                    ['. august ', '.08. '],
                    ['. september ', '.09. '],
                    ['. oktober ', '.10. '],
                    ['. november ', '.11. '],
                    ['. dezember ', '.12. '],

                    ['.januar ', '.01. '],
                    ['.februar ', '.02. '],
                    ['.märz ', '.03. '],
                    ['.april ', '.04. '],
                    ['.mai ', '.05. '],
                    ['.juni ', '.06. '],
                    ['.juli ', '.07. '],
                    ['.august ', '.08. '],
                    ['.september ', '.09. '],
                    ['.oktober ', '.10. '],
                    ['.november ', '.11. '],
                    ['.dezember ', '.12. '],
                ]

                for replacement in month_replacements:
                    text = text.replace(replacement[0], replacement[1])

                date = re.search('\d{2}\.\d{2}\.', text)
                date_formatted = datetime.datetime.strptime(date.group()+str(datetime.datetime.now().year), '%d.%m.%Y').date()

                return 'am ' + date_formatted.strftime("%d.%m.%Y"), date_formatted.strftime("%Y-%m-%d")
            except Exception as e:
                Logger.log("Date without year also not found")

        words = text.split()

        if "heute" in words:
            return 'heute', now.strftime("%Y-%m-%d")
        if "morgen" in words:
            return 'morgen', (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        if "übermorgen" in words:
            return 'übermorgen', (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")

        #when no date was found return today
        return 'heute', now.strftime("%Y-%m-%d")