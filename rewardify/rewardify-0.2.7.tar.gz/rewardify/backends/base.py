# Standard library
import datetime

from typing import List, Dict, Any


# ###########################################
# THE INTERFACE FOR ALL BACKENDS TO IMPLEMENT
# ###########################################


class AbstractBackend:
    """
    This is the abstract base class, from which any concrete backend implementation has to inherit.
    It defines the simple "get_update" method, which has to be implemented to return the actions for which the
    users have earned gold.

    Each successive call to get_update should only return those actions, that are NEW since the last update, which
    means a backend has to keep track of which actions have already been processed and which were not.
    """

    def get_update(self) -> Dict[str, List]:
        """
        This is the main and only interface a concrete implementation of a gold providing backend has to satisfy. A
        call to this method should return a dictionary, where the key is the username of the user to update. The value
        to that username is supposed to be a list of dicts, where each dict describes an action, that has given the
        user the gold. The dicts, which describe these actions should contain the following keys:
        - name: Name of the action, that has granted the gold
        - description: Short description of the action
        - gold: The amount of gold, that was earned
        - date: A datetime object for the date, at which the action was completed

        :return:
        """
        raise NotImplementedError()


# #######################
# USEFUL MIXIN BEHAVIOURS
# #######################

class CheckConfigMixin:
    """
    This mixin provides the "check_config" function, which will go through all the variable names, the backend requires
    for correct functionality and checks of the EnvironmentConfig actually contains those.

    This mixin expects two things:
    - The class must implement the "get_config" method, which returns the EnvironmentConfig instance
    - The class must implement the "expected_config" method, which returns a list with all the variable names, that are
    required for the backend

    CHANGELOG

    Added 13.06.2019
    """

    def check_config(self):
        """
        This method will check if all the variables expected from the config file are actually defined in the config.
        self.EXPECTED_CONIFG contains the list with all the variable names.
        In case not all are defined a ModuleNotFoundError will be risen.

        CHANGELOG

        Added 10.06.2019

        Changed 13.06.2019
        This was originally only a method of the mock backend, but I found it so useful for other backends as well,
        that I made it it's own mixin

        .:raises: ModuleNotFoundError

        :return:
        """
        config = self.get_config()
        for variable in self.expected_config():
            if not hasattr(config, variable):
                raise ModuleNotFoundError("The config file is missing the %s variable!" % variable)

    def get_config(self):
        """
        Returns a reference to the EnvironmentConfig instance

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        raise NotImplementedError()

    def expected_config(self):
        """
        Returns a list with the string names of the expected variables for the backend

        CHANGELOG

        Added 13.06.2019

        :return:
        """
        raise NotImplementedError()
