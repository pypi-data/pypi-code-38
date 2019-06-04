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
import os
import pandas as pd
from pandas import DataFrame
from sensiml.datamanager.featurefiles import FeatureFiles
from sensiml.datamanager.captures import Captures
from sensiml.datamanager.knowledgepack import KnowledgePack
from sensiml.datamanager.sandboxes import Sandboxes
from sensiml.datamanager.queries import Queries
from sensiml.method_calls.functioncall import FunctionCall
from sensiml.datamanager.capture_configurations import CaptureConfigurations
import sensiml.base.utility as utility


class Project(object):
    """Base class for a project."""
    _uuid = ''
    _name = ''
    _created = None
    _schema = {}
    _settings = {}
    _query_optimized = True

    def __init__(self, connection):
        """Initialize a project instance.

            Args:
                connection (connection object)
        """
        self._connection = connection
        self._feature_files = FeatureFiles(self._connection, self)
        self._captures = Captures(self._connection, self)
        self._sandboxes = Sandboxes(self._connection, self)
        self._queries = Queries(self._connection, self)
        self._plugin_config = None
        self._capture_configurations = CaptureConfigurations(
            self._connection, self)

    @property
    def uuid(self):
        """Auto generated unique identifier for the project object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def name(self):
        """Name of the project object"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def created(self):
        """Date of the project creation"""
        return self._created

    @created.setter
    def created(self, value):
        self._created = value

    @property
    def schema(self):
        """Schema of the project object"""
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    @property
    def plugin_config(self):
        """Plugin Config of the project object"""
        return self._plugin_config

    @plugin_config.setter
    def plugin_config(self, value):
        self._plugin_config = value

    @property
    def settings(self):
        """Global settings of the project object"""
        return self._settings

    @property
    def query_optimized(self):
        return self._query_optimized

    def add_segmenter(self, name, segmenter, preprocess=None, custom=False):
        """Saves a segmentation algorithm as the project's global segmentation setting.

            Args:
                name(str): Name to call the segmenter
                segmenter(FunctionCall): segmentation call object that the project will use by default
                preprocess(dict): Segment transforms to perform before segmenter
                custom(bool): a custom segmenter, or one of our server side segmenters


        """
        url = 'project/{0}/segmenter/'.format(self.uuid)
        if segmenter is not None:
            if not isinstance(segmenter, FunctionCall):
                print("segmenter is not a function call.")
                return
            segmenter_dict = segmenter._to_dict()
            if not segmenter_dict['type'] == 'segmenter':
                print("segmenter is not a function call for a segmenter")
                return
            parameters = json.dumps(segmenter_dict)
        else:
            parameters = None

        if not isinstance(custom, bool):
            print("Custom must either be true or false.")
            return

        if preprocess:
            if isinstance(preprocess, dict):
                preprocess = json.dumps(preprocess)

        segmenter_info = {'custom': custom,
                          'name': str(name),
                          'parameters': parameters,
                          'preprocess': preprocess
                          }

        request = self._connection.request('post', url, segmenter_info)
        response, err = utility.check_server_response(request)
        if err is False:
            print("Segmenter Uploaded.")
            return response

    def insert(self):
        """Calls the REST API to insert a new object, uses only the name and schema."""
        url = 'project/'
        project_info = {'name': self.name, 'capture_sample_schema': self.schema,
                        'settings': self.settings, 'plugin_config': self.plugin_config}
        request = self._connection.request('post', url, project_info)
        response, err = utility.check_server_response(request)
        if err is False:
            self.uuid = response['uuid']
            self._settings = response['settings']
            self._query_optimized = response.get('optimized', True)
            self.plugin_config = response['plugin_config']

    def update(self):
        """Calls the REST API to update the object."""
        url = 'project/{0}/'.format(self.uuid)
        project_info = {'name': self.name, 'capture_sample_schema': self.schema,
                        'settings': self.settings, 'plugin_config': self.plugin_config}
        request = self._connection.request('patch', url, project_info)
        response, err = utility.check_server_response(request)
        if err is False:
            self.plugin_config = response.get('plugin_config', None)

    def delete(self):
        """Calls the REST API to delete the object."""
        url = 'project/{0}/'.format(self.uuid)
        request = self._connection.request('delete', url,)
        response, err = utility.check_server_response(request)

    def refresh(self):
        """Calls the REST API and self populates from the server."""
        url = 'project/{0}/'.format(self.uuid)
        request = self._connection.request('get', url,)
        response, err = utility.check_server_response(request)
        if err is False:
            self.name = response['name']
            self.schema = response['capture_sample_schema']
            self._query_optimized = response.get('optimized', True)
            self.plugin_config = response.get('plugin_config', None)
            self.created = response.get('created_at', None)

    def query_optimize(self):
        """Calls the REST API and optimizes or re-optimizes the project for querying."""
        if not self.schema or not len(self._captures.get_captures()):
            print("Cannot query optimize {} until there are uploaded captures.".format(self._name) +
                  "If data was uploaded, try dsk.project.refresh() followed by dsk.project.query_optimize().")
        elif not self._query_optimized:
            print(
                "{} is not optimized for querying. Optimizing now...".format(self._name))
            self._create_profile()
        else:
            print("Re-optimizing {} for querying now...".format(self._name))
            self._delete_profile()
            self._create_profile()

    def _create_profile(self):
        """Calls the REST API and creates a profile for optimized query times."""
        url = 'project/{0}/profile/'.format(self.uuid)
        request = self._connection.request('post', url, )
        response, err = utility.check_server_response(request, is_octet=True)
        self.refresh()

    def _delete_profile(self):
        """Calls the REST API and drops the project profile."""
        url = 'project/{0}/profile/'.format(self.uuid)
        # Make a call to delete the profile
        request = self._connection.request('delete', url, )
        response, err = utility.check_server_response(request, is_octet=True)
        self.refresh()

    def get_knowledgepack(self, kp_uuid):
        """Gets the KnowledgePack(s) created by the sandbox.

            Returns:
                a KnowledgePack instance, list of instances, or None
        """
        url = 'project/{0}/knowledgepack/{1}/'.format(self.uuid, kp_uuid)
        response = self._connection.request('get', url,)
        response_data, err = utility.check_server_response(response)
        if err is False:
            kp = KnowledgePack(self._connection, self.uuid,
                               response_data.get('sandbox_uuid'))
            kp.initialize_from_dict(response_data)
            return kp

    def _get_knowledgepacks(self):
        """Gets the KnowledgePack(s) created by the sandbox.

            Returns:
                a KnowledgePack instance, list of instances, or None
        """
        url = 'project/{0}/knowledgepack/'.format(self.uuid)
        response = self._connection.request('get', url,)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return DataFrame(response_data)

    def list_knowledgepacks(self):
        """Lists all of the knowledgepacks associated with this project

        Returns:
            DataFrame: knowledpacks on kb cloud
        """
        knowledgepacks = self._get_knowledgepacks().rename(
            columns={'name': 'Name', 'project_name': 'Project', 'sandbox_name': 'Pipeline', 'uuid': 'kp_uuid', 'created_at': 'Created'})
        if len(knowledgepacks) < 1:
            print("No Knowledgepacks stored for this project on the cloud.")
            return None
        return knowledgepacks[knowledgepacks['Name'] != ''][['Name', 'Created', 'Project', 'Pipeline', 'kp_uuid']]

    def initialize_from_dict(self, dict):
        """Reads a json dict and populates a single project.

            Args:
                dict (dict): contains the project's 'name', 'uuid', 'schema', and 'settings' properties
        """
        self.uuid = dict['uuid']
        self.name = dict['name']
        self.schema = dict['capture_sample_schema']
        self._settings = dict.get('settings', [])
        self._query_optimized = dict.get('optimized', True)
        self.plugin_config = dict.get('plugin_config', None)
        self.created = dict.get('created_at', None)

    def __getitem__(self, key):
        if type(key) is str:
            return self.captures.get_capture_by_filename(key)
        else:
            return self.captures.get_captures()[key]

    @property
    def featurefiles(self):
        return self._feature_files

    @property
    def captures(self):
        return self._captures

    @property
    def sandboxes(self):
        return self._sandboxes

    @property
    def queries(self):
        return self._queries

    @property
    def capture_configurations(self):
        return self._capture_configurations

    def columns(self):
        """Returns the sensor columns available in the project.

            Returns:
                columns (list[str]): a list of string names of the project's sensor columns
        """
        try:
            columnnames = self.schema.keys()
            return columnnames
        except:
            return None

    def metadata_columns(self):
        """Returns the metadata columns available in the project.

            Returns:
                columns (list[str]): a list of string names of the project's metadata columns
        """
        return self.captures.get_metadata_names()

    def metadata_values(self):
        return self.captures.get_metadata_names_and_values()

    def label_values(self):
        return self.captures.get_label_names_and_values()

    def label_columns(self):
        """Returns the label columns available in the project.

            Returns:
                columns (list[str]): a list of string names of the project's metadata columns
        """
        return self.captures.get_label_names()

    def statistics(self):
        return self.captures.get_statistics()

    def get_active_pipelines(self):
        url = 'project/{0}/active/'.format(self.uuid)
        response = self._connection.request('get', url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            if response_data:
                return response_data

        return None

    def get_segmenters(self):
        url = 'project/{0}/segmenter/'.format(self.uuid)
        response = self._connection.request('get', url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            if response_data:
                return DataFrame(response_data).set_index('id')

        return None

    def convert_project_to_csv(self, dclprojpath, name=None, label_name=None, segmenter_id=None):
        """
        Args:
            dclprojpath: path to dcl project folder
            name (str): name of the dcl project folder. Defaults to current projects name.
            label_name: name of the label column. Defaults to current projects label column.
            segment_id: id of the segmenter folder to use.
        """

        if name is None:
            name = self.name

        dcl_project_name = os.path.join(dclprojpath, name)

        if not os.path.exists(dcl_project_name):
            print("Error: DCL project does not exist at " + dcl_project_name)
            return

        segmenters = None
        if segmenter_id is None:
            segmenters = self.get_segmenters()
            segmenter_id = int(input('Select Segementer ID\n\n' + '\n'.join(
                ["\t name: {}: id {}".format(x[0], x[1]) for x in zip(segmenters[['name']].values, segmenters.index)])+'\n'))

        if segmenter_id:
            if not os.path.exists(os.path.join(dcl_project_name, 'segments', str(segmenter_id))):
                print("Invalid Segmenter ID")
                return

        metadata_folder = os.path.join(dcl_project_name, 'metadata')
        segments_folder = os.path.join(
            dcl_project_name, 'segments', str(segmenter_id))
        data_folder = os.path.join(dcl_project_name, 'data')

        label_config = json.load(
            open(os.path.join(dcl_project_name, 'Label.config')))

        label_name = label_config['task_list'][0]['LabelName']

        root_names = [x[:-4]
                      for x in os.listdir(data_folder) if x[-4:] == '.csv']

        M = []
        for root_name in root_names:
            print('Reading File:', root_name)

            if not os.path.exists(os.path.join(segments_folder, root_name + '.sdcl')):
                print("No Segments for this Segmenter, Skipping.")
                continue

            tmp_df = pd.read_csv(os.path.join(data_folder, root_name + '.csv'))

            print("\tInitial Row #:", tmp_df.shape[0])

            # Set this to the Label you want to look at
            tmp_df[label_name] = None
            tmp_df['SegmentID'] = None
            tmp_df['filename'] = root_name

            segments = json.load(
                open(os.path.join(segments_folder, root_name + '.sdcl')))
            for segment in segments['DetectedSegments']:
                for label_data in segment['LabelData']:
                    tmp_df.loc[label_data["capture_sample_sequence_start"]:label_data['capture_sample_sequence_end'], label_data['name']] = label_data['value']

            tmp_df.dropna(subset=[label_name], inplace=True)

            if os.path.exists(os.path.join(metadata_folder, root_name + '.dcl')):
                metadata = json.load(
                    open(os.path.join(metadata_folder, root_name + '.dcl')))
                for meta in metadata['FileMetadata']:
                    tmp_df[meta['name']] = meta['value']

            print("\tSegments #:", len(tmp_df.SegmentID.unique()))
            print("\tFinal Row #:", tmp_df.shape[0])
            M.append(tmp_df)

        return pd.concat(M, sort=False).reset_index(drop=True)
