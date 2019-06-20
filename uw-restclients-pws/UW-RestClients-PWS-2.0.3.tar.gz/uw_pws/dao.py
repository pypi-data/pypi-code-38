"""
Contains UW PWS DAO implementations.
"""
from restclients_core.dao import DAO
from os.path import abspath, dirname
import os


class PWS_DAO(DAO):
    def service_name(self):
        return 'pws'

    def service_mock_paths(self):
        path = [abspath(os.path.join(dirname(__file__), "resources"))]
        return path
