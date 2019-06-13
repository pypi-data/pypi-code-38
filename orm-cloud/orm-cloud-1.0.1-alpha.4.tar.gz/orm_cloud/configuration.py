

class Configuration:
    def __init__(self):
        pass

    @property
    def db_type(self):
        return self._db_type

    @db_type.setter
    def db_type(self, db_type):
        self._db_type = db_type

    @property
    def db_hostname(self):
        return self._db_hostname

    @db_hostname.setter
    def db_hostname(self, db_hostname):
        self._db_hostname = db_hostname

    @property
    def db_username(self):
        return self._db_username

    @db_username.setter
    def db_username(self, db_username):
        self._db_username = db_username

    @property
    def db_password(self):
        return self._db_password

    @db_password.setter
    def db_password(self, db_password):
        self._db_password = db_password

    @property
    def db_name(self):
        return self._db_name

    @db_name.setter
    def db_name(self, db_name):
        self._db_name = db_name
