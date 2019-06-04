#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from Homevee.Helper import Logger
from Homevee.Manager.NutritionDataManager import NutritionDataManager
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Helper import generate_string
from Homevee.VoiceAssistant.Modules import VoiceModule

MAX_PORTION_DEVIATION = 10

class VoiceGetNutritionDiaryModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['wie', ['viel', 'viele'], ['fett', 'kalorien', 'kohlenhydrate', 'eiweiß', 'protein', 'zucker'], ['ist', 'sind', 'habe'], ['übrig', 'offen', 'auf', 'erlaubt']],
            ['wie', ['viel', 'viele'], ['fett', 'kalorien', 'kohlenhydrate', 'eiweiß', 'protein', 'zucker'], ['darf', 'kann', 'soll', 'muss'], ['essen', 'trinken', 'verzehren', ['zu', 'mir', 'nehmen']]]
        ]

    def get_label(self):
        return "nutritiondiary"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.voice_query_nutrition_diary(username, text, context, db)

    def voice_query_nutrition_diary(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        words = text.split(" ")

        queried_value = None

        for word in words:
            if word == 'fett':
                queried_value = 'FAT'
            elif word == 'kalorien':
                queried_value = 'CALORIES'
            elif word == 'kohlenhydrate':
                queried_value = 'CARBS'
            elif word == 'zucker':
                queried_value = 'SUGAR'
            elif word in ['protein', 'proteine', 'eiweiß']:
                queried_value = 'PROTEIN'
            else:
                continue

            break

        user_profile = NutritionDataManager().get_user_fitness_profile(username, db)

        Logger.log(user_profile)

        if (user_profile is False):
            answer = "Du hast noch kein Profil für den Ernährungsmanager erstellt. Das kannst du in der App im Menüpunkt Ernährungsmanager tun."
        elif queried_value is None:
            #Kein Wert gefunden
            answer = "Welchen Nährwert möchtest du abfragen?"

            answer_data = [
                ['Welcher Nährwert soll abgefragt werden.'],
                ['Welchen Nährwert ', ['magst', 'möchtest', 'willst'],' du abfragen.'],
            ]
        else:

            results = db.select_all("SELECT * FROM NUTRITION_DATA WHERE USER = :user AND DATE = :date",
                        {'user': username, 'date': datetime.datetime.today().strftime("%d.%m.%Y")})

            eaten_queried_value_today = 0

            for item in results:
                amount = (float(item['EATEN_PORTION_SIZE']) / float(item['PORTIONSIZE']))

                eaten_queried_value_today += item[queried_value] * amount

            unit = None

            if queried_value == 'FAT':
                value_left = user_profile['fatgoal']-eaten_queried_value_today
                unit = "Gramm Fett"
            elif queried_value == 'CALORIES':
                value_left = int(user_profile['caloriesgoal']-eaten_queried_value_today)
                eaten_queried_value_today = int(eaten_queried_value_today)
                unit = 'Kalorien'
            elif queried_value == 'CARBS':
                value_left = user_profile['carbsgoal']-eaten_queried_value_today
                unit = 'Gramm Kohlenhydrate'
            elif queried_value == 'SUGAR':
                value_left = user_profile['sugargoal']-eaten_queried_value_today
                unit = 'Gramm Zucker'
            elif queried_value == 'PROTEIN':
                value_left = user_profile['proteingoal']-eaten_queried_value_today
                unit = 'Gramm Protein'

            answer_data = [
                ['Du hast heute ', ['schon', 'bereits'], ' ', str(eaten_queried_value_today), " ", unit, ' ',
                 ['gegessen', 'verzehrt', 'aufgenommen', 'zu dir genommen'], ' und ', ['noch', 'weitere'], ' ',
                 str(value_left), ' ', unit, ' ', ['übrig', 'frei', 'offen'], '.']
            ]

            #answer = "Du hast heute schon "+str(eaten_queried_value_today)+" "+unit+" zu dir genommen und noch "+str(value_left)+" "+unit+" übrig."

        answer = generate_string(answer_data)

        return {'msg_speech': answer, 'msg_text': answer}