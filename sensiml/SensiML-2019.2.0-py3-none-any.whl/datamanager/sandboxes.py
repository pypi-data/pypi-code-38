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
from sensiml.datamanager.sandbox import Sandbox
import sensiml.base.utility as utility


class SandboxExistsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Sandboxes():
    """Base class for a collection of sandboxes."""

    def __init__(self, connection, project):
        self._connection = connection
        self._project = project

    def build_sandbox_list(self):
        """Populates the function_list property from the server."""
        sandbox_list = {}

        sandbox_response = self.get_sandboxes()
        for sandbox in sandbox_response:
            sandbox_list[sandbox.name] = sandbox

        return sandbox_list

    def get_or_create_sandbox(self, name):
        """Calls the REST API and gets the sandbox by name, if it doesn't exist insert a new sandbox

            Args:
                name (str): name of the sandbox

            Returns:
                sandbox object
        """
        sandbox = self.get_sandbox_by_name(name)

        if sandbox is None:
            print("Sandbox {} does not exist, creating a new sandbox.".format(name))
            sandbox = self.new_sandbox()
            sandbox.name = name
            sandbox.insert()

        return sandbox

    def create_sandbox(self, name, steps):
        """Creates a sandbox using the given name and steps

            Args:
                name (str): name of the sandbox
                steps (list[dict]): list of dictionaries specifying the pipeline steps

            Returns:
                sandbox object
        """
        if self.get_sandbox_by_name(name) is not None:
            raise SandboxExistsError(
                "sandbox {0} already exists.".format(name))
        else:
            sandbox = self.new_sandbox()
            sandbox.name = name
            sandbox._steps = steps
            sandbox.insert()
            return sandbox

    def get_sandbox_by_name(self, name):
        """Calls the REST API and gets the sandbox by name

            Args:
                name (str): name of the sandbox

            Returns:
                sandbox object
        """
        sandbox_list = self.get_sandboxes()
        for sandbox in sandbox_list:
            if sandbox.name == name:
                return sandbox
        return None

    def new_sandbox(self, dict={}):
        """Creates a new sandbox but does not insert in on the server

            Args:
                dict (optional[dict]): contains name and steps properties of the sandbox

            Returns:
                sandbox object
        """
        sandbox = Sandbox(self._connection, self._project)
        if len(dict) is not 0:
            sandbox.initialize_from_dict(dict)
        return sandbox

    def get_sandboxes(self):
        """Gets all sandboxes from server and turns them into local sandbox objects.

            Returns:
                list[sandbox]
        """
        # Query the server and get the json
        url = 'project/{0}/sandbox/'.format(self._project.uuid)
        response = self._connection.request('get', url,)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError as e:
            print(response)
        # Populate each sandbox from the server
        sandboxes = []
        if err is False:
            for sandbox_params in response_data:
                sandboxes.append(self.new_sandbox(sandbox_params))
        return sandboxes

    def __str__(self):
        output_string = 'Sandboxes:\n'
        for s in self.get_sandboxes():
            output_string += '    {0}\n'.format(s.name)

        return output_string
