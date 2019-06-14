#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

from Homevee.Item.Event import Event
from Homevee.Utils.Database import Database


class EventManager():
    def __init__(self):
        return

    '''Gibt die Ereignisse zurück'''
    def get_events(self, user, type, limit, offset, db: Database = None):
        if db is None:
            db = Database()
        events = Event.load_all_from_db_desc_date_by_type(offset, limit, type)
        user.events_last_checked = time.time()
        user.save(db)
        return events

    '''Gibt die Anzahl der ungesehenen Ereignisse zurück'''
    def get_unseen_events(self, user, db: Database = None):
        if db is None:
            db = Database()
        count = Event.get_unseen_events(user)
        return count

    '''Gibt die vorhandenen Ereignis-Typen zurück'''
    def get_event_types(self, db):
        results = db.select_all("SELECT DISTINCT TYPE FROM EVENTS ORDER BY TYPE", {})

        types = []

        for data in results:
            types.append(data['TYPE'])

        return types

    '''Erstellt ein neues Ereignis'''
    def add_event(self, type, text, db: Database = None):
        if db is None:
            db = Database()
        event = Event(text=text, type=type)
        return event.save()