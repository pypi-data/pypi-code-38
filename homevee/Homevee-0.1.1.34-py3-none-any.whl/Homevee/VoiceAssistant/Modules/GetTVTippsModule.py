#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Manager.TVPlanManager import TVPlanManager
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant import Helper
from Homevee.VoiceAssistant.Modules import VoiceModule


class VoiceGetTvTippsModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            [['was', 'welche'], 'sind', ['tv-tipps', 'tvtipps', 'tv-tips', 'tvtips']],
            [['was', 'welche'], 'sind', ['tv', 'fernseh'], ['tipps', 'tips']],
            [['was', 'welche'], 'sind', ['fernseh-tipps', 'fernsehtipps', 'fernseh-tips', 'fernsehtips']],
        ]

    def get_label(self):
        return "gettvtipps"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.get_tv_tipps(username, text, context, db)

    def get_tv_tipps(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        tv_shows = TVPlanManager().get_tv_plan(username, "tipps", db)

        VERB = ['kommt', 'läuft']

        show_strings = []
        for show in tv_shows:
            TIME = show['time'] + ' Uhr'
            CHANNEL = show['channel']
            NAME = '\''+show['name']+'\''

            string_data = [
                ['um ', TIME, ' ', VERB, ' auf ', CHANNEL,  ' ', NAME],
                ['um ', TIME, ' ', VERB, ' ', NAME, ' auf ', CHANNEL],
                ['auf ', CHANNEL, ' um ', TIME, ' ', VERB, ' ', NAME],
                ['auf ', CHANNEL, ' ', VERB, ' ', NAME, ' um ', TIME],
                [NAME, ' ', VERB, ' um ', TIME, ' auf ', CHANNEL],
                [NAME, ' ', VERB, ' auf ', CHANNEL, ' um ', TIME],
            ]

            show_strings.append(Helper.generate_string(string_data))

        show_string = None
        for i in range(0, len(show_strings)):
            if show_string is None:
                show_string = show_strings[i]
            elif i == len(show_strings)-1:
                if i != 0:
                    show_string = show_string + ' und '
                show_string = show_string+show_strings[i]
            else:
                show_string = show_string+', '+show_strings[i]

        answer_data = [
            [['Die', 'Deine'], ' ', ['TV', 'Fernseh', 'Programm'], '-', ['Tipps', 'Vorschläge', 'Empfehlungen'], ' ',
                ['heute', 'für heute'], ' ', ['sind', 'lauten'], ':']
        ]

        output = Helper.generate_string(answer_data) + ' ' + show_string + '.'

        return {'msg_speech': output, 'msg_text': output}