#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback
from sqlite3.dbapi2 import Row
from typing import Type, List

from Homevee.Exception import ItemNotFoundException, NoPermissionException
from Homevee.Helper import Logger
from Homevee.Item import Item
from Homevee.Item.Status import *
from Homevee.Item.User import User, Permission
from Homevee.Manager import Manager
from Homevee.Utils.Database import Database


class UserManager(Manager):
    def __init__(self):
        super(UserManager, self).__init__()
        return

    def item_exists(self, item: User, db: Database) -> bool:
        return self.find_by_id(item.id, db) is None

    def create(self, item: User, db: Database) -> bool:
        return db.insert("""INSERT INTO USERDATA (USERNAME, PASSWORD, IP, PERMISSIONS, PW_SALT) VALUES 
                                    (:username, :password, :ip, :permissions, :salt)""",
                  {'username': item.username, 'password': item.hashed_password, 'ip': item.ip,
                   'permissions': Permission.get_json_list(item.permissions), 'salt': item.salt}) != False

    def update(self, item: User, db: Database) -> bool:
        return db.update("""UPDATE USERDATA SET PASSWORD = :password, IP = :ip, PERMISSIONS = :permissions,
                                    PW_SALT = :salt WHERE ID = :id""",
                  {'password': item.hashed_password, 'ip': item.ip,
                   'permissions': Permission.get_json_list(item.permissions),
                   'salt': item.salt, 'id': item.id})

    def delete(self, item: User, db: Database) -> bool:
        return db.delete("DELETE FROM USERDATA WHERE ID == :id", {'user': item.id})

    def get_all(self, db: Database) -> List[Type[Item]]:
        return self.find_by_query('SELECT * FROM USERDATA', {}, db)

    def find_by_id(self, id: int, db: Database) -> Type[Item]:
        return self.find_one_by_query('SELECT * FROM USERDATA', {}, db)

    def find_by_username(self, username: list, db: Database) -> Type[Item]:
        users = self.find_by_usernames([username], db)

        if(len(users) == 0):
            return None
        else:
            return users[0]

    def find_by_usernames(self, usernames: list, db: Database) -> List[Type[Item]]:
        return self.find_by_query('SELECT * FROM USERDATA WHERE USERNAME IN (%s)' % ','.join('?'*len(usernames)),
                                     usernames, db)

    def construct_item_from_dict(self, dict: dict) -> Type[Item]:
        pass

    def check_permission(self, user: User, item: User) -> bool:
        return user.has_permission("admin") or (user.id == item.id)

    def create_item_from_db_result(self, result: Row) -> User:
        return User(result['USERNAME'], result['PASSWORD'], result['IP'], result['AT_HOME'],
                        result['EVENTS_LAST_CHECKED'], Permission.create_list_from_json(result['PERMISSIONS']),
                        result['DASHBOARD_DATA'], result['PW_SALT'], result['FCM_TOKEN'],
                        result['CURRENT_LOCATION'], result['ID'])


    def set_user_fcm_token(self, user, token, db: Database = None):
        if db is None:
            db = Database()
        user.fcm_token = token

        try:
            user.save(db)
            return Status(type=STATUS_OK).get_dict()
        except:
            return Status(type=STATUS_ERROR).get_dict()

    def has_users(self, db):
        users = User.load_all(db)
        return len(users) > 0

    def get_users(self, user, db: Database = None):
        if db is None:
            db = Database()
        if not user.hash_password("admin"):
            return Status(type=STATUS_NO_ADMIN).get_dict()

        return User.load_all(db)

    def delete_user(self, user, user_to_delete, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            return Status(type=STATUS_NO_ADMIN).get_dict()

        user_to_delete = User.load_username_from_db(user_to_delete, db)
        return user_to_delete.delete(db)

    def add_edit_user(self, user, name, psw, ip, permissions, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            if user.username != name:
                raise NoPermissionException

        hashed_pw, salt = User.hash_password(psw)

        try:
            edit_user = User.load_username_from_db(name, db)

            if not (psw == "" or psw is None):
                edit_user.hashed_password = hashed_pw
                edit_user.salt = salt

            edit_user.ip = ip
            edit_user.permissions = Permission.create_list_from_json(permissions)

        except ItemNotFoundException:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            edit_user = User(username=name, hashed_password=hashed_pw, salt=salt, ip=ip,
                             permissions=Permission.create_list_from_json(permissions),
                             at_home=False, fcm_token=None, current_location=None,
                             dashboard_data=None, events_last_checked=0)

        print(edit_user.get_dict())

        return edit_user.save(db)