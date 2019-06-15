# Standard library
from unittest import TestCase

# Third party
from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField

# Local imports
from rewardify.rarity import Rarity

from rewardify.probability import RarityProbability
from rewardify.probability import ProbabilityField


class TestRarityProbability(TestCase):

    SAMPLE_VALUE = 0.25
    SAMPLE_VALUE_LIST = [SAMPLE_VALUE] * 4

    # THE ACTUAL TEST CASES
    # ---------------------

    def test_construction_works(self):
        rarity_probability = RarityProbability(0.25, 0.25, 0.25, 0.25)
        self.assertIsInstance(rarity_probability, RarityProbability)

    def test_indexing_with_rarity_works(self):
        rarity_probability = self.get_sample_object()

        # Now we are testing the various methods to index a RarityProbability object
        self.assertEqual(rarity_probability[1], self.SAMPLE_VALUE)
        self.assertEqual(rarity_probability['common'], self.SAMPLE_VALUE)
        self.assertEqual(rarity_probability[Rarity('common')], self.SAMPLE_VALUE)

    def test_converting_into_list(self):
        rarity_probability = self.get_sample_object()

        probability_list = rarity_probability.list()
        self.assertListEqual(probability_list, self.SAMPLE_VALUE_LIST)

    def test_creating_from_list(self):
        rarity_probability = RarityProbability.from_iterable(self.SAMPLE_VALUE_LIST)

        self.assertEqual(rarity_probability['common'], self.SAMPLE_VALUE)

    def test_creating_csv_string_from_object(self):
        expected_string = '0.25,0.25,0.25,0.25'
        rarity_probability = self.get_sample_object()

        csv_string = rarity_probability.csv(accuracy=2)
        self.assertEqual(csv_string, expected_string)

    def test_creating_object_from_csv_string(self):
        csv_string = '0.5,0.3,0.1,0.1'
        rarity_probability = RarityProbability.from_csv(csv_string)

        self.assertEqual(rarity_probability['common'], 0.5)

    def test_equals(self):
        rarity_probability1 = RarityProbability(0.25, 0.25, 0.25, 0.25)
        rarity_probability2 = RarityProbability(0.25, 0.25, 0.25, 0.25)
        rarity_probability3 = RarityProbability(0.7, 0.1, 0.1, 0.1)

        # objects 1 and 2 must be equal. Object 3 is different
        self.assertEqual(rarity_probability1, rarity_probability2)
        self.assertNotEqual(rarity_probability1, rarity_probability3)

    def test_choice(self):
        rarity_probability = RarityProbability(0.25, 0.25, 0.25, 0.25)
        result = rarity_probability.choice()
        self.assertTrue(result in Rarity.RARITIES)

    # HELPER METHODS
    # --------------

    def get_sample_object(self):
        return RarityProbability(self.SAMPLE_VALUE, self.SAMPLE_VALUE, self.SAMPLE_VALUE, self.SAMPLE_VALUE)


# TESTING THE PROBABILITY FIELD
# -----------------------------


class ProbabilityModel(Model):

    name = CharField()
    slot = ProbabilityField()


class TestProbabilityField(TestCase):
    TEST_DATABASE = SqliteDatabase(':memory:')
    MODELS = [ProbabilityModel]

    SAMPLE_MODEL_NAME = 'sample'
    SAMPLE_RARITY_PROBABILITY = RarityProbability(0.25, 0.25, 0.25, 0.25)

    # SETTING UP THE TEST DATABASE
    # ----------------------------

    def setUp(self):
        self.TEST_DATABASE.bind(self.MODELS, bind_refs=False, bind_backrefs=False)

        self.TEST_DATABASE.connect()
        self.TEST_DATABASE.create_tables(self.MODELS)

    def tearDown(self):
        self.TEST_DATABASE.drop_tables(self.MODELS)
        self.TEST_DATABASE.close()

    # ACTUAL TEST CASES
    # -----------------

    def test_model_creation_works(self):
        # Saving the model into the database
        model = ProbabilityModel(
            name=self.SAMPLE_MODEL_NAME,
            slot=RarityProbability(0.25, 0.25, 0.25, 0.25)
        )
        model.save()

        # Loading the model again from the database
        model = ProbabilityModel.get(ProbabilityModel.name == self.SAMPLE_MODEL_NAME)
        self.assertIsInstance(model.slot, RarityProbability)

    def test_model_creation_works_with_list(self):
        model = ProbabilityModel(
            name=self.SAMPLE_MODEL_NAME,
            slot=[0.5, 0.2, 0.2, 0.1]
        )
        model.save()

        model = self.get_sample_model()
        self.assertEqual(model.slot['common'], 0.5)
        self.assertEqual(model.slot['legendary'], 0.1)

    # HELPER METHODS
    # --------------

    def get_sample_model(self):
        return ProbabilityModel.get(ProbabilityModel.name == self.SAMPLE_MODEL_NAME)
