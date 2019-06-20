# -*- coding: utf-8 -*-

"""
OMXWare SDK
"""

import sys
from datetime import datetime, timedelta

from omxware import omxware
from omxware.exceptions.InvalidParamsException import InvalidParamsError
from omxware.utils.AESCipher import AESCipher
from omxware.utils.SecUtils import rand

token = ''


def get_token(username, password):
    """
    Verify the credentials and get a User Token

    Parameters:
            :param username: OMXWare username. This is different from your IBM Id username
            :type username: str

            :param password: OMXWare password. This is different from your IBM Id's password
            :type password: str

    Returns:
        OMXWare user token

    Raises:
        KeyError: Raises an exception.
    """

    if username is None:
        sys.exit("Username cannot be empty!")

    if password is None:
        sys.exit("Password cannot be empty!")

    # Verify username and password

    cipher = AESCipher()
    omxware_token = cipher.encrypt(rand() + "::::" + username + "::::" + password)

    return omxware_token


class OmxwareDev(omxware):
    PAGE_SIZE_DEFAULT = 25
    PAGE_INDEX_DEFAULT = 1

    def __init__(self, omxware_token, env='master'):
        """
        Initialize an OMXWare session.

        Parameters:
            :param omxware_token: OMXWare Token. use
            :type omxware_token: str

            :param env: OMXWare `env` type. Must be one of ['master', 'dev', 'dev_search', 'local']
            :type env: str
        """

        super().__init__(omxware_token, env)

# User
    def whoami(self):
        """
        Get OMXWare User info .

        Returns:
            :return:    OmxResponse :   User
        """
        try:

            self._init_omx_connection()
            methodurl = "/api/secure/user/profile"

            headers = {'content-type': 'application/json',
                       'content-language': 'en-US',
                       'accept': 'application/json'}

            params = {}

            resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
            return resp
        except InvalidParamsError as ex:
            print("\nERROR: " + str(ex))
            help(self.whoami)

# OMXWare Registrations / Login Metrics
    def events(self, type=None, lastNdays=30, page_size=50000, page_nummber=1):
        """
        Get OMXWare User Events

        Parameters:
            :param: type:   str:    Must be one of { 'login', 'register' }
            :param: lastNdays:  int:    last N days to query the events


        Returns:
            :return:    OmxResponse :   User
        """
        try:
            today = datetime.today().strftime('%Y-%m-%d')
            date_N_days_ago = (datetime.today() - timedelta(days=lastNdays)).strftime('%Y-%m-%d')

            if type is not None:
                self._init_omx_connection()
                methodurl = '/api/secure/admin/omx-user-stats/from/' + date_N_days_ago + '/to/' + today + '/size/' + str(page_size) + '/page/' + str(page_nummber) + '?event_type='+type

                headers = {'content-type': 'application/json',
                           'content-language': 'en-US',
                           'accept': 'application/json'}

                params = {}

                resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
                return resp

            else:
                return None
        except InvalidParamsError as ex:
            print("\nERROR: " + str(ex))
            help(self.events)
            return None

# OMXWare Jobs for current user
#     def jobs(self, type=None, lastNdays=30, page_size=50000, page_nummber=1):
#         """
#         Get OMXWare User Events
#
#         Parameters:
#             :param: type:   str:    Must be one of { 'login', 'register' }
#             :param: lastNdays:  int:    last N days to query the events
#
#
#         Returns:
#             :return:    OmxResponse :   User
#         """
#         try:
#             today = datetime.today().strftime('%Y-%m-%d')
#             date_N_days_ago = (datetime.today() - timedelta(days=lastNdays)).strftime('%Y-%m-%d')
#
#             if type is not None:
#                 self._init_omx_connection()
#                 methodurl = '/api/secure/admin/omx-user-stats/from/' + date_N_days_ago + '/to/' + today + '/size/' + str(page_size) + '/page/' + str(page_nummber) + '?event_type='+type
#
#                 headers = {'content-type': 'application/json',
#                            'content-language': 'en-US',
#                            'accept': 'application/json'}
#
#                 params = {}
#
#                 resp = self.connection.get(methodurl=methodurl, headers=headers, payload=params)
#                 return resp
#
#             else:
#                 return None
#         except InvalidParamsError as ex:
#             print("\nERROR: " + str(ex))
#             help(self.events)
#             return None
