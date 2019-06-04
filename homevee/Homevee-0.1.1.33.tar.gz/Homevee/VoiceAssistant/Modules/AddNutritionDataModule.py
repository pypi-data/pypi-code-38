#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import re

from Homevee.Helper import Logger
from Homevee.Manager.NutritionDataManager import NutritionDataManager
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Helper import set_context
from Homevee.VoiceAssistant.Modules import VoiceModule

MAX_PORTION_DEVIATION = 10

class VoiceAddNutritionDataModule(VoiceModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['ich', ['gegessen', 'essen', 'esse', 'getrunken', 'trinke', 'trink']]
        ]

    def get_label(self):
        return "addnutrition"

    def get_context_key(self):
        return "CONTEXT_ADD_NUTRITION"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.voice_add_nutrition_item(username, text, context, db)

    def voice_add_nutrition_item(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        answer = "add_nutrition_item"

        text = re.sub(r'([\d]+)g', '\1 Gramm', text)

        Logger.log(text)

        words = text.split(" ")

        number_words = ['ein', 'einer', 'eine', 'einem', 'einen']

        amount_words = ['gramm', 'milliliter', 'kilo', 'kilogramm', 'liter', 'stück', 'scheiben', 'scheibe', 'brötchen']

        eat_words = ['esse', 'gegessen', 'essen', 'ess', 'trink', 'trinke', 'trinken', 'getrunken']

        time_words = ['jetzt', 'gerade', 'eben']

        daytime_words = ['morgens', 'morgen', 'mittag', 'mittags', 'abend', 'abends', 'snack', 'snacks', 'zwischendurch']

        is_name = False

        item = None

        amount = None
        amount_type = None

        daytime = None

        current_hour = datetime.datetime.now().hour

        for word in words:
            if(word in time_words):
                daytime = 'snacks'
                if current_hour >= 5 and current_hour < 10:
                    daytime = 'morning'
                elif current_hour >= 11 and current_hour < 13:
                    daytime = 'noon'
                elif current_hour >= 17 and current_hour < 19:
                    daytime = 'evening'

            if(word in daytime_words and daytime is None):
                if word in ['morgens', 'morgen']:
                    daytime = 'morning'
                elif word in ['mittag', 'mittags']:
                    daytime = 'noon'
                elif word in ['abends', 'abend']:
                    daytime = 'evening'
                elif word in ['snack', 'snacks', 'zwischendurch']:
                    daytime = 'snacks'

            if is_name and word in eat_words:
                is_name = False

            if is_name:
                if item is None:
                    item = word
                else:
                    item = item + " " +word

            if word in number_words:
                is_name = True
                amount = 1

            if word in amount_words:
                amount = words[words.index(word)-1]
                amount_type = word
                is_name = True

        Logger.log(str(item)+" => "+str(amount)+" => "+str(amount_type)+" => "+str(daytime))

        nutrition_data = None

        if(context is not None):

            if('query' in context):
                if(context['query'] == 'amount'):
                    for word in words:
                        if word in number_words:
                            amount = 1
                            break

                    if amount is None:
                        numbers_in_text = [int(s) for s in text.split() if s.isdigit()]

                        if (len(numbers_in_text) != 0):
                            amount = numbers_in_text[0]
                elif(context['query'] == 'item'):
                    item = text
                elif(context['query'] == 'daytime'):
                    for word in words:
                        if (word in daytime_words and daytime is None):
                            if word in ['morgens', 'morgen']:
                                daytime = 'morning'
                            elif word in ['mittag', 'mittags']:
                                daytime = 'noon'
                            elif word in ['abends', 'abend']:
                                daytime = 'evening'
                            elif word in ['snack', 'snacks', 'zwischendurch']:
                                daytime = 'snacks'

            if daytime is None and 'daytime' in context and context['daytime'] is not None:
                daytime = context['daytime']

            if amount is None and 'amount' in context and context['amount'] is not None:
                amount = context['amount']

            if amount_type is None and 'amount_type' in context and context['amount_type'] is not None:
                amount_type = context['amount_type']

            if nutrition_data is None and 'nutrition_data' in context and context['nutrition_data'] is not None:
                nutrition_data = context['nutrition_data']
                item = nutrition_data['name']

        #print "Amount: "+str(amount)

        if(item is not None):
            if(nutrition_data is None):
                nutrition_data = NutritionDataManager().get_nutrition_data(username, item, db)

            if(nutrition_data is None or nutrition_data is False):
                answer = "Zum Suchbegriff "+item+" wurden keine Einträge gefunden."
                return {'msg_speech': answer, 'msg_text': answer}

            date = datetime.datetime.today().strftime("%d.%m.%Y")

            if(amount is None):
                answer = "Wie viel " + nutrition_data['portionunit'] + " hast du von " + nutrition_data[
                    'name'] + " verzehrt?"
                context = {'nutrition_data': nutrition_data, 'amount': amount, 'amount_type': amount_type,
                           'daytime': daytime, 'query': 'amount'}
                set_context(username, self.get_context_key(), context, db)
            elif(daytime is None):
                answer = "Wann hast du " + nutrition_data['name'] + " verzehrt? Morgens, Mittags, Abends oder zwischendurch?"
                context = {'nutrition_data': nutrition_data, 'amount': amount, 'amount_type': amount_type,
                           'daytime': daytime, 'query': 'daytime'}
                set_context(username, self.get_context_key(), context, db)
            else:
                #print "amount: "+str(amount)
                portion_deviation = float(amount) / float(nutrition_data['portionsize'])

                #print portion_deviation

                if(portion_deviation >= MAX_PORTION_DEVIATION or portion_deviation <= 1.0/float(MAX_PORTION_DEVIATION)):
                    #invalid portion size

                    answer = "Wie viel "+nutrition_data['portionunit']+" hast du von "+nutrition_data['name']+" verzehrt?"
                    context = {'nutrition_data': nutrition_data, 'amount': amount, 'amount_type': amount_type, 'daytime': daytime, 'query': 'amount'}
                    set_context(username, self.get_context_key(), context, db)
                else:
                    #anhand der aktuellen uhrzeit die daytime errechnen

                    answer = "Ok, " + str(amount) + " " + nutrition_data['portionunit'] + " "+ nutrition_data['name'] +" wurde deinem Ernährungstagebuch hinzugefügt."

                    NutritionDataManager().add_edit_user_day_nutrition_item(username, None, date, daytime, nutrition_data['name'], amount,
                                                 nutrition_data['portionsize'], nutrition_data['portionunit'],
                                                 nutrition_data['calories'], nutrition_data['fat'], nutrition_data['saturated'],
                                                 nutrition_data['unsaturated'], nutrition_data['carbs'], nutrition_data['sugar'],
                                                 nutrition_data['protein'], db)

                    calories_left = NutritionDataManager().get_user_nutrition_overview(username, db)['data']['nutrition_day_data']['calories_left']

                    if (calories_left >= 0):
                        answer = answer + ' Du hast heute noch ' + str(calories_left) + ' Kalorien übrig.'
                    else:
                        answer = answer + ' Du bist heute ' + str(-1*calories_left) + ' Kalorien über deinem Ziel.'
        else:
            answer = "Was möchtest du deinem Ernährungstagebuch hinzufügen?"
            context = {'amount': amount, 'amount_type': amount_type, 'daytime': daytime, 'query': 'item'}
            set_context(username, self.get_context_key(), context, db)

        #determine amount

        #determine product

        return {'msg_speech': answer, 'msg_text': answer}