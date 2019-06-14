#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from Homevee.Helper import Logger
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Helper import generate_string
from Homevee.VoiceAssistant.Modules import VoiceModule

MIN_OUTPUT_LENGTH = 100

class VoiceGetWikipediaDefinitionModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            [['wer', 'was'], ['ist', 'war']]
        ]

    def get_label(self):
        return "getwikipediadefinition"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.voice_definition(username, text, context, db)

    def voice_definition(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        words = text.split(" ")

        definition = []

        query = None

        is_query = False

        for word in words:
            if is_query:
                if query is None:
                    query = word.capitalize()
                else:
                    query = query + " " + word.capitalize()

            if word == "ist" or word == "war":
                is_query = True

        url = 'https://de.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles='+query.replace(" ", "%20")
        response = urllib.request.urlopen(url).read()

        Logger.log(url)
        Logger.log(response)

        data = json.loads(response)

        pages = data['query']['pages']

        page_keys = list(pages.keys())[0]

        if 'extract' in pages[page_keys]:
            definition = pages[page_keys]['extract']

        if  page_keys == -1 or len(definition) == 0:
            answers = [
                ['Ich habe ', ['zu ', 'über '], query, ' ' , ['leider ', 'bedauerlicherweise ', ''], [[['gar ', ''], 'nichts '], 'keine Ergebnisse '], ['gefunden', 'finden können'], '.']
            ]

            output = generate_string(answers)
            return {'msg_speech': output, 'msg_text': output}

        definition = definition.replace('[[', '')
        definition = definition.replace(']]', '')
        definition = definition.replace('\n', '')

        definition = re.sub("\s*[\(\[].*?[\)\]]\s*", " ", definition)
        definition = re.sub("\s+", " ", definition)

        #definition = re.sub('#\s*\(.+\)\s*#U', ' ', definition)
        #definition = re.sub('#\s*\[.+\]\s*#U', ' ', definition)

        sentences = definition.split('. ')

        output = sentences[0]

        last_char = output[-1:]

        index = 1
        if len(sentences) > 1:
            while self.is_number(last_char) or len(output) < MIN_OUTPUT_LENGTH:
                output = output + '. ' + sentences[index]
                index = index + 1
                last_char = output[-1:]

        if not output.endswith("."):
            output = output + "."

        return {'msg_speech': output, 'msg_text': output}