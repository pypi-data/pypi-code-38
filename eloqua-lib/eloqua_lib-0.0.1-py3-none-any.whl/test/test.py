from datetime import datetime
import logging
from unittest import TestCase
import unittest

from eloqua.eloqua import EloquaConnection, CustomObject
from .test_data import *
from .creds import *

# Enter your sandbox orgs credentials in creds.py
# This script will create all the required objects and delete them on its own

logger = logging.getLogger("EloquaTestClass")
logging.basicConfig(level=logging.INFO)


class TestForms(TestCase):
    def setUp(self):
        self.elq = EloquaConnection(ELOQUA_COMPANY, ELOQUA_USER_NAME, ELOQUA_PASSWORD)

    def test_form_asset(self):
        pass


class TestCustomObject(TestCase):

    def setUp(self):
        self.elq = EloquaConnection(ELOQUA_COMPANY, ELOQUA_USER_NAME, ELOQUA_PASSWORD)

        # ensure testing object exists
        existing_testing_objects_resp = self.elq.get_list(CustomObject, {
            "search": "name=%s" % TESTING_CUSTOM_OBJECT_DOG_OWNER['name']
        })
        if len(existing_testing_objects_resp.data) > 0:
            self.testing_object = existing_testing_objects_resp.data[0]
            code = self.elq.generate_custom_object_code(TESTING_CUSTOM_OBJECT_DOG_OWNER['name'], class_name="DogOwner")
        else:
            logger.error("Please add this class (DogOwner) to the `test_data.py` file")
            self.create_custom_object_asset(TESTING_CUSTOM_OBJECT_DOG_OWNER)
            code = self.elq.generate_custom_object_code(TESTING_CUSTOM_OBJECT_DOG_OWNER['name'], class_name="DogOwner")
            logger.error("\n%s" % code)
            raise Exception()

    def tearDown(self):
        pass

    def delete_custom_object_if_exists(self, data):
        existing_testing_objects_resp = self.elq.get_list(CustomObject, {
            "search": "name=%s" % data['name']
        })

        if len(existing_testing_objects_resp.data) > 0:
            self.elq.delete(existing_testing_objects_resp.data[0])

    def create_custom_object_asset(self, data):
        """ Helper method to create testing custom object"""
        custom_object = CustomObject()
        custom_object.raw_data = data
        resp = self.elq.create(custom_object)
        return resp

    def test_custom_object_asset(self):
        object_name_change_test_name = "NameChangeTest_xxxxx_xxxxxxx__x"
        self.delete_custom_object_if_exists(TESTING_CUSTOM_OBJECT_ASSET)
        test_custom_object = self.create_custom_object_asset(TESTING_CUSTOM_OBJECT_ASSET)

        logger.info("Created custom object %s" % test_custom_object)

        # Edit Custom Object
        test_custom_object.name = object_name_change_test_name
        resp = self.elq.update(test_custom_object)
        new_object = self.elq.get_list(CustomObject, {
            "search": "name=%s" % object_name_change_test_name
        }).data[0]

        logger.info("Edited custom object name to %s" % object_name_change_test_name)

        # Set the name back to the original name
        self.assertEqual(object_name_change_test_name, new_object.name)

        new_object.name = TESTING_CUSTOM_OBJECT_ASSET['name']
        resp = self.elq.update(new_object)

        logger.info("Edited custom object name back: %s" % TESTING_CUSTOM_OBJECT_ASSET['name'])

        # Code Generation
        code = self.elq.generate_custom_object_code(TESTING_CUSTOM_OBJECT_ASSET['name'], class_name="QuickTest")
        logger.info("Printing code for object")
        logger.info("\n%s" % code)

        self.delete_custom_object_if_exists(TESTING_CUSTOM_OBJECT_ASSET)

    def test_custom_object_data(self):
        logger.info("If this test class is failing, delete the custom object in your instance TEST_Dog_Owner and re "
                    "run. Then add the class it prints to the test_data.py class")
        dog_owner_1 = DogOwner()

        # Set attributes
        date = int(datetime.timestamp(datetime.now()))

        dog_owner_1.DogBreed1 = "Corgi"
        dog_owner_1.DogName1 = "Spot"
        dog_owner_1.StartOfOwnership1 = date
        dog_owner_1.DogColor1 = "Brown"
        dog_owner_1.AgeAtStartOfOwnership1 = 1

        # Create record
        dog_owner_1 = self.elq.create(dog_owner_1)
        assert isinstance(dog_owner_1, DogOwner)
        self.assertEqual("Corgi", dog_owner_1.DogBreed1)
        self.assertEqual("Spot", dog_owner_1.DogName1)
        self.assertEqual("Brown", dog_owner_1.DogColor1)
        self.assertEqual(str(date), dog_owner_1.StartOfOwnership1)
        self.assertEqual("1", dog_owner_1.AgeAtStartOfOwnership1)

        # Edit record
        dog_owner_1.DogName1 = "Poochy Poo"
        self.elq.update(dog_owner_1)

        dog_owner_1 = self.elq.get(DogOwner, dog_owner_1.id)

        self.assertEqual("Poochy Poo", dog_owner_1.DogName1)

        existing_pooches = self.elq.get_list(DogOwner, {
            "search": "DogName1='Poochy Poo'"
        }).data

        self.assertNotEqual(0, len(existing_pooches))

        existing_pooch_number = len(existing_pooches)

        # Delete Records
        self.elq.delete(dog_owner_1)

        existing_pooches = self.elq.get_list(DogOwner, {
            "search": "DogName1='Poochy Poo'"
        }).data

        self.assertEqual(existing_pooch_number - 1, len(existing_pooches))


def main():
    unittest.main()
