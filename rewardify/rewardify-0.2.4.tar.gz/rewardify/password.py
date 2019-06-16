# Third party imports
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from peewee import Field


class PasswordHash(str):
    """
    This class inherits from a normal "string" object.
    It represents a password hash. Only hashs are being written to the database, so not to be able to possibly leak
    plain text passwords.
    The password string gets passed to the constructor, but is then immediately hashed and discarded, so only the hash
    string is saved.

    Objects of the PasswordHash type provide direct method access to check if a given password string
    correlates to the hash.

    CHANGELOG

    Added 08.06.2019
    """

    # CLASS VARIABLES
    # ---------------

    # The password hasher object, which we need to hash the password strings for us
    PASSWORD_HASHER = PasswordHasher()

    # This is a substring, which every PasswordHash contains to identify it as a string.
    # we will use a "string" contains to check if a given string is already a hash or a plain text password
    HASH_IDENTIFIER = "$argon2id$"

    # OVERWRITING STRING CONSTRUCTOR
    # ------------------------------

    def __new__(cls, password_string: str):
        """
        The __new__ method is called when a new object is being instantiated from the class. In this case we use it to
        modify the construction logic of the str parent class to implement custom logic:
        When the string already is a hash, it will be set as the value of the string. If it is detected, that the given
        string is still a plain text password though, it will first be hashed.

        CHANGELOG

        Added 08.06.2019

        Changed 09.06.2019
        Added the distinction between the string already being a hash or a plain text password.

        :param password_string:
        :return:
        """
        # IMPORTANT NOTICE:
        # In order to overwrite the value within a class, that inherits from the built in "str" class (as would be the
        # case when some preprocessing or modification of the string has to be made) the __new__ method has to be used!
        # The __init__ method will not work!

        # If the string, that is being passed to the constructor already is the string representation of a hash we just
        # use that value, if not we need to hash it first!
        if cls.is_hash(password_string):
            password_hash = password_string
        else:
            password_hash = cls.PASSWORD_HASHER.hash(password_string)
        return str.__new__(cls, password_hash)

    def __init__(self, password_string: str):
        super(PasswordHash, self).__init__()

    # UTILITY METHODS
    # ---------------

    def check(self, password_string: str) -> bool:
        """
        Given a password string, that was entered by a user through the front end, this method will check if the
        given password string correlates with this very hash and return true if it does so.

        CHANGELOG

        Added 08.06.2019

        :param password_string:
        :return:
        """
        try:
            self.PASSWORD_HASHER.verify(self, password_string)
            return True
        except VerifyMismatchError:
            return False

    def verify(self, password_string: str):
        """
        Given a password string, that was entered by a user through the front end, this method will check if the
        given password string correlates with this very hash and raises an exception if the given string does not
        match with the hash

        CHANGELOG

        Added 08.06.2019

        :param password_string:
        :return: void
        """
        self.PASSWORD_HASHER.verify(self, password_string)

    @classmethod
    def is_hash(cls, string):
        """
        Given a string, this method returns true, if the given string is already the hash of a password and false if
        it still is a plain text password.

        CHANGELOG

        Added 08.06.2019

        :param string:
        :return: bool
        """
        if cls.HASH_IDENTIFIER in string:
            return True
        else:
            return False


class PasswordField(Field):
    """
    This is a custom field for database models, which stores a password in the form of a hash. The plain text password
    will not be stored!

    CHANGELOG

    Added 09.06.2019
    """

    field_type = 'text'

    # FIELD ACCESS METHODS
    # --------------------

    def db_value(self, value):
        """
        This method is called when the python value has to be converted into a actual database value, for that we will
        use the hashed string representation of the password string

        CHANGELOG

        Added 09.06.2019

        :param value:
        :return:
        """
        # Given a value from the "realm of python code execution" this method has to return a value, that will
        # ultimately be passed to the database to be saved into a (string) field.
        password_hash = PasswordHash(value)
        return str(password_hash)

    def python_value(self, value):
        """
        This method is called when the database value is supposed to be converted into a python object, which will then
        serve as the attribute to the model object.
        In this case we will take the string hash and convert it into a PasswordHash object, as that features
        special methods to check for password validity

        CHANGELOG

        Added 09.06.2019

        :param value:
        :return:
        """
        # This method is given the raw value, which is retrieved from the database and has the job of converting
        # it into the correct python object.
        # This would be a "PasswordHash" instance
        password_hash = PasswordHash(value)
        return password_hash
