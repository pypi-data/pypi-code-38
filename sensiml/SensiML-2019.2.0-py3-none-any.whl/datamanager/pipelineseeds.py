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

from sensiml.datamanager.pipelineseed import PipelineSeed
import sensiml.base.utility as utility


class PipelineSeeds():
    """Base class for a collection of pipeline seeds"""

    def __init__(self, connection):
        self._connection = connection
        self.build_pipeline_seeds()

    def __getitem__(self, index):
        return self.seed_list[index]

    def build_pipeline_seeds(self):
        """Populates the seed_list property from the server."""
        self.seed_list = []
        self.seed_dict = {}

        seeds = self.get_seeds()
        for seed in seeds:
            self.seed_dict[seed.name] = seed
            self.seed_list.append(seed)

    def get_seed_by_name(self, name):
        if len(self.seed_list) == 0:
            self.build_pipeline_seeds()
        return self.seed_dict.get(name, None)

    def _new_seed_from_dict(self, dict):
        """Creates and populates a seed from a set of properties.

            Args:
                dict (dict): contains properties of a Seed

            Returns:
                pipeline seed
        """
        seed = PipelineSeed(self._connection)
        seed.initialize_from_dict(dict)
        return seed

    def get_seeds(self):
        """Gets all seeds as seed objects.

            Returns:
                list of functions
        """
        url = 'seed/v2/'
        response = self._connection.request('get', url,)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        pipeline_seeds = []
        for seed in response_data:
            pipeline_seeds.append(self._new_seed_from_dict(seed))

        return pipeline_seeds

    def __call__(self):
        all_seeds = self.get_seeds()
        if (len(all_seeds) < 0):
            return DataFrame()
        ret = DataFrame(columns=['Name', 'Description'])
        for seed in all_seeds:
            ret = ret.append(seed(), ignore_index=True)
        ret = ret.set_index('Name').reset_index()
        return ret

    def __str__(self):
        output_string = 'Seeds are pipeline templates on the server that can be used to generate models \n' + \
                        'using the dsk.pipeline.auto() command. They eliminate the need to specify a \n' + \
                        'pipeline and are most effective when chosen appropriately for the application.\n\n'

        for seed in sorted(self.seed_list, key=lambda x: x.id):
            output_string += 'Name:          {0}\n'.format(seed.name)
            pipeline_format = '{} -> ' * len(seed.pipeline)
            output_string += 'Pipeline:      {0}\n\n'.format(
                pipeline_format.format(*[step['name'] for step in seed.pipeline])[:-3])
            output_string += '{0}\n\n'.format(seed.description)

        output_string += '\n'

        return output_string
