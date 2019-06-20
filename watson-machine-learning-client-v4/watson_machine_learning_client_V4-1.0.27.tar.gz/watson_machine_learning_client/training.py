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
from watson_machine_learning_client.utils import print_text_header_h1, print_text_header_h2, TRAINING_RUN_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, str_type_conv, meta_props_str_conv, group_metrics, StatusLogger
import time
from watson_machine_learning_client.metanames import TrainingConfigurationMetaNames
from watson_machine_learning_client.wml_client_error import WMLClientError
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource
from ibm_boto3.exceptions import Boto3Error


class Training(WMLResource):
    """
       Train new models.
    """

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        self._ICP = client.ICP
        self.ConfigurationMetaNames = TrainingConfigurationMetaNames()

    @staticmethod
    def _is_training_uid(s):
        res = re.match('p\-[a-zA-Z0-9\-\_]+', s)
        return res is not None

    @staticmethod
    def _is_training_url(s):
        res = re.match('\/v3\/models\/p\-[a-zA-Z0-9\-\_]+', s)
        return res is not None
    
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_status(self, training_uid):
        """
                Get the status of a training created.

                **Parameters**

                .. important::
                    #. **training_uid**:  training UID\n
                       **type**: str\n

                **Output**

                .. important::
                    **returns**: training_status\n
                    **return type**: dict\n

                **Example**

                 >>> training_status = client.training.get_status(training_uid)
        """

        training_uid = str_type_conv(training_uid)
        Training._validate_type(training_uid, 'training_uid', STR_TYPE, True)

        details = self.get_details(training_uid)

        if details is not None:
            return WMLResource._get_required_element_from_dict(details, u'details', [u'entity', u'status'])
        else:
            raise WMLClientError(u'Getting trained model status failed. Unable to get model details for training_uid: \'{}\'.'.format(training_uid))

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, training_uid=None, limit=None):
        """
           Get metadata of training(s). If training UID is not specified returns all model spaces metadata.

           **Parameters**

           .. important::
                #. **training_uid**: Training UID (optional)\n
                   **type**: str\n
                #. **limit**:  limit number of fetched records (optional)\n
                   **type**: int\n

           **Output**

           .. important::
                **returns**: metadata of training(s)\n
                **return type**: dict
                The output can be {"resources": [dict]} or a dict\n

           .. note::
                If UID is not specified, all trainings metadata is fetched\n

           **Example**

            >>> training_run_details = client.training.get_details(training_uid)
            >>> training_runs_details = client.training.get_details()
        """

        training_uid = str_type_conv(training_uid)
        Training._validate_type(training_uid, 'training_uid', STR_TYPE, False)

        url = self._href_definitions.get_trainings_href()

        return self._get_artifact_details(url, training_uid, limit, 'trained models')

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_href(training_details):
        """
            Get training_href from training details.

            **Parameters**

            .. important::
                #. **training_details**:  Metadata of the training created\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: training href\n
                **return type**: str

            **Example**

             >>> training_details = client.training.get_details(training_uid)
             >>> run_url = client.training.get_href(training_details)
        """

        Training._validate_type(training_details, u'training_details', object, True)
        Training._validate_type_of_details(training_details, TRAINING_RUN_DETAILS_TYPE)
        return WMLResource._get_required_element_from_dict(training_details, u'training_details', [u'metadata', u'href'])

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(training_details):
        """
            Get training_uid from training details.

            **Parameters**

            .. important::
                #. **training_details**:  Metadata of the training created\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: training UID\n
                **return type**: str

            **Example**

             >>> training_details = client.training.get_details(training_uid)
             >>> model_uid = client.training.get_uid(training_details)
        """

        Training._validate_type(training_details, u'training_details', object, True)
        return WMLResource._get_required_element_from_dict(training_details, u'training_details', [u'metadata', u'guid'])

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def run(self, meta_props, asynchronous=True):
        """
                Create a training

                **Parameters**

                .. important::

                    #. **meta_props**:  meta data of the training configuration. To see available meta names use:\n
                                        >>> client.training.ConfigurationMetaNames.show()

                       **type**: str\n

                    #. **asynchronous**:
                        * True  - training job is submitted and progress can be checked later.\n
                        * False - method will wait till job completion and print training stats.\n
                       **type**: bool\n


                **Output**

                .. important::

                    **returns**: Metadata of the training created\n
                    **return type**: dict\n

                **Example**

                    >>> metadata = {
                    >>>  client.training.ConfigurationMetaNames.NAME: 'Hand-written Digit Recognition',
                    >>>  client.training.ConfigurationMetaNames.TRAINING_DATA_REFERENCES: [{
                    >>>          'connection': {
                    >>>              'endpoint_url': 'https://s3-api.us-geo.objectstorage.service.networklayer.com',
                    >>>              'access_key_id': '***',
                    >>>              'secret_access_key': '***'
                    >>>          },
                    >>>          'source': {
                    >>>              'bucket': 'wml-dev',
                    >>>          }
                    >>>          'type': 's3'
                    >>>      }],
                    >>> client.training.ConfigurationMetaNames.TRAINING_RESULTS_REFERENCE: {
                    >>>          'connection': {
                    >>>              'endpoint_url': 'https://s3-api.us-geo.objectstorage.service.networklayer.com',
                    >>>              'access_key_id': '***',
                    >>>              'secret_access_key': '***'
                    >>>          },
                    >>>          'target': {
                    >>>              'bucket': 'wml-dev-results',
                    >>>          }
                    >>>          'type': 's3'
                    >>>      },
                    >>> client.training.ConfigurationMetaNames.PIPELINE_UID : "/v4/pipelines/<PIPELINE-ID>"
                    >>> }
                    >>> training_details = client.training.run(definition_uid, meta_props=metadata)
                    >>> training_uid = client.training.get_uid(training_details)
        """

        Training._validate_type(meta_props, 'meta_props', object, True)
        Training._validate_type(asynchronous, 'asynchronous', bool, True)

        meta_props_str_conv(meta_props)
        self.ConfigurationMetaNames._validate(meta_props)
        training_configuration_metadata = {

            u'training_data_references': meta_props[self.ConfigurationMetaNames.TRAINING_DATA_REFERENCES],
            u'results_reference': meta_props[self.ConfigurationMetaNames.TRAINING_RESULTS_REFERENCE]
        }

        # TODO remove when training service starts copying such data on their own

        if self.ConfigurationMetaNames.PIPELINE_UID in meta_props:
            training_configuration_metadata["pipeline"] = {
                "href": "/v4/pipelines/"+meta_props[self.ConfigurationMetaNames.PIPELINE_UID]
            }
            if self.ConfigurationMetaNames.PIPELINE_DATA_BINDINGS in meta_props:
                training_configuration_metadata["pipeline"]["data_bindings"] = meta_props[self.ConfigurationMetaNames.PIPELINE_DATA_BINDINGS]
            if self.ConfigurationMetaNames.PIPELINE_NODE_PARAMETERS in meta_props:
                training_configuration_metadata["pipeline"]["nodes_parameters"] = meta_props[
                    self.ConfigurationMetaNames.PIPELINE_NODE_PARAMETERS]
            if self.ConfigurationMetaNames.PIPELINE_MODEL_TYPE in meta_props:
                training_configuration_metadata["pipeline"]["model_type"] = meta_props[
                    self.ConfigurationMetaNames.PIPELINE_MODEL_TYPE]

        if self.ConfigurationMetaNames.EXPERIMENT_UID in meta_props:
            training_configuration_metadata["experiment"] = {
                "href": "/v4/experiments/"+meta_props[self.ConfigurationMetaNames.EXPERIMENT_UID]
            }
        # else:
        #     raise WMLClientError(u'Invalid pipeline/experiment uid: \'{}\'.'.format(uid))


        if self.ConfigurationMetaNames.TAGS in meta_props:
            training_configuration_metadata["tags"] = meta_props[self.ConfigurationMetaNames.TAGS]

        if self.ConfigurationMetaNames.TRAINING_LIB in meta_props:
            training_configuration_metadata["training_lib"] =  meta_props[self.ConfigurationMetaNames.TRAINING_LIB]

        train_endpoint = self._href_definitions.get_trainings_href()
        if not self._ICP:
         response_train_post = requests.post(train_endpoint, json=training_configuration_metadata,
                                            headers=self._client._get_headers())

        else:
         response_train_post = requests.post(train_endpoint, json=training_configuration_metadata,
                                                headers=self._client._get_headers(),verify=False)

        run_details = self._handle_response(201, u'training', response_train_post)

        trained_model_guid = self.get_uid(run_details)

        if asynchronous is True:
            return run_details
        else:
            print_text_header_h1(u'Running \'{}\''.format(trained_model_guid))

            status = self.get_status(trained_model_guid)
            state = status[u'state']

            with StatusLogger(state) as status_logger:
                while state not in ['error', 'completed', 'canceled']:
                    time.sleep(5)
                    state = self.get_status(trained_model_guid)['state']
                    status_logger.log_state(state)

            if u'completed' in state:
                print(u'\nTraining of \'{}\' finished successfully.'.format(str(trained_model_guid)))
            else:
                print(u'\nTraining of \'{}\' failed with status: \'{}\'.'.format(trained_model_guid, str(status)))

            self._logger.debug(u'Response({}): {}'.format(state, run_details))
            return self.get_details(trained_model_guid)

    def list(self, limit=None):
        """
           List stored trainings. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all trainings in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.training.list()
        """

        details = self.get_details()
        resources = details[u'resources']
        values = [(m[u'metadata'][u'guid'], m[u'entity'][u'status'][u'state'], m[u'metadata'][u'created_at']) for m in resources]

        self._list(values, [u'GUID (training)', u'STATE', u'CREATED'], limit, 50)

    def list_subtrainings(self, training_uid):
        """
           List the sub-trainings.

           **Parameters**

           .. important::
                #. **training_uid**:  Training GUID\n
                   **type**: str\n

           **Output**

           .. important::
                This method only prints the list of all sub-trainings associated with a training in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.training.list_subtrainings()
        """

        details = self.get_details(training_uid)
        if "experiment" not in details["entity"]:
            raise WMLClientError("Sub-trainings are available for training created via experiment only.")
        resources = details[u'entity']["sub_trainings"]
        values = [(m[u'metadata'][u'guid'], m[u'entity'][u'status'][u'state'], m[u'metadata'][u'created_at']) for m in resources]

        self._list(values, [u'GUID (sub_training)', u'STATE', u'CREATED'], None, 50)

    def list_intermediate_models(self, training_uid):
        """
           List the intermediate_models.

           **Parameters**

           .. important::
                #. **training_uid**:  Training GUID\n
                   **type**: str\n

           **Output**

           .. important::
                This method only prints the list of all intermediate_models associated with an AUTOAI training in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.training.list_intermediate_models()
        """

        details = self.get_details(training_uid)
        #if status is completed then only lists only global_output else display message saying "state value"
        training_state = details[u'entity'][u'status'][u'state']
        if(training_state=='completed'):

            metrics_list =  details[u'entity'][u'status'][u'metrics']
            new_list=[]
            for ml in metrics_list:
                # if(ml[u'context'][u'intermediate_model'][u'process']=='global_output'):
                    name=ml[u'context'][u'intermediate_model'][u'name']
                    path=ml[u'context'][u'intermediate_model'][u'location'][u'model']
                    accuracy=ml[u'ml_metrics'][u'training_accuracy']
                    F1Micro=round(ml[u'ml_metrics'][u'training_f1_micro'],2)
                    F1Macro = round(ml[u'ml_metrics'][u'training_f1_macro'],2)
                    F1Weighted = round(ml[u'ml_metrics'][u'training_f1_weighted'],2)
                    logLoss=round(ml[u'ml_metrics'][u'training_neg_log_loss'],2)
                    PrecisionMicro = round(ml[u'ml_metrics'][u'training_precision_micro'],2)
                    PrecisionWeighted = round(ml[u'ml_metrics'][u'training_precision_weighted'],2)
                    PrecisionMacro = round(ml[u'ml_metrics'][u'training_precision_macro'],2)
                    RecallMacro = round(ml[u'ml_metrics'][u'training_recall_macro'],2)
                    RecallMicro = round(ml[u'ml_metrics'][u'training_recall_micro'],2)
                    RecallWeighted = round(ml[u'ml_metrics'][u'training_recall_weighted'],2)
                    createdAt = details[u'metadata'][u'created_at']
                    new_list.append([name,path,accuracy,F1Micro,F1Macro,F1Weighted,logLoss,PrecisionMicro,PrecisionMacro,PrecisionWeighted,RecallMicro,RecallMacro,RecallWeighted,createdAt])
                    new_list.append([])

            from tabulate import tabulate
            header = [u'NAME', u'PATH', u'Accuracy', u'F1Micro', u'F1Macro', u'F1Weighted', u'LogLoss', u'PrecisionMicro' , u'PrecisionMacro',u'PrecisionWeighted', u'RecallMicro', u'RecallMacro', u'RecallWeighted', u'CreatedAt' ]
            table = tabulate([header] + new_list)

            print(table)
            #self._list(new_list, [u'NAME', u'PATH', u'Accuracy', u'F1Micro', u'F1Macro', u'F1Weighted', u'LogLoss', u'PrecisionMicro' , u'PrecisionMacro',u'PrecisionWeighted', u'RecallMicro', u'RecallMacro', u'RecallWeighted', u'CreatedAt' ], None, 50)

        else:
            self._logger.debug("state is not completed")




    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, training_uid,hard_delete=False):
        """
            Delete a training.

            **Parameters**

            .. important::
                #. **training_uid**:  Training UID\n
                   **type**: str\n

            **Output**

            .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n

            **Example**

             >>> client.training.delete(training_uid)
        """

        training_uid = str_type_conv(training_uid)
        Training._validate_type(training_uid, u'training_uid', STR_TYPE, True)
        params = None
        if hard_delete is True:
            params = {}
            params.update({'hard_delete': u'true'})
        if not self._ICP:
         response_delete = requests.delete(self._href_definitions.get_training_href(training_uid),
                                          headers=self._client._get_headers(),params=params)
        else:
         response_delete = requests.delete(self._href_definitions.get_training_href(training_uid),
                                              headers=self._client._get_headers(),params=params,verify=False)

        return self._handle_response(200, u'trained model deletion', response_delete, False)

    def _COS_logs(self, run_uid,on_start=lambda: {}):
        on_start()
        run_details = self.get_details(run_uid)
        endpoint_url = run_details["entity"]["results_reference"]["connection"]["endpoint_url"]
        aws_access_key = run_details["entity"]["results_reference"]["connection"]["access_key_id"]
        aws_secret = run_details["entity"]["results_reference"]["connection"]["secret_access_key"]
        bucket = run_details["entity"]["results_reference"]["location"]["bucket"]
        # try:
        #     run_details["entity"]["training_results_reference"]["location"]["model_location"]
        # except:
        #     raise WMLClientError("The training-run has not started. Error - " + run_details["entity"]["status"]["error"]["errors"][0]["message"])

        if (bucket == ""):
            bucket = run_details["entity"]["results_reference"]["target"]["bucket"]
        import ibm_boto3

        client_cos = ibm_boto3.client(service_name='s3', aws_access_key_id=aws_access_key,
                                      aws_secret_access_key=aws_secret,
                                      endpoint_url=endpoint_url)

        try:
            try:
                key = run_details["metadata"]["guid"] + "/pipeline-model.json"

                obj = client_cos.get_object(Bucket=bucket, Key=key)
                pipeline_model = json.loads((obj['Body'].read().decode('utf-8')))

            except ibm_boto3.exceptions.ibm_botocore.client.ClientError as ex:
                if ex.response['Error']['Code'] == 'NoSuchKey':
                    print("ERROR - Cannot find pipeline_model.json in the bucket "+ run_uid)
                else:
                    print(ex)
            key = pipeline_model["pipelines"][0]["nodes"][0]["parameters"]["model_id"] + "/learner-1/training-log.txt"
            obj = client_cos.get_object(Bucket=bucket, Key=key)
            print(obj['Body'].read().decode('utf-8'))
        except ibm_boto3.exceptions.ibm_botocore.client.ClientError as ex:

            if ex.response['Error']['Code'] == 'NoSuchKey':
                print("ERROR - Cannot find training-log.txt in the bucket")
            else:
                print(ex)

    def _COS_metrics(self, run_uid,on_start=lambda: {}):
        on_start()
        run_details = self.get_details(run_uid)
        endpoint_url = run_details["entity"]["results_reference"]["connection"]["endpoint_url"]
        aws_access_key = run_details["entity"]["results_reference"]["connection"]["access_key_id"]
        aws_secret = run_details["entity"]["results_reference"]["connection"]["secret_access_key"]
        bucket = run_details["entity"]["results_reference"]["location"]["bucket"]
        # try:
        #     run_details["entity"]["training_results_reference"]["location"]["model_location"]
        # except:
        #     raise WMLClientError("The training-run has not started. Error - " + run_details["entity"]["status"]["error"]["errors"][0]["message"])

        if (bucket == ""):
            bucket = run_details["entity"]["results_reference"]["target"]["bucket"]
        import ibm_boto3

        client_cos = ibm_boto3.client(service_name='s3', aws_access_key_id=aws_access_key,
                                      aws_secret_access_key=aws_secret,
                                      endpoint_url=endpoint_url)

        try:
            try:
                key = run_details["metadata"]["guid"] + "/pipeline-model.json"

                obj = client_cos.get_object(Bucket=bucket, Key=key)

                pipeline_model = json.loads((obj['Body'].read().decode('utf-8')))
            except ibm_boto3.exceptions.ibm_botocore.client.ClientError as ex:

                if ex.response['Error']['Code'] == 'NoSuchKey':
                    print("ERROR - Cannot find pipeline_model.json in the bucket "+ run_uid)
                else:
                    print(ex)
            key = pipeline_model["pipelines"][0]["nodes"][0]["parameters"]["model_id"] + "/learner-1/evaluation-metrics.txt"

            obj = client_cos.get_object(Bucket=bucket, Key=key)
            print(obj['Body'].read().decode('utf-8'))

        except ibm_boto3.exceptions.ibm_botocore.client.ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchKey':
                print("ERROR - Cannot find evaluation-metrics.txt in the bucket")
            else:
                print(ex)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def monitor_logs(self, training_uid):
        """
            Monitor the logs of a training created.

            **Parameters**

            .. important::
                #. **training_uid**:  Training UID\n
                   **type**: str\n

            **Output**

            .. important::

                **returns**: None\n
                **return type**: None\n

            .. note::

                This method prints the training logs.

            **Example**

             >>> client.training.monitor_logs(training_uid)
        """

        training_uid = str_type_conv(training_uid)
        Training._validate_type(training_uid, u'training_uid', STR_TYPE, True)

        self._simple_monitor_logs(training_uid, lambda: print_text_header_h1(u'Log monitor started for training run: ' + str(training_uid)))

        print_text_header_h2('Log monitor done.')

    def _simple_monitor_logs(self, training_uid, on_start=lambda: {}):
        run_details = self.get_details(training_uid)
        status = run_details["entity"]["status"]["state"]

        if (status == "completed" or status == "error" or status == "failed" or status == "canceled"):
            self._COS_logs(training_uid,
                           lambda: print_text_header_h1(u'Log monitor started for training run: ' + str(training_uid)))
        else:
            from lomond import WebSocket
            if not self._ICP:
             monitor_endpoint = self._wml_credentials[u'url'].replace(u'https',
                                                                     u'wss') + u'/v4/trainings/' + training_uid
            else:
             monitor_endpoint = self._wml_credentials[u'url'].replace(u'https',
                                                                         u'ws') + u'/v4/trainings/' + training_uid
            websocket = WebSocket(monitor_endpoint)
            try:
                websocket.add_header(bytes("Authorization", "utf-8"), bytes("bearer " + self._client.service_instance._get_token(), "utf-8"))
            except:
                websocket.add_header(bytes("Authorization"), bytes("bearer " + self._client.service_instance._get_token()))

            on_start()

            for event in websocket:

                if event.name == u'text':
                    text = json.loads(event.text)
                    entity = text[u'entity']
                    if 'status' in entity:
                      if 'message' in entity['status']:
                        message = entity['status']['message']
                        if len(message) > 0:
                          print(message)

            websocket.close()

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def monitor_metrics(self, training_uid):
        """
            Monitor the metrics of a training created.

            **Parameters**

            .. important::
                #. **training_uid**:  Training UID\n
                   **type**: str\n

            **Output**

            **Output**

            .. important::

                **returns**: None\n
                **return type**: None\n

            .. note::

                This method prints the training metrics.

            **Example**

             >>> client.training.monitor_metrics(training_uid)
        """

        training_uid = str_type_conv(training_uid)
        Training._validate_type(training_uid, u'training_uid', STR_TYPE, True)
        run_details = self.get_details(training_uid)
        status = run_details["entity"]["status"]["state"]

        if (status == "completed" or status == "error" or status == "failed" or status == "canceled"):
            self._COS_metrics(training_uid,
                           lambda: print_text_header_h1(u'Log monitor started for training run: ' + str(training_uid)))
        else:
            from lomond import WebSocket
            if not self._ICP:
             monitor_endpoint = self._wml_credentials[u'url'].replace(u'https',
                                                                     u'wss') + u'/v4/trainings/' + training_uid
            else:
             monitor_endpoint = self._wml_credentials[u'url'].replace(u'https',
                                                                         u'ws') + u'/v4/trainings/' + training_uid
            websocket = WebSocket(monitor_endpoint)
            try:
                websocket.add_header(bytes("Authorization", "utf-8"), bytes("bearer " + self._client.service_instance._get_token(), "utf-8"))
            except:
                websocket.add_header(bytes("Authorization"), bytes("bearer " + self._client.service_instance._get_token()))

            print_text_header_h1('Metric monitor started for training run: ' + str(training_uid))

            for event in websocket:
                if event.name == u'text':
                    text = json.loads(event.text)
                    entity = text[u'entity']
                    if 'status' in entity:
                        status = entity[u'status']
                        if u'metrics' in status:
                            metrics = status[u'metrics']
                            if len(metrics) > 0:
                             metric = metrics[0]
                             print(metric)

            websocket.close()

            print_text_header_h2('Metric monitor done.')

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_metrics(self, training_uid):
        """
                Get metrics.

                **Parameters**

                .. important::
                    #. **training_uid**:  training UID\n
                       **type**: str\n

                **Output**

                .. important::
                    **returns**: Metrics of a training run\n
                    **return type**: list of dict\n

                **Example**

                 >>> training_status = client.training.get_metrics(training_uid)
        """

        training_uid = str_type_conv(training_uid)
        Training._validate_type(training_uid, u'training_uid', STR_TYPE, True)

        status = self.get_status(training_uid)
        metrics = status['metrics']

        return metrics

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _get_latest_metrics(self, training_uid):
        """
             Get latest metrics values.

             :param training_uid: ID of trained model
             :type training_uid: {0}

             :returns: metric values
             :rtype: list of dicts

             A way you might use me is:

             >>> client.training.get_latest_metrics(training_uid)
         """
        training_uid = str_type_conv(training_uid)
        Training._validate_type(training_uid, u'training_uid', STR_TYPE, True)

        status = self.get_status(training_uid)
        metrics = status['metrics']
        latest_metrics = []

        if len(metrics) > 0:
            grouped_metrics = group_metrics(metrics)

            for key, value in grouped_metrics.items():
                sorted_value = sorted(value, key=lambda k: k['iteration'])

            latest_metrics.append(sorted_value[-1])

        return latest_metrics