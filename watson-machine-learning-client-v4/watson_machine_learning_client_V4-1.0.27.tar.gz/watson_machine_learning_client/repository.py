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
from watson_machine_learning_client.utils import get_url, INSTANCE_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, str_type_conv, is_python_2
from watson_machine_learning_client.metanames import ModelMetaNames, ExperimentMetaNames, FunctionMetaNames, PipelineMetanames, SpacesMetaNames
from watson_machine_learning_client.wml_client_error import WMLClientError
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.models import Models
from watson_machine_learning_client.experiments import Experiments
from watson_machine_learning_client.functions import Functions
from watson_machine_learning_client.pipelines import Pipelines
from watson_machine_learning_client.spaces import Spaces
from multiprocessing import Pool
from watson_machine_learning_client.libs.repo.mlrepositoryclient import MLRepositoryClient

_DEFAULT_LIST_LENGTH = 50


class Repository(WMLResource):
    """
    Store and manage your models, functions, spaces, pipelines and experiments using Watson Machine Learning Repository.
    
    .. important::
    
        #. To view ModelMetaNames, use: \n 
           >>> client.repository.ModelMetaNames.show()
        #. To view ExperimentMetaNames, use: \n 
           >>> client.repository.ExperimentMetaNames.show()
        #. To view FunctionMetaNames, use: \n 
           >>> client.repository.FunctionMetaNames.show()
        #. To view PipelineMetaNames, use: \n 
           >>> client.repository.PipelineMetaNames.show()
        #. To view SpacesMetaNames, use: \n 
           >>> client.repository.SpacesMetaNames.show()
    """

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        if not client.ICP:
            Repository._validate_type(client.service_instance.details, u'instance_details', dict, True)
            Repository._validate_type_of_details(client.service_instance.details, INSTANCE_DETAILS_TYPE)
        self._ICP = client.ICP
        self._ml_repository_client = None

        self.ExperimentMetaNames = ExperimentMetaNames()
        self.FunctionMetaNames = FunctionMetaNames()
        self.PipelineMetaNames = PipelineMetanames()
        self.SpacesMetaNames = SpacesMetaNames()
        self.ModelMetaNames = ModelMetaNames()

        self._refresh_repo_client() # regular token is initialized in service_instance

    def _refresh_repo_client(self):
        # If apiKey is passed in credentials then refresh repoclient with IAM token else MLToken
        self._ml_repository_client = MLRepositoryClient(self._wml_credentials[u'url'])
        if self._client.proceed is True:
            if self._client.service_instance._is_iam() is not None:
                self._ml_repository_client.authorize_with_token(self._client.wml_token)
                self._ml_repository_client._add_header('X-WML-User-Client', 'PythonClient')
                if self._client.project_id is not None:
                    self._ml_repository_client._add_header('X-Watson-Project-ID', self._client.project_id)
            else:
                self._ml_repository_client.authorize_with_iamtoken(self._client.wml_token,
                                                                   self._wml_credentials[u'instance_id'])
                self._ml_repository_client._add_header('X-WML-User-Client', 'PythonClient')
                self._ml_repository_client._add_header('ML-Instance-ID', self._wml_credentials[u'instance_id'])
                if self._client.project_id is not None:
                    self._ml_repository_client._add_header('X-Watson-Project-ID', self._client.project_id)
        else:
            if self._client._is_IAM():
                self._ml_repository_client.authorize_with_iamtoken(self._client.wml_token,self._wml_credentials[u'instance_id'])
                self._ml_repository_client._add_header('X-WML-User-Client', 'PythonClient')
                self._ml_repository_client._add_header('ML-Instance-ID', self._wml_credentials[u'instance_id'])
                if self._client.project_id is not None:
                    self._ml_repository_client._add_header('X-Watson-Project-ID', self._client.project_id)
            else:

                if self._ICP:
                    self._repotoken = self._client._get_icptoken()
                    self._ml_repository_token = self._repotoken.replace('Bearer', '')
                    self._ml_repository_client.authorize_with_token(self._ml_repository_token)
                else:
                    self._ml_repository_client.authorize(self._wml_credentials[u'username'], self._wml_credentials[u'password'])
                    self._ml_repository_client._add_header('X-WML-User-Client', 'PythonClient')
                    if self._client.project_id is not None:
                        self._ml_repository_client._add_header('X-Watson-Project-ID', self._client.project_id)

    def store_experiment(self, meta_props):
        """
           Create an experiment.

           **Parameters**

           .. important::
                #. **meta_props**:  meta data of the experiment configuration. To see available meta names use:\n
                                    >>> client.experiments.ConfigurationMetaNames.get()

                   **type**: dict\n

           **Output**

                .. important::
                   **returns**: Metadata of the experiment created\n
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
            >>> experiment_details = client.repository.store_experiment(meta_props=metadata)
            >>> experiment_href = client.repository.get_experiment_href(experiment_details)
        """


        return self._client.experiments.store(meta_props)


    def store_space(self, meta_props):
        """
               Create a space.

               **Parameters**

               .. important::

                    #. **meta_props**:  meta data of the space configuration. To see available meta names use:\n
                                        >>> client.spaces.ConfigurationMetaNames.get()

                       **type**: dict\n

               **Output**

               .. important::

                    **returns**: Metadata of the space created\n
                    **return type**: dict\n

               **Example**

                >>> metadata = {
                >>>  client.spaces.ConfigurationMetaNames.NAME: 'my_space'
                >>> }
                >>> space_details = client.repository.store_space(meta_props=metadata)
                >>> space_href = client.repository.get_space_href(experiment_details)
        """

        return self._client.spaces.store(meta_props)

    @staticmethod
    def _meta_props_to_repository_v3_style(meta_props):
        if is_python_2():
            new_meta_props = meta_props.copy()

            for key in new_meta_props:
                if type(new_meta_props[key]) is unicode:
                    new_meta_props[key] = str(new_meta_props[key])

            return new_meta_props
        else:
            return meta_props

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store_pipeline(self, meta_props):
        """
                Create a pipeline.

                **Parameters**

                .. important::

                   #. **meta_props**:  meta data of the pipeline configuration. To see available meta names use:\n
                                    >>> client.pipelines.ConfigurationMetaNames.get()

                      **type**: dict\n

                **Output**

                .. important::

                    **returns**: Metadata of the pipeline created\\n
                    **return type**: dict\n

                **Example**

                    >>> metadata = {
                    >>>  client.pipelines.ConfigurationMetaNames.NAME: 'my_training_definition',
                    >>>  client.pipelines.ConfigurationMetaNames.DOCUMENT: {"doc_type":"pipeline","version": "2.0","primary_pipeline": "dlaas_only","pipelines": [{"id": "dlaas_only","runtime_ref": "hybrid","nodes": [{"id": "training","type": "model_node","op": "dl_train","runtime_ref": "DL","inputs": [],"outputs": [],"parameters": {"name": "tf-mnist","description": "Simple MNIST model implemented in TF","command": "python3 convolutional_network.py --trainImagesFile ${DATA_DIR}/train-images-idx3-ubyte.gz --trainLabelsFile ${DATA_DIR}/train-labels-idx1-ubyte.gz --testImagesFile ${DATA_DIR}/t10k-images-idx3-ubyte.gz --testLabelsFile ${DATA_DIR}/t10k-labels-idx1-ubyte.gz --learningRate 0.001 --trainingIters 6000","compute": {"name": "k80","nodes": 1},"training_lib_href":"/v4/libraries/64758251-bt01-4aa5-a7ay-72639e2ff4d2/content"},"target_bucket": "wml-dev-results"}]}]}}
                    >>> pipeline_details = client.repository.store_pipeline(pipeline_filepath, meta_props=metadata)
                    >>> pipeline_href = client.repository.get_pipeline_href(pipeline_details)
        """


        return self._client.pipelines.store(meta_props)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store_model(self, model, meta_props=None, training_data=None, training_target=None, pipeline=None, feature_names=None, label_column_names=None,subtrainingId=None):
        """
                Create a model.

                **Parameters**

                .. important::

                    #. **model**:  \n
                            Can be one of following:\n
                            - The train model object:\n
                                - scikit-learn
                                - xgboost
                                - spark (PipelineModel)
                            - path to saved model in format:\n
                                - keras (.tgz)
                                - pmml (.xml)
                                - scikit-learn (.tar.gz)
                                - xgboost (.tar.gz)
                                - tensorflow (.tar.gz)
                                - spss (.str)
                            - directory containing model file(s):\n
                                - scikit-learn
                                - xgboost
                                - tensorflow
                            - trained model UID
                    #. **training_data**:  Spark DataFrame supported for spark models. Pandas dataframe, numpy.ndarray or array supported for scikit-learn models\n
                       **type**: spark dataframe, pandas dataframe, numpy.ndarray or array\n

                    #. **meta_props**:  meta data of the models configuration. To see available meta names use:\n
                                        >>> client.repository.ModelMetaNames.get()

                       **type**: dict\n

                    #. **training_target**:  array with labels required for scikit-learn models\n
                       **type**: array\n

                    #. **pipeline**:  pipeline required for spark mllib models\n
                       **type**: object\n

                    #. **feature_names**:  Feature names for the training data in case of Scikit-Learn/XGBoost models. This is applicable only in the case where the training data is not of type - pandas.DataFrame.\n
                       **type**: numpy.ndarray or list\n

                    #. **label_column_names**:  Label column names of the trained Scikit-Learn/XGBoost models.\n
                       **type**: numpy.ndarray and list\n

                    #. **subtrainingId**:  The subtraining ID for a training created via an experiment.\n
                       **type**: str\n

                **Output**

                .. important::

                    **returns**: Metadata of the model created\n
                    **return type**: dict\n

                .. note::

                    * For a keras model, model content is expected to contain a .h5 file and an archived version of it.\n

                    * For deploying a keras model, it is mandatory to pass the FRAMEWORK_LIBRARIES along with other metaprops.\n
                      >>> client.repository.ModelMetaNames.FRAMEWORK_LIBRARIES: [{'name':'keras', 'version': '2.1.3'}]

                    * feature_names is an optional argument containing the feature names for the training data in case of Scikit-Learn/XGBoost models. Valid types are numpy.ndarray and list. This is applicable only in the case where the training data is not of type - pandas.DataFrame.\n

                    * If the training data is of type pandas.DataFrame and feature_names are provided, feature_names are ignored.\n

                **Example**

                    >>> stored_model_details = client.repository.store_model(model, name)

                    In more complicated cases you should create proper metadata, similar to this one:\n

                    >>> metadata = {
                    >>>        client.repository.ModelMetaNames.NAME: 'customer satisfaction prediction model',
                    >>>        client.repository.ModelMetaNames.TYPE: 'tensorflow_1.5',
                    >>>        client.repository.ModelMetaNames.RUNTIME_UID: 'tensorflow_1.5-py3'
                    >>>}

                    A way you might use me with local tar.gz containing model:\n

                    >>> stored_model_details = client.repository.store_model(path_to_tar_gz, meta_props=metadata, training_data=None)

                    A way you might use me with local directory containing model file(s):\n

                    >>> stored_model_details = client.repository.store_model(path_to_model_directory, meta_props=metadata, training_data=None)

                    A way you might use me with trained model guid:\n

                    >>> stored_model_details = client.repository.store_model(trained_model_guid, meta_props=metadata, training_data=None)
            """

        return self._client._models.store(model, meta_props=meta_props, training_data=training_data, training_target=training_target, pipeline=pipeline, feature_names=feature_names, label_column_names=label_column_names,subtrainingId=subtrainingId)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store_function(self, function, meta_props):
        """
            Create a function.

            **Parameters**

            .. important::
                #. **meta_props**:  meta data or name of the function. To see available meta names use:\n
                                    >>> client.functions.ConfigurationMetaNames.get()

                       **type**: dict\n
                #. **function**:  path to file with archived function content or function (as described above)\n
                         - As a 'function' may be used one of the following:\n
                         - filepath to gz file\n
                         - 'score' function reference, where the function is the function which will be deployed\n
                         - generator function, which takes no argument or arguments which all have primitive python default values and as result return 'score' function\n
                   **type**: str or function\n

            **Output**

            .. important::

                    **returns**: Metadata of the function created.\n
                    **return type**: dict\n

            **Example**

             The most simple use is (using `score` function):

             >>> def score(payload):
             >>>      values = [[row[0]*row[1]] for row in payload['values']]
             >>>      return {'fields': ['multiplication'], 'values': values}
             >>> stored_function_details = client.functions.store(score, name)

             Other, more interesting example is using generator function.
             In this situation it is possible to pass some variables:

                >>> wml_creds = {...}
                >>> def gen_function(wml_credentials=wml_creds, x=2):
                        def f(payload):
                            values = [[row[0]*row[1]*x] for row in payload['values']]
                            return {'fields': ['multiplication'], 'values': values}
                        return f
                >>> stored_function_details = client.functions.store(gen_function, name)

             In more complicated cases you should create proper metadata, similar to this one:

                >>> metadata = {
                >>>    client.repository.FunctionMetaNames.NAME: "function",
                >>>    client.repository.FunctionMetaNames.DESCRIPTION: "This is ai function",
                >>>    client.repository.FunctionMetaNames.RUNTIME_UID: "53dc4cf1-252f-424b-b52d-5cdd9814987f",
                >>>    client.repository.FunctionMetaNames.INPUT_DATA_SCHEMAS: [{"fields": [{"metadata": {}, "type": "string", "name": "GENDER", "nullable": True}]}],
                >>>    client.repository.FunctionMetaNames.OUTPUT_DATA_SCHEMAS:[{"fields": [{"metadata": {}, "type": "string", "name": "GENDER", "nullable": True}]}],
                >>>    client.repository.FunctionMetaNames.TAGS: [{"value": "ProjectA", "description": "Functions created for ProjectA"}]
                >>> }
                >>> stored_function_details = client.repository.store_function(score, metadata)
            """

        return self._client._functions.store(function, meta_props)


    def _create_model_revision(self, model, model_uid, meta_props = None):
        """
        Create a new version for a model.

        .. note::
            Model version creation is not allowed for spark models

        :param model:  Can be one of following:
            - path to saved model in format:
                - keras (.tgz)
                - pmml (.xml)
                - scikit-learn (.tar.gz)
                - xgboost (.tar.gz)
                - tensorflow (.tar.gz)
                - spss (.str)
            - trained model guid
        :type model: {str_type}

        :param meta_props: meta data of the model. To see available meta names use:

            >>> client.repository.ModelMetaNames.get()

        :type meta_props: dict/{str_type}

        :param model_uid:  model ID
        :type model_uid: {str_type}

        :returns: model version details
        :rtype: dict

        Example:

        >>> metadata = {
        >>>        client.repository.ModelMetaNames.NAME: 'SAMPLE NAME',
        >>>        client.repository.ModelMetaNames.DESCRIPTION: 'SAMPLE DESCRIPTION',
        >>>        client.repository.ModelMetaNames.AUTHOR_NAME: 'AUTHOR',
        >>>        client.repository.ModelMetaNames.FRAMEWORK_NAME: 'pmml',
        >>>        client.repository.ModelMetaNames.FRAMEWORK_VERSION: '4.3'
        >>>}

        A way you might use me with local tar.gz containing model:

        >>> stored_model_details = client.repository.create_version(path_to_tar_gz, model_uid="MODELID" ,meta_props=metadata)

        A way you might use me with trained model guid:

        >>> stored_model_details = client.repository.create_version(trained_model_guid, model_uid="MODELID" ,meta_props=metadata)
        """
        return self._client._models.store(model, meta_props, version=True, artifactid=model_uid)

    def update_model(self, model_uid, changes=None):
        """
                Updates existing model metadata.

                **Parameters**

                .. important::

                    #. **model_uid**:  UID of model which definition should be updated\n
                       **type**: str\n

                    #. **changes**:  elements which should be changed, where keys are ConfigurationMetaNames\n
                       **type**: dict\n

                **Output**

                .. important::

                      **returns**: metadata of updated model\n
                      **return type**: dict\n

                **Example**

                 >>> metadata = {
                 >>> client.repository.ModelMetaNames.NAME:"updated_model"
                 >>> }
                 >>> model_details = client.repository.update_model(model_uid, changes=metadata)

        """

        return self._client._models.update(model_uid, changes)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def update_experiment(self, experiment_uid, changes):
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
                 >>> client.repository.ExperimentMetaNames.NAME:"updated_exp"
                 >>> }
                 >>> exp_details = client.repository.update_experiment(experiment_uid, changes=metadata)

        """

        return self._client.experiments.update(experiment_uid, changes)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def update_function(self, function_uid, changes):
        """
                Updates existing function metadata.

                **Parameters**

                .. important::

                       #. **function_uid**:  UID of function which define what should be updated\n
                          **type**: str\n
                       #. **changes**:  elements which should be changed, where keys are ConfigurationMetaNames\n
                          **type**: dict\n

                **Output**

                .. important::

                       **returns**: metadata of updated function\n
                       **return type**: dict\n

                **Example**

                 >>> metadata = {
                 >>> client.repository.FunctionMetaNames.NAME:"updated_function"
                 >>> }
                 >>> function_details = client.repository.update_function(function_uid, changes=metadata)

        """
        return self._client._functions.update(function_uid, changes)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def update_pipeline(self, pipeline_uid, changes):
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
                 >>> client.repository.PipelineMetanames.NAME:"updated_pipeline"
                 >>> }
                 >>> pipeline_details = client.repository.update_pipeline(pipeline_uid, changes=metadata)

        """

        return self._client.pipelines.update(pipeline_uid, changes)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def update_space(self, space_uid, changes):
        """
                Updates existing space metadata.

                **Parameters**

                .. important::
                    #. **space_uid**:  UID of space which definition should be updated\n
                       **type**: str\n
                    #. **changes**:  elements which should be changed, where keys are ConfigurationMetaNames\n
                       **type**: dict\n

                **Output**

                .. important::
                    **returns**: metadata of updated space\n
                    **return type**: dict\n

                **Example**

                 >>> metadata = {
                 >>> client.repository.SpacesMetaNames.NAME:"updated_space"
                 >>> }
                 >>> space_details = client.repository.update_space(space_uid, changes=metadata)
        """

        return self._client.spaces.update(space_uid, changes)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def load(self, artifact_uid):
        """
           Load model from repository to object in local environment.

           **Parameters**

           .. important::

                #. **artifact_uid**:  UID of model\n
                   **type**: str\n

           **Output**

           .. important::

                **returns**: model object\n
                **return type**: object\n

           **Example**

            >>> model_obj = client.repository.load(model_uid)
        """

        return self._client._models.load(artifact_uid)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def download(self, artifact_uid, filename='downloaded_artifact.tar.gz'):
        """
               Downloads configuration file for artifact with specified uid.

               **Parameters**

               .. important::

                    #. **artifact_uid**:  UID of model, function, runtime or library\n
                       **type**: str\n

                    #. **filename**:  Name of the file to which the artifact content has to be downloaded\n
                       **default value**: downloaded_artifact.tar.gz\n
                       **type**: str\n

               **Output**

               .. important::

                   **returns**: Path to the downloaded artifact content\n
                   **return type**: str\n

               .. note::

                    If filename is not specified, the default filename is "downloaded_artifact.tar.gz".\n

               **Example**

                >>> client.repository.download(model_uid, 'my_model.tar.gz')
        """
        self._validate_type(artifact_uid, 'artifact_uid', STR_TYPE, True)
        self._validate_type(filename, 'filename', STR_TYPE, True)

        res = self._check_artifact_type(artifact_uid)

        if res['model'] is True:
            return self._client._models.download(artifact_uid, filename)
        elif res['function'] is True:
            return self._client._functions.download(artifact_uid, filename)
        elif res['library'] is True:
            return self._client.runtimes.download_library(artifact_uid, filename)
        elif res['runtime'] is True:
            return self._client.runtimes.download_configuration(artifact_uid, filename)
        else:
            raise WMLClientError('Unexpected type of artifact to download: {}'.format(res))

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, artifact_uid):
        """
           Delete model, experiment, pipeline, space, runtime, library or function from repository.

           **Parameters**

           .. important::
                #. **artifact_uid**:  stored model, experiment, function, pipeline, space, library or runtime UID\n
                   **type**: str\n

           **Output**

           .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n

           **Example**

            >>> client.repository.delete(artifact_uid)
        """

        artifact_uid = str_type_conv(artifact_uid)
        Repository._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)

        artifact_type = self._check_artifact_type(artifact_uid)
        self._logger.debug(u'Attempting deletion of artifact with type: \'{}\''.format(str(artifact_type)))


        if artifact_type[u'model'] is True:
            return self._client._models.delete(artifact_uid)
        elif artifact_type[u'experiment'] is True:
            return self._client.experiments.delete(artifact_uid)
        elif artifact_type[u'pipeline'] is True:
            return self._client.pipelines.delete(artifact_uid)
        elif artifact_type[u'function'] is True:
            return self._client._functions.delete(artifact_uid)
        elif artifact_type[u'space'] is True:
            return self._client.spaces.delete(artifact_uid)
        elif artifact_type[u'runtime'] is True:
            return self._client.runtimes.delete(artifact_uid)
        elif artifact_type[u'library'] is True:
            return self._client.runtimes.delete_library(artifact_uid)
        else:
            raise WMLClientError(u'Artifact with artifact_uid: \'{}\' does not exist.'.format(artifact_uid))

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, artifact_uid=None):
        """
           Get metadata of stored artifacts. If UID is not specified returns all models, experiments, functions, pipelines, spaces, libraries and runtimes metadata.

           **Parameters**

           .. important::
                #. **artifact_uid**:  stored model, experiment, function, pipeline, space, library or runtime UID (optional)\n
                   **type**: str\n

           **Output**

           .. important::
                **returns**: stored artifact(s) metadata\n
                **return type**: dict\n
                dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n

           .. note::
                If UID is not specified, all models, experiments, functions, pipelines, spaces, libraries and runtimes metadata is fetched\n

           **Example**

            >>> details = client.repository.get_details(artifact_uid)
            >>> details = client.repository.get_details()
        """

        artifact_uid = str_type_conv(artifact_uid)
        Repository._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, False)


        if artifact_uid is None:
                model_details = self._client._models.get_details()
                experiment_details = self.get_experiment_details()
                pipeline_details = self.get_pipeline_details()
                library_details = self._client.runtimes.get_library_details()
                runtime_details = self._client.runtimes.get_details()
                function_details = self._client._functions.get_details()
                space_details = self._client.spaces.get_details()

                details = {
                    u'models': model_details,
                    u'experiments': experiment_details,
                    u'pipeline': pipeline_details,
                    u'runtimes': runtime_details,
                    u'libraries': library_details,
                    u'spaces': space_details,
                    u'functions': function_details
                }

        else:
                uid_type = self._check_artifact_type(artifact_uid)
                if uid_type[u'model'] is True:
                    details = self._client._models.get_details(artifact_uid)
                elif uid_type[u'experiment'] is True:
                    details = self.get_experiment_details(artifact_uid)
                elif uid_type[u'pipeline'] is True:
                    details = self.get_pipeline_details(artifact_uid)
                elif uid_type[u'function'] is True:
                    details = self._client._functions.get_details(artifact_uid)
                elif uid_type[u'runtime'] is True:
                    details = self._client.runtimes.get_details(artifact_uid)
                elif uid_type[u'library'] is True:
                    details = self._client.runtimes.get_library_details(artifact_uid)
                elif uid_type[u'space'] is True:
                    details = self._client.spaces.get_details(artifact_uid)
                else:
                    raise WMLClientError(u'Getting artifact details failed. Artifact uid: \'{}\' not found.'.format(artifact_uid))

        return details

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_model_details(self, model_uid=None, limit=None):
        """
           Get metadata of stored model. If model UID is not specified returns all models metadata.

           **Parameters**

           .. important::
                #. **model_uid**: Model UID (optional)\n
                   **type**: str\n
                #. **limit**:  limit number of fetched records (optional)\n
                   **type**: int\n

           **Output**

           .. important::
                **returns**: metadata of model(s)\n
                **return type**: dict
                dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n

           .. note::
                If UID is not specified, all models metadata is fetched\n

           **Example**

            >>> model_details = client.repository.get_model_details(model_uid)
            >>> models_details = client.repository.get_model_details()
        """

        return self._client._models.get_details(model_uid, limit)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_experiment_details(self, experiment_uid=None, limit=None):
        """
           Get metadata of experiment. If no experiment UID is specified all experiments metadata is returned.

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

             >>> experiment_details = client.respository.get_experiment_details(experiment_uid)
             >>> experiment_details = client.respository.get_experiment_details()
         """
        experiment_uid = str_type_conv(experiment_uid)
        Repository._validate_type(experiment_uid, u'experiment_uid', STR_TYPE, False)
        Repository._validate_type(limit, u'limit', int, False)

        url = self._href_definitions.get_experiments_href()

        return self._client.experiments.get_details(experiment_uid, limit)


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_function_details(self, function_uid=None, limit=None):
        """

           Get metadata of function. If no function UID is specified all functions metadata is returned.

           **Parameters**

           .. important::
                #. **function_uid**:  UID of function (optional)\n
                   **type**: str\n
                #. **limit**:  limit number of fetched records (optional)\n
                   **type**: int\n

           **Output**

           .. important::
                **returns**: function(s) metadata\n
                **return type**: dict\n
                dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n

           .. note::
                If UID is not specified, all functions metadata is fetched\n

           **Example**

            >>> function_details = client.respository.get_function_details(function_uid)
            >>> function_details = client.respository.get_function_details()
         """
        Repository._validate_type(function_uid, u'function_uid', STR_TYPE, False)
        Repository._validate_type(limit, u'limit', int, False)
        return self._client._functions.get_details(function_uid, limit)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_pipeline_details(self, pipeline_uid=None, limit=None):
        """
           Get metadata of stored pipelines. If pipeline UID is not specified returns all pipelines metadata.

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

            >>> pipeline_details = client.repository.get_pipeline_details(pipeline_uid)
            >>> pipeline_details = client.repository.get_pipeline_details()
        """

        Repository._validate_type(pipeline_uid, u'pipeline_uid', STR_TYPE, False)
        Repository._validate_type(limit, u'limit', int, False)
        return self._client.pipelines.get_details(pipeline_uid, limit)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_space_details(self, space_uid=None, limit=None):
        """
           Get metadata of stored space. If space UID is not specified returns all model spaces metadata.

           **Parameters**

           .. important::
                #. **space_uid**: Space UID (optional)\n
                   **type**: str\n
                #. **limit**:  limit number of fetched records (optional)\n
                   **type**: int\n

           **Output**

           .. important::
                **returns**: metadata of space(s)\n
                **return type**: dict
                dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n

           .. note::
                If UID is not specified, all spaces metadata is fetched\n

           **Example**

            >>> space_details = client.repository.get_space_details(space_uid)
            >>> space_details = client.repository.get_space_details()
        """

        Repository._validate_type(space_uid, u'space_uid', STR_TYPE, False)
        Repository._validate_type(limit, u'limit', int, False)
        return self._client.spaces.get_details(space_uid, limit)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_model_href(model_details):
        """
            Get href of stored model.

           **Parameters**

           .. important::
                #. **model_details**:  Metadata of the stored model\n
                   **type**: dict\n

           **Output**

           .. important::
                **returns**: href of stored model\n
                **return type**: str\n

           **Example**

            >>> model_details = client.repository.get_model_detailsf(model_uid)
            >>> model_uid = client.repository.get_model_href(model_details)
        """

        return Models.get_href(model_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_model_uid(model_details):
        """
            Get UID of stored model.

           **Parameters**

           .. important::
                #. **model_details**:  Metadata of the stored model\n
                   **type**: dict\n

           **Output**

           .. important::
                **returns**: UID of stored model\n
                **return type**: str\n

           **Example**

            >>> model_details = client.repository.get_model_detailsf(model_uid)
            >>> model_uid = client.repository.get_model_uid(model_details)
        """

        return Models.get_uid(model_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_experiment_uid(experiment_details):
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
            >>> experiment_details = client.repository.get_experiment_detailsf(experiment_uid)
            >>> experiment_uid = client.repository.get_experiment_uid(experiment_details)
        """

        return Experiments.get_uid(experiment_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_experiment_href(experiment_details):
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
             >>> experiment_details = client.repository.get_experiment_detailsf(experiment_uid)
             >>> experiment_href = client.repository.get_experiment_href(experiment_details)
        """

        return Experiments.get_href(experiment_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_function_uid(function_details):
        """
            Get UID of stored function.

            **Parameters**

            .. important::
                #. **function_details**:  Metadata of the stored function\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: UID of stored function\n
                **return type**: str\n

            **Example**

             >>> function_details = client.repository.get_function_detailsf(function_uid)
             >>> function_uid = client.repository.get_function_uid(function_details)
        """
        return Functions.get_uid(function_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_pipeline_uid(pipeline_details):
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

             >>> pipeline_details = client.repository.get_pipeline_details(pipeline_uid)
             >>> pipeline_uid = client.repository.get_pipeline_uid(pipeline_details)

        """

        return Pipelines.get_uid(pipeline_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_function_href(function_details):
        """

            Get href of stored function.

            **Parameters**

            .. important::
                #. **function_details**:  Metadata of the stored function\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: href of stored function\n
                **return type**: str\n

            **Example**

             >>> function_details = client.repository.get_function_detailsf(function_uid)
             >>> function_url = client.repository.get_function_href(function_details)
        """
        return Functions.get_href(function_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_pipeline_href(pipeline_details):
        """
            Get pipeline_hef from pipeline details.

            **Parameters**

            .. important::
                #. **pipeline_details**:  Metadata of the stored pipeline\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: pipeline href\n
                **return type**: str

            **Example**

             >>> pipeline_details = client.repository.get_pipeline_details(pipeline_uid)
             >>> pipeline_href = client.repository.get_pipeline_href(pipeline_details)
        """

        return Pipelines.get_href(pipeline_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_space_uid(space_details):
        """
            Get space_uid from space details.

            **Parameters**

            .. important::
                #. **space_details**:  Metadata of the stored space\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: space UID\n
                **return type**: str

            **Example**

             >>> space_details = client.repository.get_space_details(space_uid)
             >>> space_uid = client.repository.get_space_uid(space_details)
        """

        return Spaces.get_uid(space_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_space_href(space_details):
        """
            Get space_href from space details.

            **Parameters**

            .. important::
                #. **space_details**:  Metadata of the stored space\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: space href\n
                **return type**: str

            **Example**

             >>> space_details = client.repository.get_space_details(space_uid)
             >>> space_href = client.repository.get_space_href(space_details)
        """

        return Spaces.get_href(space_details)

    def list(self):
        """
           List stored models, pipelines, runtimes, libraries, functions, spaces and experiments. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all models, pipelines, runtimes, libraries, functions, spaces and experiments in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.repository.list()
        """

        from tabulate import tabulate

        headers = self._client._get_headers()
        params = {u'limit': 1000} # TODO - should be unlimited, if results not sorted

        pool = Pool(processes=4)
        isIcp = self._ICP

        endpoints = {
                u'model': self._href_definitions.get_published_models_href(),
                u'experiment': self._href_definitions.get_experiments_href(),
                u'pipeline': self._href_definitions.get_pipelines_href(),
                u'function': self._href_definitions.get_functions_href(),
                u'runtime': self._href_definitions.get_runtimes_href(),
                u'library': self._href_definitions.get_custom_libraries_href(),
                u'space': self._href_definitions.get_spaces_href(),

            }


        artifact_get = {artifact: pool.apply_async(get_url, (endpoints[artifact], headers, params, isIcp)) for artifact in endpoints}
        resources = {artifact: [] for artifact in endpoints}

        for artifact in endpoints:
            try:
                    response = artifact_get[artifact].get()
                    response_text = self._handle_response(200, u'getting all {}s'.format(artifact), response)
                    resources[artifact] = response_text[u'resources']
            except Exception as e:
                    self._logger.error(e)

        pool.close()


        model_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], m[u'entity'][u'type'], u'model') for m in resources[u'model']]
        experiment_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'],m['metadata']['created_at'], u'-', u'experiment') for m in resources[u'experiment']]
        pipeline_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', u'pipeline')for m in self._client.pipelines.get_details()[u'resources']]
        function_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', m[u'entity'][u'type'] + u' function') for m in resources[u'function']]
        runtime_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', m[u'entity'][u'platform'][u'name'] + u' runtime') for m in resources[u'runtime']]
        library_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', m[u'entity'][u'platform'][u'name'] + u' library') for m in resources[u'library']]
        space_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', u' space') for m in resources[u'space']]


        values = list(set(model_values + experiment_values + pipeline_values + function_values + runtime_values + library_values  + space_values))
        values = sorted(sorted(values, key=lambda x: x[2], reverse=True), key=lambda x: x[4])

        table = tabulate([[u'GUID', u'NAME', u'CREATED', u'FRAMEWORK', u'TYPE']] + values[:_DEFAULT_LIST_LENGTH])
        print(table)
        if len(values) > _DEFAULT_LIST_LENGTH:
             print('Note: Only first {} records were displayed. To display more use more specific list functions.'.format(_DEFAULT_LIST_LENGTH))


    def list_models(self, limit=None):
        """
           List stored models. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all models in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.repository.list_models()
        """

        self._client._models.list(limit=limit)

    def list_experiments(self, limit=None):
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

            >>> client.repository.list_experiments()
        """

        self._client.experiments.list(limit=limit)

    def list_spaces(self, limit=None):
        """
           List stored spaces. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all spaces in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.repository.list_spaces()
        """

        self._client.spaces.list(limit=limit)

    def list_functions(self, limit=None):
        """

            List stored functions. If limit is set to None there will be only first 50 records shown.

            **Parameters**

            .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

            **Output**

            .. important::
                This method only prints the list of all functions in a table format.\n
                **return type**: None\n

            **Example**

             >>> client.respository.list_functions()
        """
        self._client._functions.list(limit=limit)

    def list_pipelines(self, limit=None):
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

            >>> client.repository.list_pipelines()
        """

        self._client.pipelines.list(limit=limit)

    def _check_artifact_type(self, artifact_uid):
        artifact_uid = str_type_conv(artifact_uid)
        Repository._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)

        def _artifact_exists(response):
            return (response is not None) and (u'status_code' in dir(response)) and (response.status_code == 200)

        pool = Pool(processes=4)
        headers = self._client._get_headers()

        isIcp=self._ICP
        endpoints = {
                u'model': self._href_definitions.get_model_last_version_href(artifact_uid),
                u'pipeline': self._href_definitions.get_pipeline_href(artifact_uid),
                u'experiment': self._href_definitions.get_experiment_href(artifact_uid),
                u'function': self._href_definitions.get_function_href(artifact_uid),
                u'runtime': self._href_definitions.get_runtime_href(artifact_uid),
                u'library': self._href_definitions.get_custom_library_href(artifact_uid),
                u'space': self._href_definitions.get_space_href(artifact_uid)
            }

        future = {artifact: pool.apply_async(get_url, (endpoints[artifact], headers, None, isIcp)) for artifact in endpoints}
        response_get = {artifact: None for artifact in endpoints}

        for artifact in endpoints:
                try:
                    response_get[artifact] = future[artifact].get()
                    self._logger.debug(u'Response({})[{}]: {}'.format(endpoints[artifact], response_get[artifact].status_code, response_get[artifact].text))
                except Exception as e:
                    self._logger.debug(u'Error during checking artifact type: ' + str(e))

        pool.close()

        artifact_type = {artifact: _artifact_exists(response_get[artifact]) for artifact in response_get}

        return artifact_type




    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _create_revision(self, artifact_uid, meta_props):
        """
                   Create revision for passed artifact_uid.

                   :param artifact_uid:  stored model, experiment, function or pipelines UID
                   :type artifact_uid: {str_type}

                   :returns:  artifact new revision metadata
                   :rtype: dict

                   A way you might use me is:

                   >>> details = client.repository.create_revision(artifact_uid)

        """
        artifact_uid = str_type_conv(artifact_uid)
        Repository._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)

        uid_type = self._check_artifact_type(artifact_uid)
        if uid_type[u'experiment'] is True:
           return self._client.experiments.create_revision(artifact_uid, meta_props)
        if uid_type[u'pipeline'] is True:
            return self._client.pipelines.create_revision(meta_props, artifact_uid)
        else:
           raise WMLClientError(u'Getting artifact details failed. Artifact uid: \'{}\' not found.'.format(artifact_uid))

        return details


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _get_revision_details(self, artifact_uid):
        """
           Get metadata of stored artifacts revisions.

           :param artifact_uid:  stored model, experiment, function or pipelines UID (optional)
           :type artifact_uid: {str_type}

           :returns: stored artifacts metadata
           :rtype: dict

           A way you might use me is:

           >>> details = client.repository.get_revision_details(artifact_uid)

        """
        artifact_uid = str_type_conv(artifact_uid)
        Repository._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)

        uid_type = self._check_artifact_type(artifact_uid)

        if uid_type[u'experiment'] is True:
            details = self._client.experiments.get_revision_details(artifact_uid)
        if uid_type[u'pipeline'] is True:
            details = self._client.pipelines.get_revisions(artifact_uid)

        else:
           raise WMLClientError(u'Getting artifact details failed. Artifact uid: \'{}\' not found.'.format(artifact_uid))
        return details