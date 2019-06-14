#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from Homevee.Manager.ControlManager.ActionManager import ActionManager
from Homevee.Utils.Database import Database


class CustomVoiceCommandManager():
    def __init__(self):
        return

    def get_voice_commands(self, db):
        commands = []
        results = db.select_all("SELECT * FROM CUSTOM_VOICE_COMMANDS", {})

        for item in results:
            command_data = self.get_command_data(item['ID'], db)

            responses = self.get_response_data(item['ID'], db)

            commands.append({'id': item['ID'], 'name': item['NAME'], 'action_data': item['ACTION_DATA'],
                          'command_data': command_data,
                             'response_data': responses})

        return commands

    def get_command_data(self, id, db: Database = None):
        if db is None:
            db = Database()
        items = db.select_all("SELECT * FROM CUSTOM_VOICE_COMMAND_SENTENCES WHERE COMMAND_ID = :id", {'id': id})

        data = []

        for item in items:
            data.append(item['COMMAND'])

        return data

    def get_response_data(self, id, db: Database = None):
        if db is None:
            db = Database()
        items = db.select_all("SELECT * FROM CUSTOM_VOICE_COMMAND_RESPONSES WHERE COMMAND_ID = :id", {'id': id})

        data = []

        for item in items:
            data.append(item['RESPONSE'])

        return data

    def add_edit_voice_command(self, username, id, name, command_data, response_data, action_data, db: Database = None):
        if db is None:
            db = Database()
        add_new = (id == None or id == "" or id == "-1")

        if(add_new):
            id = db.insert("INSERT INTO CUSTOM_VOICE_COMMANDS (NAME, ACTION_DATA) VALUES (:name, :actions)",
                        {'name': name, 'actions': action_data})

            command_data = json.loads(command_data)
            self.add_command_data(command_data, id, db)

            response_data = json.loads(response_data)
            self.add_response_data(response_data, id, db)
        else:
            db.update("UPDATE AUTOMATION_DATA SET NAME = :name, ACTION_DATA = :actions WHERE ID = :id",
                {'name': name, 'actions': action_data, 'id': id})

            db.delete("DELETE FROM CUSTOM_VOICE_COMMAND_SENTENCES WHERE COMMAND_ID = :id", {'id': id})
            db.delete("DELETE FROM CUSTOM_VOICE_COMMAND_RESPONSES WHERE COMMAND_ID = :id", {'id': id})

            command_data = json.loads(command_data)
            self.add_command_data(command_data, id, db)

            response_data = json.loads(response_data)
            self.add_response_data(response_data, id, db)

    def delete_voice_command(self, username, id, db: Database = None):
        if db is None:
            db = Database()
        db.delete("DELETE FROM CUSTOM_VOICE_COMMANDS WHERE ID = :id", {'id': id})
        db.delete("DELETE FROM CUSTOM_VOICE_COMMAND_RESPONSES WHERE COMMAND_ID = :id", {'id': id})
        db.delete("DELETE FROM CUSTOM_VOICE_COMMAND_SENTENCES WHERE COMMAND_ID = :id", {'id': id})

    def add_command_data(self, commands, id, db: Database = None):
        if db is None:
            db = Database()
        for command in commands:
            param_array = {'id': id, 'command': command.lower()}

            db.insert("""INSERT INTO CUSTOM_VOICE_COMMAND_SENTENCES (COMMAND_ID, COMMAND) VALUES (:id, :command)""",
                param_array)

    def add_response_data(self, responses, id, db: Database = None):
        if db is None:
            db = Database()
        for response in responses:
            param_array = {'id': id, 'response': response}

            db.insert("""INSERT INTO CUSTOM_VOICE_COMMAND_RESPONSES (COMMAND_ID, RESPONSE) VALUES (:id, :response)""",
                param_array)

    def run_custom_voice_commands(self, text, username, db: Database = None):
        if db is None:
            db = Database()
        result = db.select_one("SELECT * FROM CUSTOM_VOICE_COMMAND_SENTENCES, CUSTOM_VOICE_COMMANDS WHERE ID = COMMAND_ID AND COMMAND = :command",
                    {'command': text})

        if(result is None):
            return None

        id = result['ID']

        action_data = result['ACTION_DATA']

        action_data = json.loads(action_data)

        #run actions
        ActionManager().run_actions(action_data, db)

        result = db.select_one("SELECT * FROM CUSTOM_VOICE_COMMAND_RESPONSES WHERE COMMAND_ID = :id ORDER BY RANDOM()",
                    {'id': id})

        return result['RESPONSE']