#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Item.Room import Room
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database

class SceneManager():
    def __init__(self):
        return

    def get_all_scenes(self, user, db: Database = None):
        if db is None:
            db = Database()

        results = db.select_all("SELECT * FROM ROOMS", None)

        rooms = []

        for room in results:
            if not user.has_permission(room['LOCATION']):
                continue

            scenes = self.get_scenes(user, room['LOCATION'], db)

            scenes = scenes['scenes']

            if(len(scenes) is not 0):
                room_item = {'name': room['NAME'], 'location': room['LOCATION'], 'icon': room['ICON'], 'scenes': scenes}
                rooms.append(room_item)

        return {'rooms': rooms}

    def get_scenes(self, user, location, db: Database = None):
        if db is None:
            db = Database()
        scenes = []

        if isinstance(location, Room):
            location = location.id

        if user.has_permission(location):
            items = db.select_all("SELECT * FROM SCENES WHERE ROOM = :location",{'location': location})

            for item in items:
                scenes.append({'id': item['ID'], 'name': item['NAME'], 'action_data': item['ACTION_DATA'],
                              'location': item['ROOM']})

        return {'scenes': scenes}

    def add_edit_scene(self, user, id, name, location, action_data, db: Database = None):
        if db is None:
            db = Database()
        add_new = (id == None or id == "" or id == "-1")

        with db:
            cur = db.cursor()

            if(add_new):
                db.insert("INSERT INTO SCENES (NAME, ROOM, ACTION_DATA) VALUES (:name, :room, :actions)",
                            {'name': name, 'room': location, 'actions': action_data})

                return Status(type=STATUS_OK).get_dict()

            else:
                db.update("UPDATE SCENES SET NAME = :name, ROOM = :location, ACTION_DATA = :actions WHERE ID = :id",
                    {'name': name, 'location': location, 'actions': action_data, 'id': id})

                return Status(type=STATUS_OK).get_dict()

    def delete_scene(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        with db:
            cur = db.cursor()

            db.delete("DELETE FROM SCENES WHERE ID = :id", {'id': id})

            return Status(type=STATUS_OK).get_dict()