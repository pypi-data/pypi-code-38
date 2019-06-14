#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Utils.Database import Database

class PlaceManager():
    def __init__(self):
        return

    def get_place(self, id, db: Database = None):
        if db is None:
            db = Database()
        if(id is None or id == "" or id is -1):
            return None

        place = db.select_one("SELECT * FROM PLACES WHERE ID = :id",
                    {'id': id})

        return place

    def get_my_places(self, user, db: Database = None):
        if db is None:
            db = Database()
        places = []

        results = db.select_all("SELECT * FROM PLACES", {})

        for place in results:
            places.append({'id': place['ID'], 'name': place['NAME'], 'address': place['ADDRESS'], 'latitude': place['LATITUDE'], 'longitude': place['LONGITUDE']})

        return places

    def add_edit_place(self, user, id, name, address, latitude, longitude, db: Database = None):
        if db is None:
            db = Database()
        add_new = (id == None or id == "" or id == "-1")

        if (add_new):
            db.insert("INSERT INTO PLACES (NAME, ADDRESS, LATITUDE, LONGITUDE) VALUES (:name, :address, :latitude, :longitude)",
                        {'name': name, 'address': address, 'latitude': latitude, 'longitude': longitude})
        else:
            db.update("UPDATE PLACES SET NAME = :name, ADDRESS = :address, LATITUDE = :latitude, LONGITUDE = :longitude WHERE ID = :id",
                        {'name': name, 'address': address, 'latitude': latitude, 'longitude': longitude, 'id': id})

    def delete_place(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        db.delete("DELETE FROM PLACES WHERE ID = :id", {'id': id})