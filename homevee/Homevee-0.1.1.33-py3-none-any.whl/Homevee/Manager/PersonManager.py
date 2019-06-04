#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Item.Device import Device
from Homevee.Item.Person import Person
from Homevee.Utils.Database import Database

class PersonManager():
    def __init__(self):
        return

    def add_edit_person(self, user, id, name, nickname, address, latitude, longitude, phonenumber, birthdate, db: Database = None):
        if db is None:
            db = Database()
        try:
            person = Device.load_from_db(Person, id, db)
            person.name = name
            person.nickname = nickname
            person.phone_number = phonenumber
            person.address = address
            person.birthdate = birthdate
            person.longitude = longitude
            person.latitude = latitude
        except:
            person = Person(name, nickname, phonenumber, address, birthdate, longitude, latitude)

        return person.api_save()

    def get_persons(self, db):
        persons = Person.load_all(db)
        return {'persons': Person.list_to_dict(persons)}

    def delete_person(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        person = Device.load_from_db(Person, id)
        return person.api_delete()