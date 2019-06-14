#!/usr/bin/python
# -*- coding: utf-8 -*-

from Homevee.Item import Item
from Homevee.Item.Device import Device
from Homevee.Item.Person import Person
from Homevee.Utils.Database import Database

class PersonManager():
    def __init__(self):
        return

    def add_edit_person(self, user, id, name, nickname, address, latitude, longitude, phonenumber, birthdate, db: Database = None):
        if db is None:
            db = Database()

        person_item = None

        try:
            person_item = Item.load_from_db(Person, id, db)
        except:
            pass

        if person_item is None:
            person_item = Person(name, nickname, phonenumber, address, birthdate, longitude, latitude)
        else:
            person_item.name = name
            person_item.nickname = nickname
            person_item.phone_number = phonenumber
            person_item.address = address
            person_item.birthdate = birthdate
            person_item.longitude = longitude
            person_item.latitude = latitude
            print("update")

        return person_item.save()

    def get_persons(self, db):
        persons = Person.load_all(db)
        return persons

    def delete_person(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        person = Device.load_from_db(Person, id)
        return person.delete()