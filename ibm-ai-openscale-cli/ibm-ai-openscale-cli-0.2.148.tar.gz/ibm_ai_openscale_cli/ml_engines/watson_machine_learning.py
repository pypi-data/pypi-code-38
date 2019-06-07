# coding=utf-8
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from retry import retry
import time
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict
from watson_machine_learning_client import WatsonMachineLearningAPIClient

logger = FastpathLogger(__name__)

class WatsonMachineLearningEngine:

    def __init__(self, credentials):
        start = time.time()
        self._client = WatsonMachineLearningAPIClient(dict(credentials))
        elapsed = time.time() - start
        logger.log_info('Using Watson Machine Learning Python Client version: {}'.format(self._client.version))
        logger.log_debug('TIMER: Connect to WatsonMachineLearningAPIClient in {:.3f} seconds'.format(elapsed))

    def set_model(self, model):
        self._model_metadata = model.metadata

    def _create_pipeline(self, model_name, pipeline_metadata_file):
        logger.log_info('Creating pipeline for model {} ...'.format(self._model_metadata['model_name']))
        pipeline_metadata = jsonFileToDict(pipeline_metadata_file)
        pipeline_props = {
            self._client.repository.DefinitionMetaNames.AUTHOR_NAME: pipeline_metadata['author']['name'],
            self._client.repository.DefinitionMetaNames.NAME: pipeline_metadata['name'],
            self._client.repository.DefinitionMetaNames.FRAMEWORK_NAME: pipeline_metadata['framework']['name'],
            self._client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: pipeline_metadata['framework']['version'],
            self._client.repository.DefinitionMetaNames.RUNTIME_NAME: pipeline_metadata['framework']['runtimes'][0]['name'],
            self._client.repository.DefinitionMetaNames.RUNTIME_VERSION: pipeline_metadata['framework']['runtimes'][0]['version'],
            self._client.repository.DefinitionMetaNames.DESCRIPTION: pipeline_metadata['description'],
            self._client.repository.DefinitionMetaNames.TRAINING_DATA_REFERENCES: pipeline_metadata['training_data_reference']
        }
        start = time.time()
        self._client.repository.store_definition(self._model_metadata['pipeline_file'], meta_props=pipeline_props)
        elapsed = time.time() - start
        logger.log_debug('TIMER: WML repository.store_definition(pipeline) in {:.3f} seconds'.format(elapsed))
        logger.log_info('Pipeline created successfully')

    def _delete_models(self, model_name):
        models = self._client.repository.get_model_details()
        found_model = False
        for model in models['resources']:
            model_guid = model['metadata']['guid']
            if model_name == model['entity']['name']:
                try:
                    found_model = True
                    logger.log_info('Deleting model {} ...'.format(model_name))
                    self._reliable_delete_model(model_guid)
                    logger.log_info('Model deleted successfully')
                except Exception as e:
                    logger.log_warning('Error deleting WML deployment "{}": {}'.format(model_guid, str(e)))
        if not found_model:
            logger.log_info('No existing model found with name: {}'.format(model_name))

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_delete_model(self, model_guid):
        start = time.time()
        self._client.repository.delete(model_guid)
        elapsed = time.time() - start
        logger.log_debug('TIMER: WML repository.delete(model) in {:.3f} seconds'.format(elapsed))

    def _create_model(self, model_name, model_metadata_file):
        logger.log_info('Creating new model {} ...'.format(model_name))
        metadata = jsonFileToDict(model_metadata_file)
        model_props = {
            self._client.repository.ModelMetaNames.NAME: model_name,
            self._client.repository.ModelMetaNames.FRAMEWORK_NAME: metadata['framework']['name'],
            self._client.repository.ModelMetaNames.FRAMEWORK_VERSION: metadata['framework']['version'],
            self._client.repository.ModelMetaNames.RUNTIME_NAME: metadata['framework']['runtimes'][0]['name'],
            self._client.repository.ModelMetaNames.RUNTIME_VERSION: metadata['framework']['runtimes'][0]['version'],
            self._client.repository.ModelMetaNames.LABEL_FIELD: metadata['label_column'],
            self._client.repository.ModelMetaNames.TRAINING_DATA_SCHEMA: metadata['training_data_schema'],
            self._client.repository.ModelMetaNames.INPUT_DATA_SCHEMA: metadata['input_data_schema']
        }
        if 'evaluation' in metadata:
            model_props[self._client.repository.ModelMetaNames.EVALUATION_METHOD] = metadata['evaluation']['method']
            model_props[self._client.repository.ModelMetaNames.EVALUATION_METRICS] = metadata['evaluation']['metrics']
        if 'output_data_schema' in metadata:
            model_props[self._client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA] = metadata['output_data_schema']
        if 'training_data_reference' in metadata:
            model_props[self._client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE] = metadata['training_data_reference'][0]
        model_details = self._reliable_create_model(self._model_metadata['model_file'], model_props)
        model_guid = self._client.repository.get_model_uid(model_details)
        logger.log_info('Created new model {} successfully (guid: {})'.format(model_name, model_guid))
        return (metadata, model_guid)

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_create_model(self, model_file, model_props):
        start = time.time()
        model_details = self._client.repository.store_model(model_file, model_props)
        elapsed = time.time() - start
        logger.log_debug('TIMER: WML repository.store_model in {:.3f} seconds'.format(elapsed))
        return model_details

    def _list_all_models(self):
        logger.log_info('Listing all models ...')
        start = time.time()
        self._client.repository.list_models()
        elapsed = time.time() - start
        logger.log_debug('TIMER: WML repository.list_models in {:.3f} seconds'.format(elapsed))
        logger.log_info('Models listed successfully')

    def _deploy_model(self, model_guid, deployment_name, deployment_description):
        logger.log_info('Creating new deployment {} ...'.format(deployment_name))
        deployment_details = self._reliable_deploy_model(model_guid, deployment_name, deployment_description)
        deployment_guid = deployment_details['metadata']['guid']
        logger.log_info('Created new deployment {} successfully (guid: {})'.format(deployment_name, deployment_guid))
        return deployment_guid

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_deploy_model(self, model_guid, deployment_name, deployment_description):
        start = time.time()
        deployment_details = self._client.deployments.create(artifact_uid=model_guid, name=deployment_name, description=deployment_description)
        elapsed = time.time() - start
        logger.log_debug('TIMER: WML deployments.create in {:.3f} seconds'.format(elapsed))
        return deployment_details

    def _delete_deployments(self, deployment_name):
        deployment_details = self._client.deployments.get_details()
        found_deployment = False
        for details in deployment_details['resources']:
            deployment_guid = details['metadata']['guid']
            if deployment_name == details['entity']['name']:
                try:
                    found_deployment = True
                    logger.log_info('Deleting deployment {} ...'.format(deployment_name))
                    self._reliable_delete_deployment(deployment_guid)
                    logger.log_info('Deployment deleted successfully'.format(deployment_name))
                except Exception as e:
                    logger.log_warning('Error deleting WML deployment "{}": {}.'.format(deployment_guid, str(e)))
        if not found_deployment:
            logger.log_info('No existing deployment found with name: {}'.format(deployment_name))

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_delete_deployment(self, deployment_guid):
        start = time.time()
        self._client.deployments.delete(deployment_guid)
        elapsed = time.time() - start
        logger.log_debug('TIMER: WML deployments.delete in {:.3f} seconds'.format(elapsed))

    def _list_all_deployments(self):
        start = time.time()
        deployment_details = self._client.deployments.get_details()
        elapsed = time.time() - start
        logger.log_debug('TIMER: WML deployments.get_details in {:.3f} seconds'.format(elapsed))
        for details in deployment_details['resources']:
            logger.log_info('Name: {}, GUID: {}'.format(details['entity']['name'], details['metadata']['guid']))

    def create_model_and_deploy(self):
        model_name = self._model_metadata['model_name']
        deployment_name = self._model_metadata['deployment_name']

        # delete existing deployment
        logger.log_info('Checking for deployments with the name {}'.format(deployment_name))
        self._delete_deployments(deployment_name)

        # delete existing model
        logger.log_info('Checking for models with the name {}'.format(model_name))
        self._delete_models(model_name)

        # create new model and deployment
        # self._create_pipeline(model_name, self._model_metadata['pipeline_metadata_file'])
        model_metadata_dict, model_guid = self._create_model(model_name, self._model_metadata['model_metadata_file'])
        deployment_guid = self._deploy_model(model_guid, deployment_name, self._model_metadata['deployment_description'])

        model_deployment_dict = {}
        model_deployment_dict['model_name'] = model_name
        model_deployment_dict['source_uid'] = model_guid
        model_deployment_dict['model_metadata_dict'] = model_metadata_dict
        model_deployment_dict['deployment_name'] = deployment_name
        model_deployment_dict['source_entry_metadata_guid'] = deployment_guid
        model_deployment_dict['binding_uid'] = self._client.service_instance.get_instance_id()

        return model_deployment_dict

    def model_cleanup(self):
        deployment_name = self._model_metadata['deployment_name']
        self._delete_deployments(deployment_name)
        model_name = self._model_metadata['model_name']
        self._delete_models(model_name)

    # returns info for first-found deployment with the specified name, if there are multiple
    def get_existing_deployment(self, deployment_name):
        model_name = self._model_metadata['model_name']
        model_guid = None
        deployment_guid = None
        model_metadata_dict = None
        logger.log_info('Use existing model named: {}'.format(model_name))
        models = self._client.repository.get_model_details()
        for this_model in models['resources']:
            this_model_name = this_model['entity']['name']
            guid = this_model['metadata']['guid']
            metaData = this_model['metadata']
            if model_name == this_model_name:
                model_guid = guid
                model_metadata_dict = metaData
                break
        deploymentDetails = self._client.deployments.get_details()
        for details in deploymentDetails['resources']:
            dep_guid = details['metadata']['guid']
            dep_name = details['entity']['name']
            if dep_name == deployment_name:
                deployment_guid = dep_guid
                break

        logger.log_info('Model Name: {}  Model GUID: {}'.format(model_name, model_guid))
        logger.log_info('Deployment Name: {}  Deployment GUID: {}'.format(deployment_name, deployment_guid))

        model_deployment_dict = {}
        model_deployment_dict['model_metadata_dict'] = model_metadata_dict
        model_deployment_dict['source_uid'] = model_guid
        model_deployment_dict['source_entry_metadata_guid'] = deployment_guid
        model_deployment_dict['binding_uid'] = self._client.service_instance.get_instance_id()

        return model_deployment_dict
