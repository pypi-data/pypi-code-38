import os
import utils.graph_utils as graph
import utils.utils as utils
import unittest
from unittest.mock import patch, Mock
from unittest import TestCase

class TestGraphUtils(TestCase):
    """
    Tests for GraphUtils class
    """
    def test_visualize_using_boxplot_null_data(self):
        # GraphUtils can be passed any version (can be dummy) for testing
        utils = graph.GraphUtils('17.0(6136089)', '16.3(6135950)')
        result = utils.visualize_using_boxplot(None, 2, 10, 3500)
        assert result == None

    def test_visualize_using_boxplot2_null_data(self):
        # GraphUtils can be passed any version (can be dummy) for testing
        utils = graph.GraphUtils('17.0(6136089)', '16.3(6135950)')
        result = utils.visualize_using_boxplot(None, 2, 3750, None)
        assert result == None

    def test_visualize_using_voilinplot_null_data(self):
        utils = graph.GraphUtils('17.0(6136089)', '16.3(6135950)')
        result = utils.visualize_using_voilinplot(None, 2, 10)
        assert result == None

    def test_cmp_aura_flexipage_null_data(self):
        utils = graph.GraphUtils('17.0(6136089)', '16.3(6135950)')
        result = utils.cmp_aura_flexipage(None, 3500)
        assert result == None

    def test_cmp_network_null_data(self):
        utils = graph.GraphUtils('17.0(6136089)', '16.3(6135950)')
        result = utils.cmp_network(None, 3500)
        assert result == None

    def test_visualize_using_boxplot_invalid_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        gutils = graph.GraphUtils('17.0(6136089)', '16.3(6135950)')
        result = gutils.visualize_using_boxplot(data, 2, 10, 3500)
        assert result == None  

    def test_visualize_using_voilinplot_invalid_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        gutils = graph.GraphUtils('17.0(6136089)', '16.3(6135950)')
        result = gutils.visualize_using_voilinplot(data, 2, 10)
        assert result == None  

    def test_cmp_aura_flexipage_invalid_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        gutils = graph.GraphUtils('17.0(6136089)', '16.3(6135950)')
        result = gutils.cmp_aura_flexipage(data, 3500)
        assert result == None

    def test_cmp_network_invalid_data(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        dirpath = dirpath + "/data/"

        data = utils.load_file(dirpath, "File_Data.csv")
        gutils = graph.GraphUtils('17.0(6136089)', '16.3(6135950)')
        result = gutils.cmp_network(data, 3500)
        assert result == None