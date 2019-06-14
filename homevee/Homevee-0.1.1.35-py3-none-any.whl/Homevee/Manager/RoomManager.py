#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlite3.dbapi2 import Row
from typing import Type, List

from Homevee.Exception import NoPermissionException, RoomHasItemsException
from Homevee.Item import Item
from Homevee.Item.Room import Room
from Homevee.Item.Status import *
from Homevee.Item.User import User
from Homevee.Manager import Manager
from Homevee.Manager.SceneManager import SceneManager
from Homevee.Utils.Database import Database


class RoomManager(Manager):
    def __init__(self):
        super(RoomManager, self).__init__()
        return

    def item_exists(self, item: Room, db: Database) -> bool:
        return self.find_by_id(item.id, db) is not None

    def create(self, item: Room, db: Database) -> bool:
        return (db.insert("INSERT INTO ROOMS (NAME, ICON) VALUES (:name, :icon)",
                  {'name': item.name, 'icon': item.icon}) != False)

    def update(self, item: Room, db: Database) -> bool:
        return db.update("UPDATE ROOMS SET NAME = :name, ICON = :icon WHERE LOCATION = :id",
                            {'name': item.name, 'icon': item.icon, 'id': item.id})

    def delete(self, item: Room, db: Database) -> bool:
        # TODO implement room deletion
        return False

    def get_all(self, db: Database) -> List[Type[Item]]:
        return self.find_by_query('SELECT * FROM ROOMS', {}, db)

    def find_by_id(self, id: int, db: Database) -> Type[Item]:
        return self.find_one_by_query('SELECT * FROM ROOMS WHERE ID = :id', {'id': id}, db)

    def construct_item_from_dict(self, dict: dict) -> Type[Item]:
        return Room.create_from_dict(dict)

    def check_permission(self, user: User, item: Room) -> bool:
        return user.has_permission(item.id)

    def create_item_from_db_result(self, result: Row) -> Room:
        return Room(result['NAME'], result['ICON'], result['LOCATION'])

    def get_rooms(self, user: User, db: Database = None) -> list:
        if db is None:
            db = Database()
        rooms = []
        all_rooms = Room.load_all(db)
        for room in all_rooms:
            if(user.has_permission(room.id)):
                rooms.append(room)
        return rooms

    def add_edit_room(self, user, room_name, room_key, icon, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            raise NoPermissionException()

        try:
            room = Item.load_from_db(Room, room_key, db)
            room.name = room_name
            room.icon = icon
        except:
            room = Room(room_name, room_key)

        return room.save()

    def delete_room(self, user, room_key, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            raise NoPermissionException()

        room = Item.load_from_db(Room, room_key, db)

        roomdata = room.get_room_data(db)

        #roomdata = get_room_data(user, room_key, db)['roomdata']

        if roomdata is not None and len(roomdata) == 1:
            if roomdata[0]['type'] == "scenes":
                scenes = SceneManager().get_scenes(user, room_key, db)

                for scene in scenes:
                    if scene['room'] == room_key:
                        return Status(type=STATUS_ROOM_HAS_ITEMS).get_dict()
        elif roomdata is not None and len(roomdata) > 1:
            raise RoomHasItemsException()

        return room.delete()

    def move_items_and_delete_old_room(self, user, old_room, new_room, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            return Status(type=STATUS_NO_ADMIN).get_dict()

        params = {'oldroom': old_room, 'newroom': new_room}

        query_array = []

        #Funksteckdosen
        query_array.append("UPDATE 'funksteckdosen' SET ROOM = :newroom WHERE ROOM == :oldroom;")

        #Z-Wave
        query_array.append("UPDATE 'ZWAVE_SENSOREN' SET RAUM = :newroom WHERE RAUM == :oldroom;")
        query_array.append("UPDATE 'ZWAVE_THERMOSTATS' SET RAUM = :newroom WHERE RAUM == :oldroom;")

        #DIY
        query_array.append("UPDATE 'DIY_DEVICES' SET ROOM = :newroom WHERE ROOM == :oldroom;")
        query_array.append("UPDATE 'DIY_SENSORS' SET RAUM = :newroom WHERE RAUM == :oldroom;")
        query_array.append("UPDATE 'DIY_REEDSENSORS' SET RAUM = :newroom WHERE RAUM == :oldroom;")
        query_array.append("UPDATE 'DIY_SWITCHES' SET RAUM = :newroom WHERE RAUM == :oldroom;")

        #Szenen
        query_array.append("UPDATE 'SCENES' SET ROOM = :newroom WHERE ROOM == :oldroom;")


        for query in query_array:
            db.update(query, params)

        return self.delete_room(user, old_room, db)

    def delete_room_with_items(self, user, room_key, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            return Status(type=STATUS_NO_ADMIN).get_dict()

        params = {'oldroom': room_key}

        query_array = []

        # Funksteckdosen
        query_array.append("DELETE FROM 'funksteckdosen' WHERE ROOM == :oldroom;")

        # Z-Wave
        query_array.append("DELETE FROM 'ZWAVE_SENSOREN' WHERE RAUM == :oldroom;")
        query_array.append("DELETE FROM 'ZWAVE_THERMOSTATS' WHERE RAUM == :oldroom;")

        # DIY
        query_array.append("DELETE FROM 'DIY_DEVICES' WHERE ROOM == :oldroom;")
        query_array.append("DELETE FROM 'DIY_REEDSENSORS' WHERE RAUM == :oldroom;")
        query_array.append("DELETE FROM 'DIY_SENSORS' WHERE RAUM == :oldroom;")
        query_array.append("DELETE FROM 'DIY_SWITCHES' WHERE RAUM == :oldroom;")

        # Szenen
        query_array.append("DELETE FROM 'SCENES' WHERE ROOM == :oldroom;")


        for query in query_array:
            db.delete(query, params)

        return self.delete_room(user, room_key, db)