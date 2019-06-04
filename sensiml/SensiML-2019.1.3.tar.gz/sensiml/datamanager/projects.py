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


from sensiml.datamanager.project import Project
import sensiml.base.utility as utility


class ProjectExistsError(Exception):
    """Base class for a project exists error"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Projects():
    """Base class for a collection of projects."""

    def __init__(self, connection):
        self._connection = connection

    def create_project(self, name):
        """Creates a project using the name property.

            Args:
                name (str): name of the new project

            Returns:
                project

            Raises:
                ProjectExistsError, if the project already exists on the server
        """
        if self.get_project_by_name(name) is not None:
            raise ProjectExistsError(
                "project {0} already exists.".format(name))
        else:
            project = self.new_project()
            project.name = name
            project.insert()
            return project

    def get_or_create_project(self, name):
        """Calls the REST API and gets the project by name, if it doesn't exist insert a new project

            Args:
                name (str): name of the project

            Returns:
                project object
        """
        project = self.get_project_by_name(name)

        if project is None:
            print("Project {} does not exist, creating a new project.".format(name))
            project = self.create_project(name)

        return project

    def get_project_by_name(self, name):
        """gets a project from the server using its name property

            Args:
                name (str): name of the project

            Returns:
                project or None if project does not exist
        """
        project_list = self.get_projects()
        for project in project_list:
            if project.name == name:
                if project.schema and not project.query_optimized:
                    if len(project._captures.get_captures()):
                        project.query_optimize()
                return project

        return None

    def __getitem__(self, key):
        return self.get_project_by_name(key)

    def new_project(self, dict={}):
        """Creates a new project.

            Args:
                dict (dict): dictionary containing the attributes of the new project

            Returns:
                project
        """
        project = Project(self._connection)
        if len(dict) is not 0:
            project.initialize_from_dict(dict)
        return project

    def get_projects(self):
        """Gets all projects from the server as project objects.

            Returns:
                list[project]
        """
        url = 'project/'
        response = self._connection.request('get', url,)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        projects = []
        if err is False:
            # Populate each project from the server if there was no error.
            for project_params in response_data:
                projects.append(self.new_project(project_params))

        return projects
