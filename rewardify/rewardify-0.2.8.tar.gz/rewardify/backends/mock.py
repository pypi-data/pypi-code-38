# Standard library
import datetime

from typing import List, Dict, Any

# local imports
from rewardify.env import EnvironmentConfig

from rewardify.backends.base import AbstractBackend, CheckConfigMixin


class MockBackend(CheckConfigMixin, AbstractBackend):
    """
    This is a mock object for testing purposes. It implements the AbstractBackend.
    For every call to the get_update() method it will return a list of exactly one action granting 100
    gold to every user, that is specified in the config variable MOCK_BACKEND_USERS.

    CHANGELOG

    Added 10.09.2019

    Changed 13.06.2019
    Removed the method "check_config" and created the "CheckConfigMixin" from that. This class now inherits from this
    mixin, thus retaining the method.
    """

    # THE CONFIG ACCESS
    # -----------------

    # This is a list of all the variable names, this backend expects to be defined in the config file to the program
    EXPECTED_CONFIG = [
        'MOCK_BACKEND_USERS'
    ]

    # A reference to the config singleton
    CONFIG: EnvironmentConfig = EnvironmentConfig.instance()

    # CLASS CONSTANTS
    # ---------------

    # This is the action description dict, which will be given to every user on the call of the
    # "get_update" method
    MOCK_ACTION = {
        'name':             'Mockery',
        'description':      'For doing absolutely nothing!',
        'gold':             100,
        'date':             datetime.datetime.now()
    }

    # INSTANCE CONSTRUCTION
    # ---------------------

    def __init__(self):
        """
        The constructor.

        CHANGELOG

        Added 10.09.2019
        """
        # This method will check if all the variables expected from the config file are actually defined in the config
        # file and will raise an exception, if that is not the case.
        self.check_config()

    def get_update(self):
        """
        This method returns the update dict as defined by the abstract base class

        CHANGELOG

        Added 10.06.2019

        :return:
        """
        update_dict = {}
        for user in self.CONFIG.MOCK_BACKEND_USERS:
            update_dict[user] = [self.MOCK_ACTION]
        return update_dict

    # IMPLEMENTING MIXIN REQUIREMENTS
    # -------------------------------

    def get_config(self):
        """
        Returns an instance of the EnvironmentConfig instance

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        return self.CONFIG

    def expected_config(self):
        """
        Returns a list with the string names of the expected variables from the config object

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        return self.EXPECTED_CONFIG
