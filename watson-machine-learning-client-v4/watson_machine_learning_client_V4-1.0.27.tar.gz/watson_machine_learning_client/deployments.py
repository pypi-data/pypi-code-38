
from __future__ import print_function
import requests
import json
from watson_machine_learning_client.utils import DEPLOYMENT_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, print_text_header_h1, print_text_header_h2, STR_TYPE, STR_TYPE_NAME, docstring_parameter, str_type_conv, meta_props_str_conv, StatusLogger, convert_metadata_to_parameters
from watson_machine_learning_client.wml_client_error import WMLClientError, MissingValue, NoVirtualDeploymentSupportedForICP
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.metanames import DeploymentMetaNames, ScoringMetaNames, DecisionOptimizationMetaNames
from watson_machine_learning_client.libs.repo.util.library_imports import LibraryChecker
import numpy as np
#from watson_machine_learning_client.metanames import DeploymentMetaNames, ScoreMetaNames, EnvironmentMetaNames

lib_checker = LibraryChecker()

class Deployments(WMLResource):
    """
        Deploy and score published artifacts (models and functions).
    """
    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        if not client.ICP:
            Deployments._validate_type(client.service_instance.details, u'instance_details', dict, True)
            Deployments._validate_type_of_details(client.service_instance.details, INSTANCE_DETAILS_TYPE)
        self.session = requests.Session()
        self._ICP = client.ICP
        self.ConfigurationMetaNames = DeploymentMetaNames()
        self.ScoringMetaNames = ScoringMetaNames()
        self.DecisionOptimizationMetaNames = DecisionOptimizationMetaNames()

    def _deployment_status_errors_handling(self, deployment_details, operation_name):
        try:
            if 'failure' in deployment_details['entity']['status']:
                errors = deployment_details[u'entity'][u'failure'][u'errors']
                for error in errors:
                    if type(error) == str:
                        try:
                            error_obj = json.loads(error)
                            print(error_obj[u'message'])
                        except:
                            print(error)
                    elif type(error) == dict:
                        print(error['message'])
                    else:
                        print(error)
                raise WMLClientError('Deployment ' + operation_name + ' failed. Errors: ' + str(errors))
            else:
                print(deployment_details['entity']['status'])
                raise WMLClientError('Deployment ' + operation_name + ' failed. Error: ' + str(deployment_details['entity']['status']['state']))
        except WMLClientError as e:
            raise e
        except Exception as e:
            self._logger.debug('Deployment ' + operation_name + ' failed: ' + str(e))
            print(deployment_details['entity']['status']['failure'])
            raise WMLClientError('Deployment ' + operation_name + ' failed.')

    @docstring_parameter({'str_type': STR_TYPE_NAME})  # TODO model_uid and artifact_uid should be changed to artifact_uid only
    def create(self, artifact_uid=None, meta_props=None, **kwargs):
            """
                Create a deployment from an artifact. As artifact we understand model or function which may be deployed.
                
                **Parameters**
                
                .. important::

                    #. **artifact_uid**:  Published artifact UID (model or function uid)\n
                       **type**: str\n

                    #. **meta_props**: metaprops. To see the available list of metanames use:\n
                                       >>> client.deployments.ConfigurationMetaNames.get()

                       **type**: dict\n
                
                **Output**
                
                .. important::

                    **returns**: metadata of the created deployment\n
                    **return type**: dict\n

                **Example**
                 >>> meta_props = {
                 >>> wml_client.deployments.ConfigurationMetaNames.NAME: "SAMPLE DEPLOYMENT NAME",
                 >>> wml_client.deployments.ConfigurationMetaNames.ONLINE: {}
                 >>> }
                 >>> deployment_details = client.deployments.create(artifact_uid, meta_props)
             """
            #artifact_uid = str_type_conv(artifact_uid) if artifact_uid is not None else (str_type_conv(kwargs['model_uid'] if 'model_uid' in kwargs else None))
            Deployments._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)

            if self._ICP:
                predictionUrl = self._wml_credentials[u'url']

            metaProps = self.ConfigurationMetaNames._generate_resource_metadata(meta_props)

            artifact_details = self._client.repository.get_details(artifact_uid)
            artifact_href = artifact_details['metadata']['href']
            artifact_revision_id = artifact_href.split('=')[1]

            if 'model' in artifact_href:
                details = "/v4/models/" + artifact_uid + "?rev=" + artifact_revision_id
            elif 'function' in artifact_href:
                details = "/v4/functions/" + artifact_uid + "?rev=" + artifact_revision_id
            else:
                raise WMLClientError('Error during update of deployment, unexpected artifact type: \'{}\'.'.format(artifact_uid))

            metaProps['asset'] = {'href': details}

            url = self._href_definitions.get_deployments_href()

            if not self._ICP:
                response = requests.post(
                    url,
                    json= metaProps,
                    headers=self._client._get_headers())
            else:
                response = requests.post(
                    url,
                    json=metaProps,
                    headers=self._client._get_headers(),
                    verify=False)

            ## Post Deployment call executed
            if response.status_code == 202:
                deployment_details = response.json()
                #print(deployment_details)


                if self._ICP:
                    if 'online_url' in deployment_details["entity"]["status"]:
                     scoringUrl = deployment_details.get(u'entity').get(u'status').get('online_url').get('url').replace('https://ibm-nginx-svc:443', predictionUrl)
                     deployment_details[u'entity'][u'status']['online_url']['url'] = scoringUrl

                deployment_uid = self.get_uid(deployment_details)

                import time
                print_text_header_h1(u'Synchronous deployment creation for uid: \'{}\' started'.format(artifact_uid))

                status = deployment_details[u'entity'][u'status']['state']

                with StatusLogger(status) as status_logger:
                    while True:
                        time.sleep(5)
                        deployment_details = self._client.deployments.get_details(deployment_uid)
                        #this is wrong , needs to update for ICP
                        if self._ICP:
                            scoringUrl = deployment_details.get(u'entity').get(u'asset').get('href').replace('https://wml-os-envoy:16600', predictionUrl)
                            deployment_details[u'entity'][u'asset']['href'] = scoringUrl
                        status = deployment_details[u'entity'][u'status'][u'state']
                        #status_logger.log_state(status)

                        if status != u'DEPLOY_IN_PROGRESS':
                            break

                if status == u'failed':
                    print_text_header_h2(u'Deployment creation failed')
                    self._deployment_status_errors_handling(deployment_details, 'creation')
                else:
                    print(u'')
                    print_text_header_h2(u'Successfully finished deployment creation, deployment_uid=\'{}\''.format(deployment_uid))
                    return deployment_details
            else:
                error_msg = u'Deployment creation failed'
                reason = response.text
                print(reason)
                print_text_header_h2(error_msg)
                raise WMLClientError(error_msg + '. Error: ' + str(response.status_code) + '. ' + reason)

            #return self._handle_response(202, u'created deployment', response)
    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(deployment_details):
        """
            Get deployment_uid from deployment details.
            
            **Parameters**
            
            .. important::
                #. **deployment_details**:  Metadata of the deployment\n
                   **type**: dict\n
            
            **Output**
            
            .. important::
                **returns**: deployment UID that is used to manage the deployment\n
                **return type**: str
            
            **Example**
            
             >>> deployment_uid = client.deployments.get_uid(deployment)
        """
        Deployments._validate_type(deployment_details, u'deployment_details', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:
            uid = deployment_details.get(u'metadata').get(u'guid')
        except Exception as e:
            raise WMLClientError(u'Getting deployment UID from deployment details failed.', e)

        if uid is None:
            raise MissingValue(u'deployment_details.metadata.guid')

        return uid

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_href(deployment_details):
        """
            Get deployment_href from deployment details.
            
            **Parameters**
            
            .. important::
                #. **deployment_details**:  Metadata of the deployment\n
                   **type**: dict\n
            
            **Output**
            
            .. important::
                **returns**: deployment href that is used to manage the deployment\n
                **return type**: str
            
            **Example**
            
            >>> deployment_href = client.deployments.get_href(deployment)
        """
        Deployments._validate_type(deployment_details, u'deployment_details', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:

            url = deployment_details.get(u'metadata').get(u'href')
        except Exception as e:
            raise WMLClientError(u'Getting deployment url from deployment details failed.', e)

        if url is None:
            raise MissingValue(u'deployment_details.metadata.href')

        return url

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, deployment_uid=None, limit=None):
        """
           Get information about your deployment(s). If deployment_uid is not passed, all deployment details are fetched.
           
           **Parameters**
           
           .. important::
                #. **deployment_uid**: Deployment UID (optional)\n
                   **type**: str\n
                #. **limit**:  limit number of fetched records (optional)\n
                   **type**: int\n
           
           **Output**
           
           .. important::
                **returns**: metadata of deployment(s)\n
                **return type**: dict\n
                dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n

           .. note::
                If UID is not specified, all deployments metadata is fetched\n

           
           **Example**
           
            >>> deployment_details = client.deployments.get_details(deployment_uid)
            >>> deployment_details = client.deployments.get_details(deployment_uid=deployment_uid)
            >>> deployments_details = client.deployments.get_details()
        """
        deployment_uid = str_type_conv(deployment_uid)
        Deployments._validate_type(deployment_uid, u'deployment_uid', STR_TYPE, False)

        if deployment_uid is not None and not is_uid(deployment_uid):
            raise WMLClientError(u'\'deployment_uid\' is not an uid: \'{}\''.format(deployment_uid))

        url = self._href_definitions.get_deployments_href()

        return self._get_artifact_details(url, deployment_uid, limit, 'deployments')

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_scoring_href(deployment_details):
        """
            Get scoring url from deployment details.
            
            **Parameters**
            
            .. important::
                #. **deployment_details**:  Metadata of the deployment\n
                   **type**: dict\n
            
            **Output**
            
            .. important::
                **returns**: scoring endpoint url that is used for making scoring requests\n
                **return type**: str\n
            
            **Example**
            
             >>> scoring_href = client.deployments.get_scoring_href(deployment)
        """
        Deployments._validate_type(deployment_details, u'deployment', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:
            scoringUrl = deployment_details['entity']['status']['online_url']['url']
        except Exception as e:
            raise WMLClientError(u'Getting scoring url for deployment failed.', e)

        if scoringUrl is None:
            raise MissingValue(u'scoring_url missing in online_predictions')

        return scoringUrl

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, deployment_uid):
        """
            Delete deployment.
            
            **Parameters**
            
            .. important::
                #. **deployment uid**:  Deployment UID\n
                   **type**: str\n
            
            **Output**
            
            .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n
            
            **Example**
            
             >>> client.deployments.delete(deployment_uid)
        """
        deployment_uid = str_type_conv(deployment_uid)
        Deployments._validate_type(deployment_uid, u'deployment_uid', STR_TYPE, True)

        if deployment_uid is not None and not is_uid(deployment_uid):
            raise WMLClientError(u'\'deployment_uid\' is not an uid: \'{}\''.format(deployment_uid))

        deployment_url = self._href_definitions.get_deployment_href(deployment_uid)

        if not self._ICP:
            response_delete = requests.delete(
                deployment_url,
                headers=self._client._get_headers())
        else:
            response_delete = requests.delete(
                deployment_url,
                headers=self._client._get_headers(),
                verify=False)

        return self._handle_response(204, u'deployment deletion', response_delete, False)


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def score(self,deployment_id, meta_props):
        """
                    Make scoring requests against deployed artifact.

                    **Parameters**

                    .. important::
                        #. **deployment_id**:  UID of the deployment to be scored\n
                           **type**: str\n
                        #. **meta_props**:  Meta props for scoring\n
                                            >>> Use client.deployments.ScoringMetaNames.show() to view the list of ScoringMetaNames.
                           **type**: dict\n
                        #. **transaction_id**:  transaction id to be passed with records during payload logging (optional)\n
                           **type**: str\n

                    **Output**

                    .. important::
                        **returns**: scoring result containing prediction and probability\n
                        **return type**: dict\n

                    .. note::

                            * client.deployments.ScoringMetaNames.INPUT_DATA is the only metaname valid for sync scoring.\n
                            * The valid payloads for scoring input are either list of values, pandas or numpy dataframes.

                    **Example**

                     >>> scoring_payload = {wml_client.deployments.ScoringMetaNames.INPUT_DATA: [{'fields': ['GENDER','AGE','MARITAL_STATUS','PROFESSION'], 'values': [['M',23,'Single','Student'],['M',55,'Single','Executive']]}]}
                     >>> predictions = client.deployments.score(deployment_id, scoring_payload)
                     >>> predictions = client.deployments.score(deployment_id, scoring_payload,async=True)
        """
        Deployments._validate_type(deployment_id, u'deployment_id', STR_TYPE, True)
        Deployments._validate_type(meta_props, u'meta_props', dict, True)

        if meta_props[self.ScoringMetaNames.INPUT_DATA] is None:
                  raise WMLClientError("Scoring data input is mandatory for synchronous scoring")


        scoring_data = meta_props[self.ScoringMetaNames.INPUT_DATA]

        if scoring_data is not None:
            score_payload = []
            for each_score_request in scoring_data:
                lib_checker.check_lib(lib_name='pandas')
                import pandas as pd

                scoring_values = each_score_request["values"]
                # Check feature types, currently supporting pandas df, numpy.ndarray, python lists and Dmatrix
                if (isinstance(scoring_values, pd.DataFrame)):
                    fields_names = scoring_values.columns.values.tolist()
                    values = scoring_values.values.tolist()

                    each_score_request["values"] = values
                    if fields_names is not None:
                        each_score_request["fields"] = fields_names


                ## If payload is a numpy dataframe

                elif (isinstance(scoring_values, np.ndarray)):

                    values = scoring_values.tolist()
                    each_score_request["values"] = values


                # else:
                #     payload_score["values"] = each_score_request["values"]
                #     if "fields" in each_score_request:
                #         payload_score["fields"] = each_score_request["fields"]
                score_payload.append(each_score_request)

            ##See if it is scoring or DecisionOptimizationJob

        payload = {}

        payload["input_data"] = score_payload

        headers = self._client._get_headers()

        scoring_url = self._wml_credentials["url"] + "/v4/deployments/" + deployment_id + "/predictions"
        if not self._ICP:
                    response_scoring = self.session.post(
                        scoring_url,
                        json=payload,
                        headers=headers)
        else:
                    response_scoring = self.session.post(
                        scoring_url,
                        json=payload,
                        headers=headers,
                        verify=False)

        return self._handle_response(200, u'scoring', response_scoring)

        #########################################



    # @docstring_parameter({'str_type': STR_TYPE_NAME})
    # def score(self, deployment_id, meta_props, transaction_id=None):
    #         """
    #             Make scoring requests against deployed artifact.
    #
    #             **Parameters**
    #
    #             .. important::
    #                 #. **deployment_id**:  UID of the deployment to be scored\n
    #                    **type**: str\n
    #                 #. **meta_props**:  Meta props for scoring\n
    #                                     >>> Use client.deployments.ScoringMetaNames.show() to view the list of ScoringMetaNames.
    #                    **type**: dict\n
    #                 #. **transaction_id**:  transaction id to be passed with records during payload logging (optional)\n
    #                    **type**: str\n
    #
    #             **Output**
    #
    #             .. important::
    #                 **returns**: scoring result containing prediction and probability\n
    #                 **return type**: dict\n
    #
    #             .. note::
    #
    #                     * client.deployments.ScoringMetaNames.SCORING_INPUT_DATA is the only metaname valid for sync scoring.\n
    #
    #             **Example**
    #
    #              >>> scoring_payload = {wml_client.deployments.ScoringMetaNames.INPUT_DATA: [{'fields': ['GENDER','AGE','MARITAL_STATUS','PROFESSION'], 'values': [['M',23,'Single','Student'],['M',55,'Single','Executive']]}]}
    #              >>> predictions = client.deployments.score(deployment_id, scoring_payload)
    #              >>> predictions = client.deployments.score(deployment_id, scoring_payload,async=True)
    #         """
    #         Deployments._validate_type(deployment_id, u'scoring_url', STR_TYPE, True)
    #         Deployments._validate_type(meta_props, u'meta_props', dict, True)
    #
    #
    #         score_payload = {}
    #         if meta_props[self.ScoringMetaNames.INPUT_DATA] is None:
    #             raise WMLClientError("Scoring data input is mandatory for synchronous scoring")
    #
    #         score_payload["input_data"] = meta_props[self.ScoringMetaNames.INPUT_DATA]
    #         payload = score_payload
    #         Deployments._validate_type(deployment_id, u'scoring_url', STR_TYPE, True)
    #         Deployments._validate_type(payload, u'payload', dict, True)
    #
    #         headers = self._client._get_headers()
    #
    #         if transaction_id is not None:
    #             headers.update({'x-global-transaction-id': transaction_id})
    #         # making change - connection keep alive
    #         scoring_url = self._wml_credentials["url"] + "/v4/deployments/"+deployment_id+"/predictions"
    #         if not self._ICP:
    #             response_scoring = self.session.post(
    #                 scoring_url,
    #                 json=payload,
    #                 headers=headers)
    #         else:
    #             response_scoring = self.session.post(
    #                 scoring_url,
    #                 json=payload,
    #                 headers=headers,
    #                 verify=False)
    #
    #         return self._handle_response(200, u'scoring', response_scoring)

    def list(self, limit=None):
        """
           List deployments. If limit is set to None there will be only first 50 records shown.
           
           **Parameters**
           
           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n
           
           **Output**
           
           .. important::
                This method only prints the list of all deployments in a table format.\n
                **return type**: None\n

           **Example**
           
            >>> client.deployments.list()
        """
        details = self.get_details()
        resources = details[u'resources']
        values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'entity'][u'status']['state'],
                   m[u'metadata'][u'created_at'], self._get_deployable_asset_type(m)) for m in resources]

        self._list(values, [u'GUID', u'NAME', u'STATE', u'CREATED', u'ARTIFACT_TYPE'], limit, 50)

    def list_jobs(self,limit=None):
        """
           List the async jobs. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all async jobs in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.deployments.list_jobs()
        """
        details = self.get_job_details()
        resources = details[u'resources']
        values= []
        for m in resources:
            if 'scoring' in m['entity']:
                state = m['entity']['scoring']['status']['state']
            else:
                state = m['entity']['decision_optimization']['status']['state']
            values.append((m[u'metadata'][u'guid'], state ,
                   m[u'metadata'][u'created_at'],m['entity']['deployment']['href'].split("/")[3]))

        self._list(values, [u'JOB-UID', u'STATE', u'CREATED',u'DEPLOYMENT-ID'], None, 50)

    def _get_deployable_asset_type(self, details):
        url = details[u'entity'][u'asset']['href']
        if 'model' in url:
            return 'model'
        elif 'function' in url:
            return 'function'
        else:
            return 'unknown'
    def update(self, deployment_id, changes):
        """
                Updates existing deployment metadata.
                
                **Parameters**
                
                .. important::

                    #. **deployment_uid**:  UID of deployment which  should be updated\n
                       **type**: str\n
                    #. **changes**:  elements which should be changed, where keys are ConfigurationMetaNames\n
                       **type**: dict\n

                **Output**
                
                .. important::

                    **returns**: metadata of updated deployment\n
                    **return type**: dict\n
                    
                **Example**
                
                 >>> metadata = {
                 >>> client.deployments.ConfigurationMetaNames.NAME:"updated_Deployment"
                 >>> }
                 >>> deployment_details = client.deployments.update(deployment_uid, changes=metadata)
        """

        ## In case of passing 'AUTO_ONLINE_DEPLOYMENT' as true, we need to poll for deployment to be either 'deploy_success' or 'update_success'.

        deployment_uid = str_type_conv(deployment_id)
        Deployments._validate_type(deployment_uid, 'deployment_uid', STR_TYPE, True)

        deployment_details = self.get_details(deployment_uid)
        patch_payload = self.ConfigurationMetaNames._generate_patch_payload(deployment_details['entity'], changes,with_validation=True)

        ## As auto_online_deployment and auto_redeploy values are passed as 'bool' but service needs them in 'str' format to patch.
        for ele in patch_payload:
            if('auto_online_deployment' in ele['path'] or 'auto_redeploy' in ele['path']):
                if(ele['value']==True):
                    ele['value']='true'
                else:
                    ele['value']='false'

        url = self._href_definitions.get_deployment_href(deployment_uid)

        if not self._ICP:
            response = requests.patch(url, json=patch_payload, headers=self._client._get_headers())
        else:
            response = requests.patch(url, json=patch_payload, headers=self._client._get_headers(), verify=False)

        updated_details = self._handle_response(200, u'deployment patch', response)

        if('auto_online_deployment' in changes):
           if response is not None:
               if response.status_code == 200:
                   deployment_details = self.get_details(deployment_uid)

                   import time
                   print_text_header_h1(u' deployment update for uid: \'{}\' started'.format(deployment_uid))

                   status = deployment_details[u'entity'][u'status'][u'state']

                   with StatusLogger(status) as status_logger:
                       while True:
                           time.sleep(5)
                           deployment_details = self.get_details(deployment_uid)
                           status = deployment_details[u'entity'][u'status'][u'state']
                           status_logger.log_state(status)

                           if status != u'DEPLOY_IN_PROGRESS' and status != u'UPDATE_IN_PROGRESS':
                               break

                   if status == u'DEPLOY_SUCCESS' or status == u'UPDATE_SUCCESS':
                       print(u'')
                       print_text_header_h2(
                           u'Successfully finished deployment update, deployment_uid=\'{}\''.format(deployment_uid))
                       return deployment_details
                   else:
                       print_text_header_h2(u'Deployment update failed')
                       self._deployment_status_errors_handling(deployment_details, 'update')
               else:
                   error_msg = u'Deployment update failed'
                   reason = response.text
                   print(reason)
                   print_text_header_h2(error_msg)
                   raise WMLClientError(error_msg + u'. Error: ' + str(response.status_code) + '. ' + reason)

        return updated_details

    ## Below functions are for async scoring. They are just dummy functions.
    def _score_async(self,deployment_uid, scoring_payload, transaction_id=None):

        Deployments._validate_type(deployment_uid, u'deployment_id', STR_TYPE, True)
        Deployments._validate_type(scoring_payload, u'scoring_payload', dict, True)
        headers = self._client._get_headers()

        if transaction_id is not None:
            headers.update({'x-global-transaction-id': transaction_id})
        # making change - connection keep alive
        scoring_url = self._href_definitions.get_async_deployment_job_href()
        if not self._ICP:
            response_scoring = self.session.post(
                scoring_url,
                json=scoring_payload,
                headers=headers)
        else:
            response_scoring = self.session.post(
                scoring_url,
                json=scoring_payload,
                headers=headers,
                verify=False)
        return self._handle_response(202, u'scoring asynchronously', response_scoring)

    def create_job(self,deployment_id,meta_props):
        """
            Create an asynchronous deployment job.

            **Parameters**

            .. important::

                #. **deployment_id**:  Deployment UID\n
                   **type**: str\n

                #. **meta_props**: metaprops. To see the available list of metanames use:\n
                                   >>> client.deployments.ScoringMetaNames.get() or client.deployments.DecisionOptimizationmetaNames.get()

                   **type**: dict\n

            **Output**

            .. important::

                **returns**: metadata of the created async deployment job\n
                **return type**: dict\n

            .. note::

                * The valid payloads for scoring input are either list of values, pandas or numpy dataframes.

            **Example**

             >>> scoring_payload = {wml_client.deployments.ScoringMetaNames.INPUT_DATA: [{'fields': ['GENDER','AGE','MARITAL_STATUS','PROFESSION'], 'values': [['M',23,'Single','Student'],['M',55,'Single','Executive']]}]}
             >>> async_job = client.deployments.create_job(deployment_id, scoring_payload)
         """
        Deployments._validate_type(deployment_id, u'deployment_uid', STR_TYPE, True)
        Deployments._validate_type(meta_props, u'meta_props', dict, True)

        scoring_data = None
        flag = 0 ## To see if it is async scoring or DecisionOptimization Job

        payload = self.ScoringMetaNames._generate_resource_metadata(meta_props, with_validation=True,
                                                                    client=self._client)

        if payload != {}:
            if "input_data" in payload["scoring"]:
                scoring_data = payload["scoring"]["input_data"]
        if payload == {}:
            flag = 1
            payload = self.DecisionOptimizationMetaNames._generate_resource_metadata(meta_props, with_validation=True,
                                                                        client=self._client)
            if "input_data" in payload["decision_optimization"]:
                scoring_data = payload["decision_optimization"]["input_data"]

        if scoring_data is not None:
            score_payload = []
            for each_score_request in scoring_data:
                lib_checker.check_lib(lib_name='pandas')
                import pandas as pd

                scoring_values = each_score_request["values"]
                # Check feature types, currently supporting pandas df, numpy.ndarray, python lists and Dmatrix
                if (isinstance(scoring_values, pd.DataFrame)):
                    fields_names = scoring_values.columns.values.tolist()
                    values = scoring_values.values.tolist()

                    each_score_request["values"] = values
                    if fields_names is not None:
                        each_score_request["fields"] = fields_names


                ## If payload is a numpy dataframe

                elif (isinstance(scoring_values, np.ndarray)):

                    values = scoring_values.tolist()
                    each_score_request["values"] = values


                # else:
                #     payload_score["values"] = each_score_request["values"]
                #     if "fields" in each_score_request:
                #         payload_score["fields"] = each_score_request["fields"]
                score_payload.append(each_score_request)

            ##See if it is scoring or DecisionOptimizationJob

            if flag == 0:
                payload["scoring"]["input_data"] = score_payload
            if flag == 1:
                payload["decision_optimization"]["input_data"] = score_payload

        payload.update({"deployment": {"href": "/v4/deployments/" + deployment_id}})
        return self._score_async(deployment_id, payload, transaction_id=None)

    def get_job_details(self,job_uid=None,limit=None):
        """
           Get information about your deployment job(s). If job_uid is not passed, all deployment jobs details are fetched.

           **Parameters**

           .. important::

                #. **job_uid**: Job UID (optional)\n
                   **type**: str\n
                #. **limit**:  limit number of fetched records (optional)\n
                   **type**: int\n

           **Output**

           .. important::
                **returns**: metadata of deployment job(s)\n
                **return type**: dict\n
                dict (if job UID is not None) or {"resources": [dict]} (if job UID is None)\n

           .. note::
                If job UID is not specified, all deployment jobs metadata associated with the deployment UID is fetched\n


           **Example**

            >>> deployment_details = client.deployments.get_job_details()
            >>> deployments_details = client.deployments.get_job_details(job_uid=job_uid)
        """
        #Deployments._validate_type(job_uid, u'deployment_uid', STR_TYPE, True)
        #Deployments._validate_type(job_uid, u'job_uid', STR_TYPE, True)
        url = self._href_definitions.get_async_deployment_job_href()
        return self._get_artifact_details(url, job_uid, limit, 'async deployment jobs')

        # headers = self._client._get_headers()
        # url = self._href_definitions.get_async_deployment_jobs_href(deployment_uid, job_uid)
        #
        # if not self._ICP:
        #     response_scoring = requests.get(
        #         url,
        #         headers=headers)
        # else:
        #     response_scoring = requests.get(
        #         url,
        #         headers=headers,
        #         verify=False)
        #
        # return self._handle_response(200, u' deployment job status', response_scoring)

    def get_job_status(self, job_id):
        """
           Get the status of the deployment job.

           **Parameters**

           .. important::
                #. **job_id**: UID of the deployment job\n
                   **type**: str\n

           **Output**

           .. important::
                **returns**: status of the deployment job\n
                **return type**: dict\n

           **Example**

            >>> job_status = client.deployments.get_job_status(job_uid)
        """
        job_details = self.get_job_details(job_id)

        if 'scoring' not in job_details['entity']:
            return job_details['entity']['decision_optimization']['status']
        return job_details['entity']['scoring']['status']

    def get_job_uid(self, job_details):
        """
           Get the UID of the deployment job.

           **Parameters**

           .. important::
                #. **job_details**: metadata of the deployment job\n
                   **type**: dict\n

           **Output**

           .. important::
                **returns**: UID of the deployment job\n
                **return type**: str\n

           **Example**

            >>> job_details = client.deployments.get_job_details(job_uid=job_uid)
            >>> job_status = client.deployments.get_job_uid(job_details)
        """

        return job_details['metadata']['guid']

    def get_job_href(self, job_details):
        """
           Get the href of the deployment job.

           **Parameters**

           .. important::
                #. **job_details**: metadata of the deployment job\n
                   **type**: dict\n

           **Output**

           .. important::
                **returns**: href of the deployment job\n
                **return type**: str\n

           **Example**

            >>> job_details = client.deployments.get_job_details(job_uid=job_uid)
            >>> job_status = client.deployments.get_job_href(job_details)
        """

        return job_details['metadata']['href']

    def delete_job(self, job_uid,hard_delete=False):
        """
                Cancels a deployment job.

                **Parameters**

                .. important::

                    #. **job_uid**:  UID of deployment job which  should be canceled\n
                       **type**: str\n

                **Output**

                .. important::

                    **returns**: status ("SUCCESS" or "FAILED")\n
                    **return type**: str\n

                **Example**

                 >>> client.deployments.delete_job(job_uid)
        """

        job_uid = str_type_conv(job_uid)

        Deployments._validate_type(job_uid, u'job_uid', STR_TYPE, True)


        if job_uid is not None and not is_uid(job_uid):
            raise WMLClientError(u'\'job_uid\' is not an uid: \'{}\''.format(job_uid))


        url = self._href_definitions.get_async_deployment_jobs_href(job_uid)
        params = None
        if hard_delete is True:
            params = {}
            params.update({'hard_delete': u'true'})
        if not self._ICP:
            response_delete = requests.delete(
                url,
                headers=self._client._get_headers(),
                params=params)
        else:
            response_delete = requests.delete(
                url,
                headers=self._client._get_headers(),
                params=params,
                verify=False)

        return self._handle_response(204, u'deployment async job deletion', response_delete, False)


    # def create_environment(self, meta_props):
    #     """
    #             Cancels a job.
    #
    #             **Parameters**
    #
    #             .. important::
    #
    #                 #. **job_uid**:  UID of job which  should be canceled\n
    #                    **type**: str\n
    #
    #             **Output**
    #
    #             .. important::
    #
    #                 **returns**: status ("SUCCESS" or "FAILED")\n
    #                 **return type**: str\n
    #
    #             **Example**
    #
    #              >>> client.deployments.delete_job(job_uid)
    #     """
    #
    #     Deployments._validate_type(meta_props, u'metaprops', dict, True)
    #
    #
    #     url = self._href_definitions.get_envs_href()
    #     metadata = self.EnvironmentMetanames._generate_resource_metadata(meta_props)
    #
    #     if not self._ICP:
    #         response_post = requests.post(url, json=metadata,
    #                                           headers=self._client._get_headers())
    #
    #
    #     else:
    #         response_post = requests.post(url, json=metadata,
    #                                       headers=self._client._get_headers(), verify=False)
    #
    #     return self._handle_response(201, u'deployment job deletion', response_post, False)
    #
    # def delete_environment(self, env_id):
    #     """
    #             Cancels a job.
    #
    #             **Parameters**
    #
    #             .. important::
    #
    #                 #. **job_uid**:  UID of job which  should be canceled\n
    #                    **type**: str\n
    #
    #             **Output**
    #
    #             .. important::
    #
    #                 **returns**: status ("SUCCESS" or "FAILED")\n
    #                 **return type**: str\n
    #
    #             **Example**
    #
    #              >>> client.deployments.delete_job(job_uid)
    #     """
    #
    #     env_id = str_type_conv(env_id)
    #
    #     Deployments._validate_type(env_id, u'env_uid', STR_TYPE, True)
    #
    #
    #     if env_id is not None and not is_uid(env_id):
    #         raise WMLClientError(u'\'env_id\' is not an uid: \'{}\''.format(env_id))
    #
    #
    #     url = self._href_definitions.get_env_href(env_id)
    #
    #     if not self._ICP:
    #         response_delete = requests.delete(
    #             url,
    #             headers=self._client._get_headers())
    #     else:
    #         response_delete = requests.delete(
    #             url,
    #             headers=self._client._get_headers(),
    #             verify=False)
    #
    #     return self._handle_response(204, u'environment deletion', response_delete, False)
    #
    # def get_environment_uid(self, env_details):
    #     """
    #        Get the UID of the environment.
    #
    #        **Parameters**
    #
    #        .. important::
    #             #. **job_details**: metadata of the job\n
    #                **type**: dict\n
    #
    #        **Output**
    #
    #        .. important::
    #             **returns**: UID of the job\n
    #             **return type**: str\n
    #
    #        **Example**
    #
    #         >>> job_details = client.deployments.get_job_details(deployment_uid=deployment_uid,job_uid=job_uid)
    #         >>> job_status = client.deployments.get_job_uid(job_details)
    #     """
    #
    #     return env_details['metadata']['guid']
    #
    # def get_environment_href(self, env_details):
    #     """
    #        Get the href of the job.
    #
    #        **Parameters**
    #
    #        .. important::
    #             #. **job_details**: metadata of the job\n
    #                **type**: dict\n
    #
    #        **Output**
    #
    #        .. important::
    #             **returns**: href of the job\n
    #             **return type**: str\n
    #
    #        **Example**
    #
    #         >>> job_details = client.deployments.get_job_details(deployment_uid=deployment_uid,job_uid=job_uid)
    #         >>> job_status = client.deployments.get_job_href(job_details)
    #     """
    #
    #     return env_details['metadata']['href']
    #
    # def get_environment_details(self,env_id=None,limit=None):
    #     """
    #        Get information about your job(s). If job_uid is not passed, all jobs details are fetched.
    #
    #        **Parameters**
    #
    #        .. important::
    #
    #             #. **job_uid**: Job UID (optional)\n
    #                **type**: str\n
    #             #. **limit**:  limit number of fetched records (optional)\n
    #                **type**: int\n
    #
    #        **Output**
    #
    #        .. important::
    #             **returns**: metadata of job(s)\n
    #             **return type**: dict\n
    #             dict (if job UID is not None) or {"resources": [dict]} (if job UID is None)\n
    #
    #        .. note::
    #             If job UID is not specified, all jobs metadata associated with the deployment UID is fetched\n
    #
    #
    #        **Example**
    #
    #         >>> deployment_details = client.deployments.get_job_details()
    #         >>> deployments_details = client.deployments.get_job_details(job_uid=job_uid)
    #     """
    #     #Deployments._validate_type(job_uid, u'deployment_uid', STR_TYPE, True)
    #     #Deployments._validate_type(job_uid, u'job_uid', STR_TYPE, True)
    #     url = self._href_definitions.get_envs_href()
    #     return self._get_artifact_details(url, env_id, limit, 'get environments details')
    #
    # def list_environments(self,limit=None):
    #     """
    #        List the async jobs. If limit is set to None there will be only first 50 records shown.
    #
    #        **Parameters**
    #
    #        .. important::
    #             #. **limit**:  limit number of fetched records\n
    #                **type**: int\n
    #
    #        **Output**
    #
    #        .. important::
    #             This method only prints the list of all async jobs in a table format.\n
    #             **return type**: None\n
    #
    #        **Example**
    #
    #         >>> client.deployments.list_jobs()
    #     """
    #     details = self.get_environment_details()
    #     resources = details[u'resources']
    #     values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'],
    #                m[u'metadata'][u'created_at']) for m in resources]
    #
    #     self._list(values, [u'GUID', u'NAME', u'CREATED'], None, 50)

