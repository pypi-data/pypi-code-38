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
from sensiml.datamanager.query import Query
import sensiml.base.utility as utility


class QueryExistsError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Queries(object):
    """Base class for a collection of queries."""

    def __init__(self, connection, project):
        self._connection = connection
        self._project = project

    def build_query_list(self):
        """Populates the function_list property from the server."""
        query_list = {}

        query_response = self.get_queries()
        for query in query_response:
            query_list[query.name] = query

        return query_list

    def create_query(self, name, columns=None, metadata_columns=None, metadata_filter='', label_column=''):
        """Creates a query with the given input properties and inserts it onto the server

            Args:
                name (str): name of the query
                columns (list[str]): sensor columns to select
                metadata_columns (list(str]): metadata columns to select
                metadata_filter (str): specifies one or more metadata filter conditions

            Returns:
                query object
        """
        if self.get_query_by_name(name) is not None:
            raise QueryExistsError("Query {0} already exists.".format(name))
        else:
            query = self.new_query()
            query.name = name
            query.columns = columns
            query.metadata_columns = metadata_columns
            query.eventlabel_columns = "NULL"
            query.metadata_filter = metadata_filter
            query.label_column = label_column
            query.insert()
            return query

    def get_or_create_query(self, name):
        """Calls the REST API and gets the query by name, if it doesn't exist insert a new query

            Args:
                name (str): name of the query

            Returns:
                query object
        """
        query = self.get_query_by_name(name)

        if query is None:
            print("Query {} does not exist, creating a new query.".format(name))
            query = self.new_query()
            query.name = name
            query.insert()

        return query

    def get_query_by_name(self, name):
        """Retrieves a query by name from the server, if it exists

            Args:
                name (str)

            Returns:
                query object or None
        """
        query_list = self.get_queries()
        for query in query_list:
            if query.name == name:
                return query
        return None

    def new_query(self):
        """Initializes a new query for the project, but does not assign property values or insert it into the server"""
        query = Query(self._connection, self._project)
        return query

    def _new_query_from_dict(self, dict):
        """Creates a query object using a dictionary (e.g. one retrieved from the server)

            Args:
                dict (dict): dictionary of query properties
                                - name
                                - columns
                                - metadata_columns
                                - metadata_filter

            Returns:
                query object
        """
        query = self.new_query()
        query.initialize_from_dict(dict)
        return query

    def get_queries(self):
        """Gets all project queries from the server and creates corresponding local query objects

            Returns:
                list[query]
        """
        # Query the server and get the json
        url = 'project/{0}/query/'.format(self._project.uuid)
        response = self._connection.request('get', url,)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        # Populate each eventlabel from the server
        queries = []
        if err is False:
            try:
                for query_params in response_data:
                    queries.append(self._new_query_from_dict(query_params))
            except Exception as e:
                print(e)
        return queries

    def __str__(self):
        output_string = 'Queries:\n'
        for q in self.get_queries():
            output_string += '    {0}\n'.format(q.name)

        return output_string

    def __getitem__(self, key):
        return self.get_query_by_name(key).__str__()
