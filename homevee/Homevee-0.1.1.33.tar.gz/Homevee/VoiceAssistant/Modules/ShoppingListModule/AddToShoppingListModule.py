#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Modules.ShoppingListModule import VoiceShoppingListModule


class VoiceAddToShoppingListModule(VoiceShoppingListModule):
    def get_pattern(self, db: Database = None):
        if db is None:
            db = Database()
        return [
            [['schreibe', 'setze'], ['auf', 'zur', 'in'], ['einkaufsliste','einkaufliste','einkaufszettel']]
        ]

    def get_label(self):
        return "getshoppinglist"

    def run_command(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        return self.add_to_shopping_list(username, text, context, db)

    def add_to_shopping_list(self, username, text, context, db: Database = None):
        if db is None:
            db = Database()
        '''words = text.split(" ")

        for i in range(0, len(words)):
            word = words[i]



        if item_count > 1:
            answer_data = [
                ['Ok']
            ]
        else:
            answer_data = [
                ['Ok']
            ]

        output = generate_string(answer_data)'''

        output = "Add Shopping List"

        return {'msg_speech': output, 'msg_text': output}

