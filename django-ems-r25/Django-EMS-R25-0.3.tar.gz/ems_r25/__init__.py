import os
from os.path import abspath, dirname

from restclients_core.dao import MockDAO
from ems_client.mock import EMSMockData

MockDAO.register_mock_path(os.path.join(
    abspath(dirname(__file__)), "resources"))

EMSMockData.register_mock_path(os.path.join(
    abspath(dirname(__file__)), "resources"))
