##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017  SensiML Corporation.                                      #
#                                                                                #
#  The source code contained or  described  herein and all documents related     #
#  to the  source  code ("Material")  are  owned by SensiML Corporation or its   #
#  suppliers or licensors. Title to the Material remains with SensiML Corpora-   #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade      #
#  secrets and proprietary and confidential information of SensiML Corporation   #
#  and its suppliers and licensors, and is protected by worldwide copyright      #
#  and trade secret laws and treaty provisions. No part of the Material may      #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,     #
#  transmitted, distributed,  or disclosed in any way without SensiML's prior    #
#  express written permission.                                                   #
#                                                                                #
#  No license under any patent, copyright,trade secret or other intellectual     #
#  property  right  is  granted  to  or  conferred upon you by disclosure or     #
#  delivery of the Materials, either expressly, by implication,  inducement,     #
#  estoppel or otherwise.Any license under such intellectual property rights     #
#  must be express and approved by SensiML in writing.                           #
#                                                                                #
#  Unless otherwise agreed by SensiML in writing, you may not remove or alter    #
#  this notice or any other notice embedded in Materials by SensiML or SensiML's #
#  suppliers or licensors in any way.                                            #
#                                                                                #
##################################################################################


import json
from pandas import DataFrame, Series

from sensiml.datamanager.platformdescription import PlatformDescription
import sensiml.base.utility as utility


class PlatformDescriptions():
    """Base class for a collection of functions"""

    def __init__(self, connection):
        self._connection = connection
        self.build_platform_descriptions()

    def __getitem__(self, index):
        if len(self.platform_list) == 0:
            self.build_platform_descriptions()

        df = self()
        for p in self.platform_list:
            if index not in df.index:
                continue
            if df.loc[index].equals(p().loc[0]):
                return p
        return None

    def refresh(self):
        self.build_platform_descriptions()

    def build_platform_descriptions(self):
        """Populates the platform_list property from the server."""
        self.platform_list = []
        self.platform_dict = {}

        platforms = self.get_platforms()
        for platform in platforms:
            self.platform_dict['{} {}'.format(
                platform.board_name, platform.platform_version)] = platform
            self.platform_list.append(platform)

    def get_platform_by_name(self, name):
        if len(self.platform_list) == 0:
            self.build_platform_descriptions()
        return self.platform_dict.get(name, None)

    def get_platform_by_id(self, id):
        if len(self.platform_list) == 0:
            self.build_platform_descriptions()

        for platform in self.platform_list:
            if platform.id == id:
                return platform
        return None

    def _new_platform_description_from_dict(self, dict):
        """Creates and populates a function from a set of properties.

            Args:
                dict (dict): contains properties of a function

            Returns:
                function
        """
        function = PlatformDescription(self._connection)
        function.initialize_from_dict(dict)
        return function

    def get_platforms(self, function_type=''):
        """Gets all functions as function objects.

            Args:
                function_type (optional[str]): type of function to retrieve

            Returns:
                list of functions
        """
        url = 'platforms/'
        response = self._connection.request('get', url,)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        platformDescriptions = []
        for platformdesc in response_data:
            platformDescriptions.append(
                self._new_platform_description_from_dict(platformdesc))

        return platformDescriptions

    def __call__(self):
        return self.__str__()

    def __str__(self):
        all_platforms = self.get_platforms()
        if(len(all_platforms) < 0):
            return DataFrame()
        ret = DataFrame(p.__dict__() for p in all_platforms)
        # for plat in all_platforms:
        #     ret = ret.append(plat(), ignore_index=True)
        return ret.sort_values(by='Id').drop(labels=['Id'], axis=1)
