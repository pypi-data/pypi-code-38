#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Manager.NutritionDataManager import NutritionDataManager
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Modules import VoiceModule

MAX_PORTION_DEVIATION = 10

class VoiceGetNutritionInfoModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['wie', ['viel', 'viele'], ['fett', 'kalorien', 'kohlenhydrate', 'eiweiß', 'protein', 'zucker'], ['hat', 'ist', 'haben', 'sind']]
        ]

    def get_label(self):
        return "getnutritioninfo"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.voice_get_nutrition_info(username, text, context, db)

    def voice_get_nutrition_info(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        words = text.split(" ")

        number_words = ['ein', 'einer', 'eine', 'einem', 'einen']

        if 'in' in words:
            in_index = words.index('in')
            del words[in_index]

            index = None

            for number_word in number_words:
                if number_word in words:
                    index = words.index(number_word)

            if index is not None:
                del words[index]

        nutrition_types = ['fett', 'eiweiß', 'protein', 'kohlenhydrate', 'kalorien', 'zucker', 'proteine']

        nutrition_value = None

        for word in words:
            if word in nutrition_types:
                nutrition_value = word
                break

        if nutrition_value is None:
            return {'msg_speech': 'Es gab einen Fehler.',
                    'msg_text': 'Es gab einen Fehler.'}

        item = None
        trigger = ['ist', 'sind', 'haben', 'hat']
        add_word = False
        add_word_index = None
        amount_type = None
        amount = None
        for i in range(0, len(words)):
            word = words[i]

            if add_word_index is not None and i == add_word_index:
                add_word = True

            if add_word:
                if word in number_words:
                    continue

                if item is None:
                    item = word
                else:
                    item = item + " " + word
                continue

            if word in trigger:
                if 'gramm' in words:
                    index = words.index('gramm')
                    amount_type = 'gramm'
                elif 'kili' in words:
                    index = words.index('kilo')
                    amount_type = 'kilo'
                elif 'milliliter' in words:
                    index = words.index('milliliter')
                    amount_type = 'milliliter'
                elif 'liter' in words:
                    index = words.index('liter')
                    amount_type = 'liter'
                else:
                    add_word = True
                    continue

                amount = words[index - 1]
                add_word_index = index + 1

        answer = ""

        # Daten abfragen
        nutrition_data = NutritionDataManager().get_nutrition_data(username, item, db)

        #print nutrition_data

        if nutrition_data is not None:
            if nutrition_data is not False:
                portionsize = nutrition_data['portionsize']

                if portionsize == 1:
                    portionsize_string = "Ein"
                else:
                    portionsize_string = str(portionsize)

                portion_string = portionsize_string + " " + nutrition_data['portionunit']

                name = nutrition_data['name']

                if (nutrition_value == "fett"):
                    value = nutrition_data['fat']
                    unit = "Gramm Fett"
                elif (nutrition_value in ['eiweiß', 'protein', 'proteine']):
                    value = nutrition_data['protein']
                    unit = "Gramm Eiweiß"
                elif (nutrition_value == "kohlenhydrate"):
                    value = nutrition_data['carbs']
                    unit = "Gramm Kohlenhydrate"
                elif (nutrition_value == "zucker"):
                    value = nutrition_data['sugar']
                    unit = "Gramm Zucker"
                elif (nutrition_value == "kalorien"):
                    value = nutrition_data['calories']
                    unit = "Kalorien"

                have_verb = "hat"

                if (portionsize > 1):
                    have_verb = "haben"

                answer = portion_string + " " + name + " " + have_verb + " " + str(value) + " " + unit + "."

                context_data = {'nutrition_type': nutrition_value}
                # set_context(username, 'nutrition', context_data, db)
            else:
                answer = "Es wurden keine Lebensmittel zum Suchbegriff "+item+" gefunden."

        else:
            #fehlermeldung ausgeben

            answer = "Die Nährwertdaten konnten nicht abgefragt werden."

        amount_text = ''
        if amount_type is not None and amount is not None:
            amount_text = ' => ' + amount + ' ' + amount_type

        return {'msg_speech': answer, 'msg_text': answer}