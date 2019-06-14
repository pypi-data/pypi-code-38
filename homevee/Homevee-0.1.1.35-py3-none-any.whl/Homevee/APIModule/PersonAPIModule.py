from Homevee.APIModule import APIModule
from Homevee.Item.Person import Person
from Homevee.Item.Status import *
from Homevee.Manager.PersonManager import PersonManager

ACTION_KEY_GET_PERSONS = "getpersons"
ACTION_KEY_ADD_EDIT_PERSON = "addeditperson"
ACTION_KEY_DELETE_PERSON = "deleteperson"

class PersonAPIModule(APIModule):
    def __init__(self):
        super(PersonAPIModule, self).__init__()
        self.person_manager = PersonManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_PERSONS: self.get_persons,
            ACTION_KEY_ADD_EDIT_PERSON: self.add_edit_person,
            ACTION_KEY_DELETE_PERSON: self.delete_person
        }

        return mappings

    def get_persons(self, user, request, db):
        persons = self.person_manager.get_persons(db)
        return Status(type=STATUS_OK, data={'persons': Person.list_to_dict(persons)})

    def add_edit_person(self, user, request, db):
        self.person_manager.add_edit_person(user, request['id'], request['name'], request['nickname'],
                                                       request['address'],
                                                       request['latitude'], request['longitude'],
                                                       request['phonenumber'],
                                                       request['birthdate'], db)
        return Status(type=STATUS_OK)

    def delete_person(self, user, request, db):
        self.person_manager.delete_person(user, request['id'], db)
        return Status(type=STATUS_OK)