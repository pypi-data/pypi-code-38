#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Helper import generate_string
from Homevee.VoiceAssistant.Modules.ShoppingListModule import VoiceShoppingListModule


class VoiceGetShoppingListModule(VoiceShoppingListModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            ['was', ['steht', 'ist'], ['einkaufszettel', 'einkaufsliste']],
            ['was', ['muss', 'soll'], 'kaufen'],
            ['wie', ['viel', 'viele'], ['muss', 'soll'], 'kaufen']
        ]

    def get_label(self):
        return "addshoppinglist"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.get_shopping_list(username, text, context, db)

    def get_shopping_list(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        items = self.find_items(text, db)

        if len(items) is 0:
            # Ganze Liste abfragen
            items = self.get_shopping_list(username, db)['items']

        data = [
            [['Das ', 'Folgendes '], 'steht ', 'auf ',
             [[['der ', 'deiner '], 'Einkaufsliste'], [['dem ', 'deinem '], 'Einkaufszettel']], ': '],
            [['Diese ', 'Folgende '], ['Artikel ', 'Produkte '], ['stehen ', 'sind '], 'auf ',
             [[['der ', 'deiner '], 'Einkaufsliste'],
              [['dem ', 'deinem '], 'Einkaufszettel']], ': ']
        ]

        output = generate_string(data)

        for i in range(0, len(items)):
            item = items[i]

            if len(items) > 1:
                # Mehr als ein Element
                if i is len(items) - 1:
                    # Letztes Element
                    output = output + " und "
                elif i < len(items) - 1 and i > 0:
                    # Nicht erstes und nicht letztes Element
                    output = output + ", "

            amount_string = str(item['amount'])
            if(item['amount'] == 1):
                amount_string = "ein"

            output = output + amount_string + " mal " + item['item']

        output += "."

        return {'msg_speech': output, 'msg_text': output}

