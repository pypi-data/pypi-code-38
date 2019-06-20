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
import json
import re
import time
import copy
from watson_machine_learning_client.wml_client_error import MissingValue, WMLClientError, MissingMetaProp
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource
from multiprocessing import Pool
from watson_machine_learning_client.utils import print_text_header_h1, print_text_header_h2, EXPERIMENT_DETAILS_TYPE,  format_metrics, STR_TYPE, STR_TYPE_NAME, docstring_parameter, group_metrics, str_type_conv, meta_props_str_conv
from watson_machine_learning_client.hpo import HPOParameter, HPOMethodParam
from watson_machine_learning_client.metanames import ExperimentMetaNames
_DEFAULT_LIST_LENGTH = 50

class Experiments(WMLResource):
    """
       Run new experiment.
    """

    ConfigurationMetaNames = ExperimentMetaNames()
    """MetaNames for experiments creation."""

    @staticmethod
    def _HPOParameter(name, values=None, max=None, min=None, step=None):
        return HPOParameter(name, values, max, min, step)

    @staticmethod
    def _HPOMethodParam(name=None, value=None):
        return HPOMethodParam(name, value)

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        self._experiments_uids_cache = {}

    def store(self, meta_props):
        """
                Create an experiment.

                **Parameters**

                .. important::

                       #. **meta_props**:  meta data of the experiment configuration. To see available meta names use:\n
                                           >>> client.experiments.ConfigurationMetaNames.get()

                          **type**: dict\n

                **Output**

                .. important::

                       **returns**: stored experiment metadata\n
                       **return type**: dict\n

                **Example**

                    >>> metadata = {
                    >>>  client.experiments.ConfigurationMetaNames.NAME: 'my_experiment',
                    >>>  client.experiments.ConfigurationMetaNames.EVALUATION_METRICS: ['accuracy'],
                    >>>  client.experiments.ConfigurationMetaNames.TRAINING_REFERENCES: [
                    >>>      {
                    >>>        'pipeline': {'href': pipeline_href_1}
                    >>>
                    >>>      },
                    >>>      {
                    >>>        'pipeline': {'href':pipeline_href_2}
                    >>>      },
                    >>>   ]
                    >>> }
                    >>> experiment_details = client.experiments.store(meta_props=metadata)
                    >>> experiment_href = client.experiments.get_href(experiment_details)
        """
        metaProps = self.ConfigurationMetaNames._generate_resource_metadata(meta_props)
        if not self._ICP:
            self.ConfigurationMetaNames._validate(meta_props)
            response_experiment_post = requests.post(
                self._href_definitions.get_experiments_href(),
                json=metaProps,
                headers=self._client._get_headers()
            )
        else:
            self.ConfigurationMetaNames._validate(meta_props)
            response_experiment_post = requests.post(
                self._href_definitions.get_experiments_href(),
                json=metaProps,
                headers=self._client._get_headers(),
                verify=False
            )

        return self._handle_response(201, u'saving experiment', response_experiment_post)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def update(self, experiment_uid, changes):
        """
                Updates existing experiment metadata.

                **Parameters**

                .. important::
                    #. **experiment_uid**:  UID of experiment which definition should be updated\n
                       **type**: str\n
                    #. **changes**:  elements which should be changed, where keys are ConfigurationMetaNames\n
                       **type**: dict\n

                **Output**

                .. important::

                     **returns**: metadata of updated experiment\n
                     **return type**: dict\n

                **Example**

                 >>> metadata = {
                 >>> client.experiments.ConfigurationMetaNames.NAME:"updated_exp"
                 >>> }
                 >>> exp_details = client.experiments.update(experiment_uid, changes=metadata)

        """
        experiment_uid = str_type_conv(experiment_uid)
        self._validate_type(experiment_uid, u'experiment_uid', STR_TYPE, True)
        self._validate_type(changes, u'changes', dict, True)
        meta_props_str_conv(changes)

        details = self._client.repository.get_details(experiment_uid)

        patch_payload = self.ConfigurationMetaNames._generate_patch_payload(details['entity'], changes, with_validation=True)

        url = self._href_definitions.get_experiment_href(experiment_uid)
        if not self._ICP:
            response = requests.patch(url, json=patch_payload, headers=self._client._get_headers())
        else:
            response = requests.patch(url, json=patch_payload, headers=self._client._get_headers(), verify=False)
        updated_details = self._handle_response(200, u'experiment patch', response)

        return updated_details


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, experiment_uid=None, limit=None):
        """
                Get metadata of experiment(s). If no experiment UID is specified all experiments metadata is returned.

                **Parameters**

                .. important::

                       #. **experiment_uid**:  UID of experiment (optional)\n
                          **type**: str\n
                       #. **limit**:  limit number of fetched records (optional)\n
                          **type**: int\n

                **Output**

                .. important::

                    **returns**: experiment(s) metadata\n
                    **return type**: dict\n
                    dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n

                .. note::

                   If UID is not specified, all experiments metadata is fetched\n

                **Example**

                 >>> experiment_details = client.experiments.get_details(experiment_uid)
                 >>> experiment_details = client.experiments.get_details()
         """

        experiment_uid = str_type_conv(experiment_uid)
        url = self._href_definitions.get_experiments_href()

        return self._get_artifact_details(url, experiment_uid, limit, 'experiment')

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(experiment_details):
        """
                Get UID of stored experiment.

                **Parameters**

                .. important::

                    #. **experiment_details**:  Metadata of the stored experiment\n
                       **type**: dict\n

                **Output**

                .. important::

                        **returns**: UID of stored experiment\n
                        **return type**: str\n

                **Example**

                 >>> experiment_details = client.experiments.get_detailsf(experiment_uid)
                 >>> experiment_uid = client.experiments.get_uid(experiment_details)
        """
        Experiments._validate_type(experiment_details, u'experiment_details', object, True)
        Experiments._validate_type_of_details(experiment_details, EXPERIMENT_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(experiment_details, u'experiment_details',
                                                           [u'metadata', u'guid'])

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_href(experiment_details):
        """
                Get href of stored experiment.

                **Parameters**

                .. important::

                      #. **experiment_details**:  Metadata of the stored experiment\n
                         **type**: dict\n

                **Output**

                .. important::

                     **returns**: href of stored experiment\n
                     **return type**: str\n

                **Example**

                 >>> experiment_details = client.experiments.get_detailsf(experiment_uid)
                 >>> experiment_href = client.experiments.get_href(experiment_details)
        """
        Experiments._validate_type(experiment_details, u'experiment_details', object, True)
        Experiments._validate_type_of_details(experiment_details, EXPERIMENT_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(experiment_details, u'experiment_details',
                                                           [u'metadata', u'href'])


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, experiment_uid):
        """
            Delete a stored experiment.

            **Parameters**

            .. important::
                #. **experiment_uid**:  UID of the stored experiment\n
                   **type**: str\n

            **Output**

            .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n

            **Example**

             >>> client.experiments.delete(experiment_uid)

        """
        experiment_uid = str_type_conv(experiment_uid)
        Experiments._validate_type(experiment_uid, u'experiment_uid', STR_TYPE, True)

        url = self._href_definitions.get_experiment_href(experiment_uid)
        if not self._ICP:
            response = requests.delete(url, headers=self._client._get_headers())
        else:
            response = requests.delete(url, headers=self._client._get_headers(), verify=False)

        return self._handle_response(204, u'experiment deletion', response, False)


    def list(self, limit=None):
        """
           List stored experiments. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all experiments in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.experiments.list()
        """

        experiment_resources = self.get_details(limit=limit)[u'resources']
        experiment_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at']) for m in
                             experiment_resources]

        self._list(experiment_values, [u'GUID', u'NAME', u'CREATED'], limit, _DEFAULT_LIST_LENGTH)


    def _create_revision(self, experiment_id, meta_props):
        """
        Creates a new experiment revision.
        :param meta_props:
        :param experiment_id:
        :return:  stored experiment new revision details
        A way you might use me is:

           >>> metadata = {
           >>>  client.experiments.ConfigurationMetaNames.NAME: 'my_experiment',
           >>>  client.experiments.ConfigurationMetaNames.EVALUATION_METRICS: ['accuracy'],
           >>>  client.experiments.ConfigurationMetaNames.TRAINING_REFERENCES: [
           >>>      {
           >>>        'pipeline': {'href': pipeline_href_1}
           >>>      },
           >>>      {
           >>>        'pipeline': {'href':pipeline_href_2}
           >>>      }
           >>>   ],
           >>> }
           >>> experiment_artifact = client.experiments.create_revision(meta_props, experiment_id)
           >>> experiment_href = client.experiments.get_href(experiment_details)

        """
        meta_props_str_conv(meta_props)
        meta_props = copy.deepcopy(meta_props)

        if not self._ICP:
            response_experiment_put = requests.put(
                self._href_definitions.get_experiment_href(experiment_id),
                json=self.ConfigurationMetaNames._generate_resource_metadata(meta_props),
                headers=self._client._get_headers()
            )

        else:
            response_experiment_put = requests.put(
                self._href_definitions.get_experiment_href(experiment_id),
                json=self.ConfigurationMetaNames._generate_resource_metadata(meta_props),
                headers=self._client._get_headers(),
                verify=False
            )

        return self._handle_response(200, u'saving experiment revision', response_experiment_put)


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _get_revision_details(self, experiment_uid, limit=None):
        """
            Get metadata of stored experiments revisions. If  experiment UID is specified metadata of all revisions of that experiment is returned.

            :param experiment_uid: stored experiment UID (optional)
            :type experiment_uid: {str_type}

            :param limit: limit number of fetched records (optional)
            :type limit: int

            :returns: stored experiment(s) metadata
            :rtype: dict

            A way you might use me is:

            >>> experiment_details = client.repository.get_revision_details(experiment_uid)
            >>> experiment_details = client.experiments.get_revision_details(experiment_uid)
         """
        url = self._href_definitions.get_experiment_href(experiment_uid) + u'/' + 'revisions'
        if not self._ICP:
            experiment_uid = str_type_conv(experiment_uid)


            response_get = requests.get(
                url,
                headers=self._client._get_headers()
            )

        else:
            response_get = requests.get(
                url,
                headers=self._client._get_headers(),
                verify=False
            )

        return self._handle_response(200, u'Fetching experiment revisions details', response_get)

