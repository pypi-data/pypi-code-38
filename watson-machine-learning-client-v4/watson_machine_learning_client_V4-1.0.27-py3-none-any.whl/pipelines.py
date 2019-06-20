################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
import requests
from watson_machine_learning_client.utils import PIPELINE_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, meta_props_str_conv, str_type_conv, get_file_from_cos
from watson_machine_learning_client.metanames import PipelineMetanames
from watson_machine_learning_client.wml_resource import WMLResource

_DEFAULT_LIST_LENGTH = 50


class Pipelines(WMLResource):
    """
    Store and manage your pipelines.
    """
    ConfigurationMetaNames = PipelineMetanames()
    """MetaNames for pipelines creation."""

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)


        self._ICP = client.ICP


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _generate_pipeline_document(self, meta_props):
        doc = {
            "doc_type": "pipeline1",
            "version": "2.0",
            "primary_pipeline": "wmla_only",
            "pipelines": [
                {
                    "id": "wmla_only",
                    "runtime_ref": "hybrid",
                    "nodes": [
                        {
                            "id": "training",
                            "type": "model_node",
                            "op": "dl_train",
                            "runtime_ref": "DL_WMLA",
                            "inputs": [
                            ],
                            "outputs": [],
                            "parameters": {
                                "name": "pipeline",
                                "description": "Pipeline - Python client"
                            }
                        }
                    ]
                }
            ],
            "schemas": [
                {
                    "id": "schema1",
                    "fields": [
                        {
                            "name": "text",
                            "type": "string"
                        }
                    ]
                }
            ]
        }
        if self.ConfigurationMetaNames.COMMAND in meta_props:
            doc["pipelines"][0]["nodes"][0]["parameters"]["command"] = meta_props[self.ConfigurationMetaNames.COMMAND]
        if self.ConfigurationMetaNames.RUNTIMES in meta_props:
            doc["runtimes"] = meta_props[self.ConfigurationMetaNames.RUNTIMES]
        if self.ConfigurationMetaNames.LIBRARY_UID in meta_props:
            doc["pipelines"][0]["nodes"][0]["parameters"]["training_lib_href"] = "/v4/libraries/"+meta_props[self.ConfigurationMetaNames.LIBRARY_UID]
        if self.ConfigurationMetaNames.COMPUTE in meta_props:
            doc["pipelines"][0]["nodes"][0]["parameters"]["compute"] = meta_props[self.ConfigurationMetaNames.COMPUTE]

        return doc

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store(self, meta_props):
        """
           Create a pipeline.\n

           **Parameters**

           .. important::

                #. **meta_props**:  meta data of the pipeline configuration. To see available meta names use:\n
                                    >>> client.pipelines.ConfigurationMetaNames.get()

                   **type**: dict\n

           **Output**

           .. important::

                **returns**: stored pipeline metadata\n
                **return type**: dict\n

           **Example**

            >>> metadata = {
            >>>  client.pipelines.ConfigurationMetaNames.NAME: 'my_pipeline',
            >>>  client.pipelines.ConfigurationMetaNames.DESCRIPTION: 'sample description'
            >>> }
            >>> pipeline_details = client.pipelines.store(training_definition_filepath, meta_props=metadata)
            >>> pipeline_url = client.pipelines.get_href(pipeline_details)
        """

        # quick support for COS credentials instead of local path
        # TODO add error handling and cleaning (remove the file)
        Pipelines._validate_type(meta_props, u'meta_props', dict, True)

        if self.ConfigurationMetaNames.DOCUMENT in meta_props:
            model_meta = self.ConfigurationMetaNames._generate_resource_metadata(
                meta_props,
                with_validation=True,
                client=self._client

            )
        else:
            document = self._generate_pipeline_document(meta_props)
            meta_props[self.ConfigurationMetaNames.DOCUMENT] = document
            model_meta = self.ConfigurationMetaNames._generate_resource_metadata(
                meta_props,
                with_validation=True,
                client=self._client

            )

        if not self._ICP:
            creation_response = requests.post(
                    self._wml_credentials['url'] + '/v4/pipelines',
                    headers=self._client._get_headers(),
                    json=model_meta
            )
        else:
            creation_response = requests.post(
                self._wml_credentials['url'] + '/v4/pipelines',
                headers=self._client._get_headers(),
                json=model_meta,
                verify=False
            )


        pipeline_details = self._handle_response(201, u'creating new pipeline', creation_response)

        return pipeline_details

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _create_revision(self, pipeline_uid,meta_props):
        """
            Create a new pipeline revision.

            :param pipeline_uid: pipeline UID
            :type pipeline_uid: {str_type}

            A way you might use me is:

            >>> client.pipelines.create_revision(pipeline_uid)
        """
        pipeline_uid = str_type_conv(pipeline_uid)
        Pipelines._validate_type(pipeline_uid, u'pipeline_uid', STR_TYPE, True)

        pipeline_endpoint = self._href_definitions.get_pipeline_href(pipeline_uid)
        model_meta = self.ConfigurationMetaNames._generate_resource_metadata(
            meta_props,
            with_validation=True,
            client=self._client

        )
        if not self._ICP:
            response_put = requests.put(pipeline_endpoint, json=model_meta,headers=self._client._get_headers())
        else:
            response_put = requests.put(pipeline_endpoint, json=model_meta,headers=self._client._get_headers(), verify=False)

        return self._handle_response(200, u'pipeline version creation', response_put, False)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def update(self, pipeline_uid, changes):
        """
                Updates existing pipeline metadata.

                **Parameters**

                .. important::

                    #. **pipeline_uid**:  UID of pipeline which definition should be updated\n
                       **type**: str\n
                    #. **changes**:  elements which should be changed, where keys are ConfigurationMetaNames\n
                       **type**: dict\n

                **Output**

                .. important::

                       **returns**: metadata of updated pipeline\n
                       **return type**: dict\n

                **Example**

                 >>> metadata = {
                 >>> client.pipelines.ConfigurationMetaNames.NAME:"updated_pipeline"
                 >>> }
                 >>> pipeline_details = client.pipelines.update(pipeline_uid, changes=metadata)
        """

        pipeline_uid = str_type_conv(pipeline_uid)
        self._validate_type(pipeline_uid, u'pipeline_uid', STR_TYPE, True)
        self._validate_type(changes, u'changes', dict, True)
        meta_props_str_conv(changes)

        details = self._client.pipelines.get_details(pipeline_uid)

        patch_payload = self.ConfigurationMetaNames._generate_patch_payload(details['entity'], changes,
                                                                            with_validation=True)

        url = self._href_definitions.get_pipeline_href(pipeline_uid)

        if not self._ICP:
            response = requests.patch(url, json=patch_payload, headers=self._client._get_headers())
        else:
            response = requests.patch(url, json=patch_payload, headers=self._client._get_headers(), verify=False)

        updated_details = self._handle_response(200, u'pipeline patch', response)

        return updated_details

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, pipeline_uid):
        """
            Delete a stored pipeline.

            **Parameters**

            .. important::
                #. **pipeline_uid**:  Pipeline UID\n
                   **type**: str\n

            **Output**

            .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n

            **Example**

             >>> client.pipelines.delete(deployment_uid)
        """

        pipeline_uid = str_type_conv(pipeline_uid)
        Pipelines._validate_type(pipeline_uid, u'pipeline_uid', STR_TYPE, True)

        pipeline_endpoint = self._href_definitions.get_pipeline_href(pipeline_uid)
        if not self._ICP:
            response_delete = requests.delete(pipeline_endpoint, headers=self._client._get_headers())
        else:
            response_delete = requests.delete(pipeline_endpoint, headers=self._client._get_headers(), verify=False)

        return self._handle_response(204, u'pipeline deletion', response_delete, False)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, pipeline_uid=None, limit=None):
        """
           Get metadata of stored pipeline(s). If pipeline UID is not specified returns all pipelines metadata.

           **Parameters**

           .. important::
                #. **pipeline_uid**: Pipeline UID (optional)\n
                   **type**: str\n
                #. **limit**:  limit number of fetched records (optional)\n
                   **type**: int\n

           **Output**

           .. important::
                **returns**: metadata of pipeline(s)\n
                **return type**: dict
                dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n

           .. note::
                If UID is not specified, all pipelines metadata is fetched\n

           **Example**

            >>> pipeline_details = client.pipelines.get_details(pipeline_uid)
            >>> pipeline_details = client.pipelines.get_details()
        """

        pipeline_uid = str_type_conv(pipeline_uid)
        Pipelines._validate_type(pipeline_uid, u'pipeline_uid', STR_TYPE, False)
        Pipelines._validate_type(limit, u'limit', int, False)

        url = self._href_definitions.get_pipelines_href()

        return self._get_artifact_details(url, pipeline_uid, limit, 'definitions',summary="False")

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _get_revisions(self, pipeline_uid, limit=None):
        """
            Get metadata of pipeline revisions.

            :param pipeline_uid:  stored pipeline UID
            :type pipeline_uid: {str_type}

            :param limit: limit number of fetched records (optional)
            :type limit: int

            :returns: stored pipeline revision(s) metadata
            :rtype: dict

            A way you might use me is:

            >>> pipeline_details = client.pipelines.get_revisions(pipeline_uid)
         """
        pipeline_uid = str_type_conv(pipeline_uid)
        Pipelines._validate_type(pipeline_uid, u'pipeline_uid', STR_TYPE, True)
        Pipelines._validate_type(limit, u'limit', int, False)

        url = self._href_definitions.get_pipeline_href(pipeline_uid) + "/revisions"

        return self._get_artifact_details(url,None,limit, 'pipeline_revisions', summary="False")

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_href(pipeline_details):
        """
            Get hef from pipeline details.

            **Parameters**

            .. important::
                #. **pipeline_details**:  Metadata of the stored pipeline\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: pipeline href\n
                **return type**: str

            **Example**

             >>> pipeline_details = client.pipelines.get_details(pipeline_uid)
             >>> pipeline_href = client.pipelines.ger_href(pipeline_details)
        """
        Pipelines._validate_type(pipeline_details, u'pipeline_details', object, True)
        Pipelines._validate_type_of_details(pipeline_details, PIPELINE_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(pipeline_details, u'pipeline_details', [u'metadata', u'href'])


    @staticmethod
    def get_uid(pipeline_details):
        """
            Get pipeline_uid from pipeline details.

            **Parameters**

            .. important::
                #. **pipeline_details**:  Metadata of the stored pipeline\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: pipeline UID\n
                **return type**: str

            **Example**

             >>> pipeline_details = client.pipelines.get_details(pipeline_uid)
             >>> pipeline_uid = client.pipelines.get_uid(deployment)
        """
        Pipelines._validate_type(pipeline_details, u'pipeline_details', object, True)
        Pipelines._validate_type_of_details(pipeline_details, PIPELINE_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(pipeline_details, u'pipeline_details', [u'metadata', u'guid'])

    def list(self, limit=None):
        """
           List stored pipelines. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all pipelines in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.pipelines.list()
        """
        pipeline_resources = self.get_details(limit=limit)[u'resources']
        pipeline_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at']) for m in pipeline_resources]

        self._list(pipeline_values, [u'GUID', u'NAME', u'CREATED'], limit, _DEFAULT_LIST_LENGTH)
