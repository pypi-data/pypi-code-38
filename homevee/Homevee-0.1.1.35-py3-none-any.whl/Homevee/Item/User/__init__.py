import os
import traceback

from passlib.handlers.pbkdf2 import pbkdf2_sha512

from Homevee.Exception import ItemNotFoundException, InvalidParametersException, DatabaseSaveFailedException
from Homevee.Helper import Logger
from Homevee.Item import Item
from Homevee.Item.User.Permission import Permission
from Homevee.Utils.Database import Database


class User(Item):
    def __init__(self, username, hashed_password, ip, at_home, events_last_checked,
                 permissions, dashboard_data, salt, fcm_token, current_location, id=None):
        super(User, self).__init__()

        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.ip = ip
        self.events_last_checked = events_last_checked
        self.permissions = permissions
        self.dashboard_data = dashboard_data
        self.salt = salt
        self.fcm_token = fcm_token
        self.current_location = current_location

        self.at_home = True
        if at_home == 1 or at_home is True or at_home == "1":
            self.at_home = True

    def delete(self, db: Database = None):
        try:
            db.delete("DELETE FROM USERDATA WHERE USERNAME == :user", {'user': self.username})
        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            raise DatabaseSaveFailedException("Could not delete user from database")

    def has_permission(self, permission):
        for user_permission in self.permissions:
            if user_permission.key == "admin" or user_permission.id == permission:
                return True

        return False

    @staticmethod
    def hash_password(password: str) -> tuple:
        """
        Hashes the given password
        :param password: the password to hash
        :return: a tuple with the hashed password and the used salt
        """
        salt = os.urandom(12).hex()

        hashed_pw = pbkdf2_sha512.encrypt(password + salt, rounds=200000)

        # print "Password: "+password
        # print "Salt: "+salt
        # print "Hashed: "+hashed_pw

        #self.hashed_password = hashed_pw
        #self.salt = salt

        return (hashed_pw, salt)

    def verify(self, password: str) -> bool:
        """
        Checks if this user is verified by the given password
        :param password: the password to verify the user with
        :return: true if verified, false otherwise
        """
        try:
            return pbkdf2_sha512.verify(password + self.salt, self.hashed_password)
        except:
            return False

    def save(self, db: Database = None):
        try:
            # insert
            if (self.id is None or self.id == ""):
                db.insert("""INSERT INTO USERDATA (USERNAME, PASSWORD, IP, PERMISSIONS, PW_SALT) VALUES 
                            (:username, :password, :ip, :permissions, :salt)""",
                            {'username': self.username, 'password': self.hashed_password, 'ip': self.ip,
                             'permissions': Permission.get_json_list(self.permissions), 'salt': self.salt})
            # update
            else:
                db.update("""UPDATE USERDATA SET PASSWORD = :password, IP = :ip, PERMISSIONS = :permissions,
                            PW_SALT = :salt WHERE ID = :id""",
                            {'password': self.hashed_password, 'ip': self.ip,
                             'permissions': Permission.get_json_list(self.permissions),
                             'salt': self.salt, 'id': self.id})
                #TODO add generated id to object
        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            raise DatabaseSaveFailedException("Could not save user to database")

    def build_dict(self):
        dict = {
            'id': self.id,
            'username': self.username,
            'password': "",#self.hashed_password,
            'ip': self.ip,
            'at_home': self.at_home,
            'events_last_checked': self.events_last_checked,
            'permissions': Permission.list_to_dict(self.permissions),
            'dashboard_data': self.dashboard_data,
            'salt': self.salt,
            'fcm_token': self.fcm_token,
            'current_location': self.current_location
        }
        return dict

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        items = []
        for result in db.select_all(query, params):
            item = User(result['USERNAME'], result['PASSWORD'], result['IP'], result['AT_HOME'],
                        result['EVENTS_LAST_CHECKED'], Permission.create_list_from_json(result['PERMISSIONS']),
                        result['DASHBOARD_DATA'], result['PW_SALT'], result['FCM_TOKEN'],
                        result['CURRENT_LOCATION'], result['ID'])
            items.append(item)
        return items

    @staticmethod
    def load_by_permission(permission, db: Database = None):
        return User.load_by_permissions([permission], db)

    @staticmethod
    def load_by_permissions(permissions, db: Database = None):
        users = User.load_all(db)
        output = []
        for permission in permissions:
            for user in users:
                if user.has_permission(permission) and user not in users:
                    output.append(user)
        return users

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        return User.load_all_from_db('SELECT * FROM USERDATA WHERE ID IN (%s)' % ','.join('?'*len(ids)),
                                     ids, db)

    @staticmethod
    def load_all_usernames_from_db(usernames, db: Database = None):
        return User.load_all_from_db('SELECT * FROM USERDATA WHERE USERNAME IN (%s)' % ','.join('?'*len(usernames)),
                                     usernames, db)

    @staticmethod
    def load_all(db: Database):
        return User.load_all_from_db('SELECT * FROM USERDATA', {}, db)

    @staticmethod
    #ID is username
    def load_username_from_db(username, db: Database = None):
        users = User.load_all_usernames_from_db([username], db)
        if((len(users) == 0) or (users[0].username != username)):
            raise ItemNotFoundException("Could not find username: " + username)
        else:
            return users[0]

    @staticmethod
    def create_from_dict(dict):
        try:
            id = dict['id']
            username = dict['username']
            password = dict['password']
            ip = dict['ip']
            at_home = dict['at_home']
            events_last_checked = dict['events_last_checked']
            permissions = Permission.list_from_dict(dict['permissions'])
            dashboard_data = dict['dashboard_data']
            salt = dict['salt']
            fcm_token = dict['fcm_token']
            current_location = dict['current_location']
            user = User(username, password, ip, at_home, events_last_checked,
                        permissions, dashboard_data, salt, fcm_token, current_location, id)
            return user
        except:
            raise InvalidParametersException("User.create_from_dict(): invalid dict")