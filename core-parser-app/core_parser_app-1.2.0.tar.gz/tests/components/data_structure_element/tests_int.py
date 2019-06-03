""" Integration test of Data structure element
"""
from bson.objectid import ObjectId

from core_main_app.commons import exceptions
from core_main_app.utils.integration_tests.integration_base_test_case import MongoIntegrationBaseTestCase
from core_parser_app.components.data_structure_element import api as api_data_structure_element
from core_parser_app.components.data_structure_element.models import DataStructureElement
# TODO: see why can't use from tests.components.data_structure_element.fixtures.fixtures import DataFixtures
from .fixtures.fixtures import DataFixtures, DataStructureElementMultipleLevelsFixture

fixture_data = DataFixtures()
fixture_multiple_levels_data = DataStructureElementMultipleLevelsFixture()


class TestDataStructureElementGetAll(MongoIntegrationBaseTestCase):
    fixture = fixture_data

    def test_data_structure_element_get_all_return_collection_of_data(self):
        # Act
        result = api_data_structure_element.get_all()
        # Assert
        self.assertTrue(all(isinstance(item, DataStructureElement) for item in result))

    def test_data_structure_element_get_all_return_all_data_structure_element_in_collection(self):
        # Act
        result = api_data_structure_element.get_all()
        # Assert
        self.assertTrue(len(self.fixture.data_structure_element_collection) == len(result))


class TestDataStructureElementGetById(MongoIntegrationBaseTestCase):
    fixture = fixture_data

    def test_data_get_by_id_raises_does_not_exist_error_if_not_found(self):
        # Act # Assert
        with self.assertRaises(exceptions.DoesNotExist):
            api_data_structure_element.get_by_id(ObjectId())

    def test_data_get_by_id_return_data_if_found(self):
        # Act
        result = api_data_structure_element.get_by_id(self.fixture.data_structure_element_collection[1].id)
        # Assert
        self.assertEqual(result, self.fixture.data_structure_element_collection[1])

    def test_data_get_by_id_raises_exception_if_fail(self):
        # Act # Assert
        with self.assertRaises(Exception):
            api_data_structure_element.get_by_id("")


class TestDataStructureElementGetByChildId(MongoIntegrationBaseTestCase):
    fixture = fixture_data

    def test_data_structure_element_get_by_child_id(self):
        # Act
        result = api_data_structure_element.get_all_by_child_id(self.fixture.data_structure_element_child_id_1)
        # Assert
        self.assertTrue(all(isinstance(item, DataStructureElement) for item in result))

    def test_data_get_by_child_id_raises_exception_if_fail(self):
        # Act # Assert
        with self.assertRaises(Exception):
            api_data_structure_element.get_all_by_child_id("")


class TestDataStructureElementGetRootElement(MongoIntegrationBaseTestCase):
    fixture = fixture_multiple_levels_data

    def test_get_root_element_returns_root_for_leaf(self):
        # Act
        result = api_data_structure_element.get_root_element(self.fixture.data_structure_element_1_1_2_1)
        # Assert
        self.assertEqual(result, self.fixture.data_structure_element_root)

    def test_get_root_element_returns_root_for_branch(self):
        # Act
        result = api_data_structure_element.get_root_element(self.fixture.data_structure_element_1_1)
        # Assert
        self.assertEqual(result, self.fixture.data_structure_element_root)

    def test_get_root_element_returns_root_for_root(self):
        # Act
        result = api_data_structure_element.get_root_element(self.fixture.data_structure_element_root)
        # Assert
        self.assertEqual(result, self.fixture.data_structure_element_root)

    def test_get_root_element_return_same_root_for_elements_of_same_tree(self):
        for element in [self.fixture.data_structure_element_root,
                        self.fixture.data_structure_element_1,
                        self.fixture.data_structure_element_2,
                        self.fixture.data_structure_element_1_1,
                        self.fixture.data_structure_element_1_1_1,
                        self.fixture.data_structure_element_1_1_2,
                        self.fixture.data_structure_element_1_1_3,
                        self.fixture.data_structure_element_1_1_2_1]:
            # Act
            result = api_data_structure_element.get_root_element(element)
            # Assert
            self.assertEqual(result, self.fixture.data_structure_element_root)
        for element in [self.fixture.data_structure_element_root_2,
                        self.fixture.data_structure_element_test]:
            # Act
            result = api_data_structure_element.get_root_element(element)
            # Assert
            self.assertEqual(result, self.fixture.data_structure_element_root_2)
