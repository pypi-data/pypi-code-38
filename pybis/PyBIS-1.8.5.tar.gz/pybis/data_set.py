#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
data_set.py

Module with functions for operating on data sets.


Created by Chandrasekhar Ramakrishnan on 2017-04-05.
Copyright (c) 2017 Chandrasekhar Ramakrishnan. All rights reserved.
"""


def transfer_to_file_creation(content, file_creation, key, file_creation_key=None):
    if file_creation_key is None:
        file_creation_key = key
    if content.get(key) is not None:
        file_creation[file_creation_key] = content[key]


class GitDataSetCreation(object):
    def __init__(self, openbis, data_set_type, path, commit_id, repository_id, dms, sample=None, experiment = None,
                 properties={}, dss_code=None, parents=None, data_set_code=None, contents=[]):
        """Initialize the command object with the necessary parameters.
        :param openbis: The openBIS API object.
        :param data_set_type: The type of the data set
        :param path: The path to the git repository
        :param commit_id: The git commit id
        :param repository_id: The git repository id - same for copies
        :param dms: An external data managment system object or external_dms_id
        :param sample: A sample object or sample id.
        :param experiment: An experiment or experiment id.
        :param properties: Properties for the data set.
        :param dss_code: Code for the DSS -- defaults to the first dss if none is supplied.
        :param parents: Parents for the data set.
        :param data_set_code: A data set code -- used if provided, otherwise generated on the server
        :param contents: A list of dicts that describe the contents:
            {'fileLength': [file length],
             'crc32': [crc32 checksum],
             'checksum': [checksum other than crc32],
             'checksumType': [checksum type if fiels checksum is used],
             'directory': [is path a directory?]
             'path': [the relative path string]}

        """
        self.openbis = openbis
        self.data_set_type = data_set_type
        self.path = path
        self.commit_id = commit_id
        self.repository_id = repository_id
        self.dms = dms
        self.sample = sample
        self.experiment = experiment
        self.properties = properties
        self.dss_code = dss_code
        self.parents = parents
        self.data_set_code = data_set_code
        self.contents = contents

    def new_git_data_set(self):
        """ Create a link data set.
        :return: A DataSet object
        """

        data_set_creation = self.data_set_metadata_creation()
        file_metadata = self.data_set_file_metadata()
        if not file_metadata:
            return self.create_pure_metadata_data_set(data_set_creation)
        return self.create_mixed_data_set(data_set_creation, file_metadata)

    def create_pure_metadata_data_set(self, data_set_creation):
        # register the files in openBIS
        request = {
            "method": "createDataSets",
            "params": [
                self.openbis.token,
                [data_set_creation]
            ]
        }

        # noinspection PyProtectedMember
        resp = self.openbis._post_request(self.openbis.as_v3, request)
        return self.openbis.get_dataset(resp[0]['permId'])

    def create_mixed_data_set(self, metadata_creation, file_metadata):
        data_set_creation = {
            "fileMetadata": file_metadata,
            "metadataCreation": metadata_creation,
            "@type": "dss.dto.dataset.create.FullDataSetCreation"
        }

        # register the files in openBIS
        request = {
            "method": "createDataSets",
            "params": [
                self.openbis.token,
                [data_set_creation]
            ]
        }

        server_url = self.data_store_url(metadata_creation['dataStoreId']['permId'])
        # noinspection PyProtectedMember
        resp = self.openbis._post_request_full_url(server_url, request)
        return self.openbis.get_dataset(resp[0]['permId'])

    def data_store_url(self, dss_code):
        data_stores = self.openbis.get_datastores()
        data_store = data_stores[data_stores['code'] == dss_code]
        return "{}/datastore_server/rmi-data-store-server-v3.json".format(data_store['downloadUrl'][0])

    def data_set_metadata_creation(self):
        """Create the respresentation of the data set metadata."""
        dss_code = self.dss_code
        if dss_code is None:
            dss_code = self.openbis.get_datastores()['code'][0]

        dms_id = self.openbis.external_data_managment_system_to_dms_id(self.dms)
        parents = self.parents
        parentIds = []
        if parents is not None:
            if not isinstance(parents, list):
                parents = [parents]
            parentIds = [self.openbis.data_set_to_data_set_id(parent) for parent in parents]
        data_set_creation = {
            "linkedData": {
                "@type": "as.dto.dataset.create.LinkedDataCreation",
                "contentCopies": [
                    {
                        "@type": "as.dto.dataset.create.ContentCopyCreation",
                        "path": self.path,
                        "gitCommitHash": self.commit_id,
                        "gitRepositoryId" : self.repository_id,
                        "externalDmsId": dms_id
                    }
                ]
            },
            "typeId": {
                "@type": "as.dto.entitytype.id.EntityTypePermId",
                "permId": self.data_set_type
            },
            "dataStoreId": {
                "permId": dss_code,
                "@type": "as.dto.datastore.id.DataStorePermId"
            },
            "parentIds": parentIds,
            "measured": False,
            "properties": self.properties,
            "@type": "as.dto.dataset.create.DataSetCreation"
        }

        if self.sample is not None:
            sample_id = self.openbis.sample_to_sample_id(self.sample)
            data_set_creation['sampleId'] = sample_id
        elif self.experiment is not None:
            experiment_id = self.openbis.experiment_to_experiment_id(self.experiment)
            data_set_creation['experimentId'] = experiment_id

        if self.data_set_code is not None:
            data_set_creation['code'] = self.data_set_code
            data_set_creation["autoGeneratedCode"] = False
        else:
            data_set_creation["autoGeneratedCode"] = True

        return data_set_creation

    def data_set_file_metadata(self):
        """Create a representation of the file metadata"""
        return [self.as_file_metadata(c) for c in self.contents]

    def as_file_metadata(self, content):
        # The DSS objects do not use type
        # result = {"@type": "dss.dto.datasetfile.DataSetFileCreation"}
        result = {}
        transfer_to_file_creation(content, result, 'fileLength')
        transfer_to_file_creation(content, result, 'crc32', 'checksumCRC32')
        transfer_to_file_creation(content, result, 'checksum', 'checksum')
        transfer_to_file_creation(content, result, 'checksumType', 'checksumType')
        transfer_to_file_creation(content, result, 'directory')
        transfer_to_file_creation(content, result, 'path')
        return result


class GitDataSetUpdate(object):

    def __init__(self, openbis, data_set_id):
        """Initialize the command object with the necessary parameters.
        :param openbis: The openBIS API object.
        :param data_set_id: Id of the data set to be updated
        """
        self.openbis = openbis
        self.data_set_id = data_set_id

    def new_content_copy(self, path, commit_id, repository_id, edms_id):
        """ Create a data set update for adding a content copy.
        :return: A DataSetUpdate object
        """
        self.path = path
        self.commit_id = commit_id
        self.repository_id = repository_id
        self.edms_id =edms_id
        
        content_copy_actions = self.get_actions_add_content_copy()
        data_set_update = self.get_data_set_update(content_copy_actions)
        self.send_request(data_set_update)

    def delete_content_copy(self, content_copy):
        """ Deletes the given content_copy from openBIS.
        :param content_copy: Content copy to be deleted.
        """
        content_copy_actions = self.get_actions_remove_content_copy(content_copy)
        data_set_update = self.get_data_set_update(content_copy_actions)
        self.send_request(data_set_update)

    def send_request(self, data_set_update):
        request = {
            "method": "updateDataSets",
            "params": [
                self.openbis.token,
                [data_set_update]
            ]
        }
        self.openbis._post_request(self.openbis.as_v3, request)


    def get_data_set_update(self, content_copy_actions=[]):
        return {
            "@type": "as.dto.dataset.update.DataSetUpdate",
            "dataSetId": self.get_data_set_id(),
            "linkedData": self.get_linked_data(content_copy_actions)
        }


    def get_data_set_id(self):
        return {
            "@type": "as.dto.dataset.id.DataSetPermId",
            "permId": self.data_set_id
        }


    def get_linked_data(self, actions):
        return {
            "@type": "as.dto.common.update.FieldUpdateValue",
            "isModified": True,
            "value": {
                "@type": "as.dto.dataset.update.LinkedDataUpdate",
                "contentCopies": {
                    "@type": "as.dto.dataset.update.ContentCopyListUpdateValue",
                    "actions": actions,
                }
            }
        }


    def get_actions_add_content_copy(self):
        return [{
                    "@type": "as.dto.common.update.ListUpdateActionAdd",
                    "items": [ self.get_content_copy_creation() ]
                }]

    def get_actions_remove_content_copy(self, content_copy):
        return [{
                    "@type": "as.dto.common.update.ListUpdateActionRemove",
                    "items": [ content_copy["id"] ]
                }]

    def get_content_copy_creation(self):
        return {
            "@type": "as.dto.dataset.create.ContentCopyCreation",
            "externalDmsId": {
                "@type": "as.dto.externaldms.id.ExternalDmsPermId",
                "permId": self.edms_id
            },
            "path": self.path,
            "gitCommitHash": self.commit_id,
            "gitRepositoryId" : self.repository_id,
        }


class GitDataSetFileSearch(object):

    def __init__(self, openbis, data_set_id, dss_code=None):
        """Initialize the command object with the necessary parameters.
        :param openbis: The openBIS API object.
        :param data_set_id: Id of the data set to be updated
        :param dss_code: Code for the DSS -- defaults to the first dss if none is supplied.
        """
        self.openbis = openbis
        self.data_set_id = data_set_id
        self.dss_code = dss_code

    def search_files(self):
        request = {
            "method": "searchFiles",
            "params": [
                self.openbis.token,
                self.get_data_set_file_search_criteria(),
                self.get_data_set_file_fetch_options(),
            ]
        }
        server_url = self.data_store_url()
        return self.openbis._post_request_full_url(server_url, request)

    def get_data_set_file_search_criteria(self):
        return {
            "@type": "dss.dto.datasetfile.search.DataSetFileSearchCriteria",
            "operator": "AND",
            "criteria": [
                {
                    "@type": "as.dto.dataset.search.DataSetSearchCriteria",
                    "relation": "DATASET",
                    "operator": "OR",
                    "criteria": [
                        {
                            "fieldName": "code",
                            "fieldType": "ATTRIBUTE",
                            "fieldValue": {
                                "value": self.data_set_id,
                                "@type": "as.dto.common.search.StringEqualToValue"
                            },
                            "@type": "as.dto.common.search.CodeSearchCriteria"
                        }
                    ],
                }
            ],
        }

    def get_data_set_file_fetch_options(self):
        return {
            "@type": "dss.dto.datasetfile.fetchoptions.DataSetFileFetchOptions",
        }

    def data_store_url(self):
        data_stores = self.openbis.get_datastores()
        if self.dss_code is None:
            self.dss_code = self.openbis.get_datastores()['code'][0]
        data_store = data_stores[data_stores['code'] == self.dss_code]
        return "{}/datastore_server/rmi-data-store-server-v3.json".format(data_store['downloadUrl'][0])
