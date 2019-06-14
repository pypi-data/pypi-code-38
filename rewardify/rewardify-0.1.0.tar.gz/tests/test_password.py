# Standard library
from unittest import TestCase

# Third party imports
from peewee import Model
from peewee import SqliteDatabase
from peewee import TextField

# Local imports
from rewardify.password import PasswordHash
from rewardify.password import PasswordField
from rewardify.password import VerifyMismatchError


class PasswordTest(TestCase):

    def test_hashing_works(self):
        password_string = "super secret"

        password_hash = PasswordHash(password_string)
        self.assertTrue(password_hash.check(password_string))

    def test_password_verification_works(self):
        password_string = "super secret"
        wrong_password_string = "lucky guess?"

        password_hash = PasswordHash(password_string)
        self.assertRaises(
            VerifyMismatchError,
            password_hash.verify,
            wrong_password_string
        )

    def test_password_hash_recognition_works(self):
        password_string = "super secret"
        password_hash = PasswordHash(password_string)

        self.assertFalse(PasswordHash.is_hash(password_string))
        self.assertTrue(PasswordHash.is_hash(password_hash))

    def test_instantiating_password_hash_with_hashed_string_works(self):
        # First we create the actual hash
        password_string = "super secret"
        password_hash = PasswordHash(password_string)

        # Then we create a new PasswordHash object from the already hashed string
        hashed_password_string = str(password_hash)
        hashed_password_hash = PasswordHash(hashed_password_string)

        # In theory the second constructor should not modify the already hashed string, thus they be the same.
        self.assertEqual(str(password_hash), str(hashed_password_hash))


# TESTING THE ACTUAL PASSWORD FIELD
# ---------------------------------


class PasswordFieldModel(Model):
    """
    This is a dummy model simply to test the working of the password field
    """
    name = TextField()
    password = PasswordField()


class PasswordFieldTest(TestCase):

    TEST_DATABASE = SqliteDatabase(':memory:')
    MODELS = [PasswordFieldModel]

    # SETTING UP THE TEST DATABASE
    # ----------------------------

    def setUp(self):
        self.TEST_DATABASE.bind(self.MODELS, bind_refs=False, bind_backrefs=False)

        self.TEST_DATABASE.connect()
        self.TEST_DATABASE.create_tables(self.MODELS)

    def tearDown(self):
        self.TEST_DATABASE.drop_tables(self.MODELS)
        self.TEST_DATABASE.close()

    # ACTUAL TEST METHODS
    # -------------------

    def test_password_field_works(self):
        name_string = 'test_password_field_works'

        # Here we create the model and save it to the database
        password_string = "super secret"
        model = PasswordFieldModel(name=name_string, password=password_string)
        model.save()

        # Now we load it and check if it has worked
        model = PasswordFieldModel.get(PasswordFieldModel.name == name_string)
        self.assertTrue(model.password.check(password_string))

