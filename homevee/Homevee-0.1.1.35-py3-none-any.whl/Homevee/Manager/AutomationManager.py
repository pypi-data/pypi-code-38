#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from Homevee.Item.Room import Room
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database


class AutomationManager():
    def __init__(self):
        return

    def get_automations(self, user, room, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(room):
            return {'result': 'nopermission'}

        rules = []
        results = db.select_all("SELECT * FROM AUTOMATION_DATA WHERE LOCATION = :location", {'location': room})

        for item in results:
            data = self.get_full_automation_data(item['ID'], db)

            if 'result' in data and data['result'] == 'nopermission':
                continue

            rules.append(data)

        return rules

    def get_full_automation_data(self, id, db: Database = None):
        if db is None:
            db = Database()
        data = db.select_one("SELECT * FROM AUTOMATION_DATA WHERE ID = :id", {'id': id})

        trigger_data = self.get_trigger_data(id, db)

        return {'name': data['NAME'], 'id': data['ID'], 'location': data['LOCATION'],
                'locationname': Room.get_name_by_id(data['LOCATION'], db), 'triggerdata': trigger_data,
                'conditiondata': data['CONDITION_DATA'], 'actiondata': data['ACTION_DATA'], 'isactive': True}

    def get_trigger_data(self, id, db: Database = None):
        if db is None:
            db = Database()
            items = db.select_all("SELECT * FROM AUTOMATION_TRIGGER_DATA WHERE AUTOMATION_RULE_ID = :id", {'id': id})

            trigger_data = []

            for item in items:
                trigger_data.append({'type': item['TYPE'], 'id': item['ID'], 'value': item['VALUE'], 'text': item['TEXT']})

            return trigger_data

    def add_edit_automation_rule(self, user, location, id, name, trigger_data, condition_data, action_data, is_active, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission(location):
            return {'result': 'nopermission'}

        add_new = (id == None or id == "" or id == "-1")

        if(add_new):
            id = db.insert("INSERT INTO AUTOMATION_DATA (LOCATION, NAME, CONDITION_DATA, ACTION_DATA, IS_ACTIVE) VALUES (:location, :name, :conditions, :actions, :active)",
                        {'location': location, 'name': name, 'conditions': condition_data, 'actions': action_data, 'active': is_active})

            trigger_data = json.loads(trigger_data)

            self.add_trigger_data(trigger_data, id, db)
            return Status(type=STATUS_OK).get_dict()

        else:
            db.update("UPDATE AUTOMATION_DATA SET LOCATION = :location, NAME = :name, CONDITION_DATA = :conditions, ACTION_DATA = :actions, IS_ACTIVE = :active WHERE ID = :id",
                {'location': location, 'name': name, 'conditions': condition_data, 'actions': action_data, 'active': is_active, 'id': id})

            trigger_data = json.loads(trigger_data)

            db.delete("DELETE FROM AUTOMATION_TRIGGER_DATA WHERE AUTOMATION_RULE_ID = :id", {'id': id})

            self.add_trigger_data(trigger_data, id, db)
            return Status(type=STATUS_OK).get_dict()

    def delete_automation_rule(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        db.delete("DELETE FROM AUTOMATION_DATA WHERE ID = :id", {'id': id})
        db.delete("DELETE FROM AUTOMATION_TRIGGER_DATA WHERE AUTOMATION_RULE_ID = :id", {'id': id})

        return Status(type=STATUS_OK).get_dict()

    def add_trigger_data(self, data, id, db: Database = None):
        if db is None:
            db = Database()
        for data in data:
            param_array = {'rule': id, 'type': data['type'], 'text': data['textdata']}

            if('id' in data):
                param_array['id'] = data['id']
            else:
                param_array['id'] = None

            if('value' in data):
                param_array['value'] = data['value']
            else:
                param_array['value'] = None

            db.insert("""INSERT INTO AUTOMATION_TRIGGER_DATA (AUTOMATION_RULE_ID, TYPE, ID, VALUE, TEXT) 
            VALUES (:rule, :type, :id, :value, :text)""", param_array)