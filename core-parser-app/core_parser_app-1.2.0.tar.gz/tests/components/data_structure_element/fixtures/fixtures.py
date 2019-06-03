""" fixtures files for Data Structure Element
"""
from core_main_app.utils.integration_tests.fixture_interface import FixtureInterface
from core_parser_app.components.data_structure_element.models import DataStructureElement


class DataFixtures(FixtureInterface):
    """ Represents Data structure element fixtures
    """
    data_structure_element_child_id_1 = None
    data_structure_element_child_3 = None
    children_2 = None
    data_structure_element_collection = None

    def insert_data(self):
        """ Insert a set of Data

        Returns:

        """
        # Make a connexion with a mock database
        self.generate_data_structure_element()

    def generate_data_structure_element(self):
        """ Insert three elements in mock database with different tag and value

        two of them have same children
        two of then have same options

        Returns:

        """
        # children build
        data_structure_element_child_1 = DataStructureElement('tag_child_1', 'value_child_1').save()
        data_structure_element_child_2 = DataStructureElement('tag_child_2', 'value_child_2').save()
        children_1 = [data_structure_element_child_1, data_structure_element_child_2]
        self.data_structure_element_child_id_1 = data_structure_element_child_1.id
        self.data_structure_element_child_3 = DataStructureElement('tag_child_3', 'value_child_3').save()
        data_structure_element_child_4 = DataStructureElement('tag_child_4', 'value_child_4').save()
        self.children_2 = [self.data_structure_element_child_3, data_structure_element_child_4]

        # option build
        data_structure_element_option_1 = {"opt_1_1": "value_opt_1", "opt_1_2": "value_opt_2"}
        data_structure_element_option_2 = {"opt_2_1": "value_opt_1", "opt_2_2": "value_opt_2"}

        # insert two complete data structure element
        data_structure_element_1 = DataStructureElement('tag1',
                                                        'value1',
                                                        data_structure_element_option_1,
                                                        children_1).save()
        data_structure_element_2 = DataStructureElement('tag2',
                                                        'value2',
                                                        data_structure_element_option_2,
                                                        self.children_2).save()
        data_structure_element_3 = DataStructureElement('tag3',
                                                        'value3',
                                                        data_structure_element_option_2,
                                                        self.children_2).save()

        # build a collection of data structure element
        self.data_structure_element_collection = [data_structure_element_child_1,
                                                  data_structure_element_child_2,
                                                  self.data_structure_element_child_3,
                                                  data_structure_element_child_4,
                                                  data_structure_element_1,
                                                  data_structure_element_2,
                                                  data_structure_element_3]


class DataStructureElementMultipleLevelsFixture(FixtureInterface):
    """ Represents Data structure element fixtures
    """
    data_structure_element_1_1_2_1 = None
    data_structure_element_1_1_1 = None
    data_structure_element_1_1_2 = None
    data_structure_element_1_1_3 = None
    data_structure_element_1_1 = None
    data_structure_element_1 = None
    data_structure_element_2 = None
    data_structure_element_root = None
    data_structure_element_test = None
    data_structure_element_root_2 = None
    data_structure_element_collection = None

    def insert_data(self):
        """ Insert a set of Data

        Returns:

        """
        # Make a connexion with a mock database
        self.generate_data_structure_element()

    def generate_data_structure_element(self):
        """ Insert data structure elements on multiple levels in mock database

        Example::

            Root -> 1 -> 1_1 -> 1_1_1
                             -> 1_1_2 -> 1_1_2_1
                             -> 1_1_3
                 -> 2

            Root2 -> test


        Returns:

        """
        # children build

        self.data_structure_element_1_1_2_1 = DataStructureElement('tag_1_1_2_1',
                                                                   'value_1_1_2_1').save()

        self.data_structure_element_1_1_1 = DataStructureElement('tag_1_1_1',
                                                                 'value_1_1_1').save()
        self.data_structure_element_1_1_2 = DataStructureElement('tag_1_1_2',
                                                                 'value_1_1_2',
                                                                 children=[self.data_structure_element_1_1_2_1]).save()
        self.data_structure_element_1_1_3 = DataStructureElement('tag_1_1_3',
                                                                 'value_1_1_3').save()

        self.data_structure_element_1_1 = DataStructureElement('tag_1_1',
                                                               'value_1_1',
                                                               children=[self.data_structure_element_1_1_1,
                                                                         self.data_structure_element_1_1_2,
                                                                         self.data_structure_element_1_1_3]).save()

        self.data_structure_element_1 = DataStructureElement('tag_1',
                                                             'value_1',
                                                             children=[self.data_structure_element_1_1]).save()

        self.data_structure_element_2 = DataStructureElement('tag_2',
                                                             'value_2').save()

        self.data_structure_element_root = DataStructureElement('root',
                                                                'root',
                                                                children=[self.data_structure_element_1,
                                                                          self.data_structure_element_2]).save()

        self.data_structure_element_test = DataStructureElement('test',
                                                                'test').save()

        self.data_structure_element_root_2 = DataStructureElement('root2',
                                                                  'root2',
                                                                  children=[self.data_structure_element_test]).save()

        # build a collection of data structure element
        self.data_structure_element_collection = [self.data_structure_element_root,
                                                  self.data_structure_element_1,
                                                  self.data_structure_element_2,
                                                  self.data_structure_element_1_1,
                                                  self.data_structure_element_1_1_1,
                                                  self.data_structure_element_1_1_2,
                                                  self.data_structure_element_1_1_3,
                                                  self.data_structure_element_1_1_2_1,
                                                  self.data_structure_element_root_2,
                                                  self.data_structure_element_test]
