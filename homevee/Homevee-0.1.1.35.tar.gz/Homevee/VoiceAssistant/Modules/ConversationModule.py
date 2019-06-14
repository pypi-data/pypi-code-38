#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
import urllib.error
import urllib.error
import urllib.parse
import urllib.parse
import urllib.request
import urllib.request

from Homevee.Helper import translations, Logger
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant import Helper
from Homevee.VoiceAssistant.Helper import generate_string
from Homevee.VoiceAssistant.Modules import VoiceModule

GREETINGS = ['hallo', 'hey', 'na', 'hi']

THANKS = ['danke', 'dank', 'dankeschön']

class VoiceConversationModule(VoiceModule):
    def get_context_key(self):
        return "VOICE_CONVERSATION"

    def get_priority(self):
        return 0

    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return []

    def get_label(self):
        return "conversation"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        Logger.log("conversation: "+text)
        return self.conversation(username, text, context, db)

    def conversation(self, username, text, context, db: Database = None):
        try:
            if db is None:
                db = Database()
            url = Helper.SMART_API_PATH + "/?action=plaintext&language=" + translations.LANGUAGE + "&text=" + urllib.parse.quote(codecs.encode(text, 'utf-8'))
            Logger.log("calling: "+url)
            output = urllib.request.urlopen(url).read()

            #print(url)

            #print(output)

            if output is None or output == '' or len(output)==0:
                data = [
                    [[['Es ', 'tut '], 'Tut '], 'mir ', ['echt ', 'sehr ', ''], ['Leid. ', 'Leid, '+username+'. '],
                    ['Da ', 'Dabei ', 'Damit '], 'kann ', 'ich ', 'dir ', ['leider ', ''], ['noch ', ''], 'nicht ', ['helfen', 'weiterhelfen'], '.']
                ]
                output = generate_string(data)
            else:
                output = output.decode("utf-8")

            result = {'msg_speech': output, 'msg_text': output}

            return result
        except:
            output = "Ich habe gerade Verbindungsprobleme und kann deine Anfrage gerade leider nicht bearbeiten."
            result = {'msg_speech': output, 'msg_text': output}
            return result


    def contains(self, text, array):
        words = text.split(' ')

        for item in array:
            if item in words:
                return True

        return False