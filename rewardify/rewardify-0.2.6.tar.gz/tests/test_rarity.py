# Standard library
from unittest import TestCase

# Third party
from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField

# Local imports
from rewardify.rarity import Rarity
from rewardify.rarity import RarityField


class TestRarity(TestCase):

    # ACTUAL TEST CASES
    # -----------------

    def test_construction_with_string_works(self):
        rarity_string = 'legendary'
        rarity_int = 4
        rarity = Rarity(rarity_string)

        self.assertEqual(str(rarity), rarity_string)
        self.assertEqual(int(rarity), rarity_int)

    def test_construction_with_int_works(self):
        rarity_string = 'legendary'
        rarity_int = 4
        rarity = Rarity(rarity_int)

        self.assertEqual(str(rarity), rarity_string)
        self.assertEqual(int(rarity), rarity_int)

    def test_comparison_works(self):
        rarity_high = Rarity(4)
        rarity_low = Rarity(1)

        self.assertTrue(rarity_high > rarity_low)
        self.assertTrue(rarity_low < rarity_high)
        self.assertTrue(rarity_high == rarity_high)


# TESTING THE RARITY FIELD
# ------------------------

class RarityModel(Model):

    name = CharField()
    rarity = RarityField()


class TestRarityField(TestCase):

    TEST_DATABASE = SqliteDatabase(':memory:')
    MODELS = [RarityModel]

    SAMPLE_MODEL_NAME = 'sample'

    # SETTING UP THE TEST DATABASE
    # ----------------------------

    def setUp(self):
        self.TEST_DATABASE.bind(self.MODELS, bind_refs=False, bind_backrefs=False)

        self.TEST_DATABASE.connect()
        self.TEST_DATABASE.create_tables(self.MODELS)

    def tearDown(self):
        self.TEST_DATABASE.drop_tables(self.MODELS)
        self.TEST_DATABASE.close()

    # THE ACTUAL TEST CASES
    # ---------------------

    def test_rarity_field_insert_string_works(self):
        # Inserting a model into the database
        model = RarityModel(
            name=self.SAMPLE_MODEL_NAME,
            rarity='legendary'
        )
        model.save()

        # Loading it again
        model = RarityModel.get(RarityModel.name == self.SAMPLE_MODEL_NAME)
        self.assertIsInstance(model.rarity, Rarity)
        self.assertEqual(model.rarity, Rarity.LEGENDARY)

    def test_rarity_field_insert_int_works(self):
        model = RarityModel(
            name=self.SAMPLE_MODEL_NAME,
            rarity=4
        )
        model.save()

        model = self.get_sample_model()
        self.assertIsInstance(model.rarity, Rarity)
        self.assertEqual(model.rarity, Rarity.LEGENDARY)

    # HELPER METHODS
    # --------------

    def get_sample_model(self):
        return RarityModel.get(RarityModel.name == self.SAMPLE_MODEL_NAME)
