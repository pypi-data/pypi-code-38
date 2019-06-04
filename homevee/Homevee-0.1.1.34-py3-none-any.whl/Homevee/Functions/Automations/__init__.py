#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from Homevee.Functions.condition_actions.actions import run_actions
from Homevee.Functions.condition_actions.conditions import conditions_true
from Homevee.Helper import Logger
from Homevee.Utils.Database import Database


class Automation():
    def run_trigger_automation(self, trigger_type, type, id, value, db: Database = None):
        if db is None:
            db = Database()
        return

    def run_automations(self, automations, db: Database = None):
        if db is None:
            db = Database()
        for item in automations:
            Logger.log(item)
            if (conditions_true(json.loads(item['CONDITION_DATA']), db)):
                if (int(item['TRIGGERED']) == 0):
                    Logger.log("running item: "+str(item))
                    run_actions(json.loads(item['ACTION_DATA']), db)
                    self.set_triggered(item['ID'], 1, db)
            else:
                self.set_triggered(item['ID'], 0, db)

    def set_triggered(self, id, triggered, db: Database = None):
        if db is None:
            db = Database()


            db.update("UPDATE AUTOMATION_DATA SET TRIGGERED = :triggered WHERE ID = :id",
                        {'triggered': triggered, 'id': id})