__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "Sritej K V R <skanakad@cisco.com>"



from unicon.bases.routers.connection_provider import BaseSingleRpConnectionProvider
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxr.spitfire.statements import connection_statement_list 
from unicon import log



class SpitfireSingleRpConnectionProvider(BaseSingleRpConnectionProvider):
    """ Implements Generic singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)

    # def connect(self):
    #     print('connecting from connection provider')
    #
    # def disconnect(self):
    #     print('disconnecting from connection provider')

    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device
            Any additional Statements(prompts) to be handled during
            initial connection has to be updated here,
            connection provider uses this method to fetch connection
            dialog
        """
        return Dialog(connection_statement_list)

