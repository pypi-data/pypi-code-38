# coding=utf-8
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
import os
import requests
import time
from retry import retry
import random
from ibm_ai_openscale_cli.enums import MLEngineType
from ibm_ai_openscale import WatsonMachineLearningInstance4ICP
from ibm_ai_openscale.engines import AzureMachineLearningInstance, AzureMachineLearningAsset
from ibm_ai_openscale.engines import CustomMachineLearningInstance, CustomMachineLearningAsset
from ibm_ai_openscale.engines import SageMakerMachineLearningInstance, SageMakerMachineLearningAsset
from ibm_ai_openscale.engines import SPSSMachineLearningInstance, SPSSMachineLearningAsset
from ibm_ai_openscale.engines import WatsonMachineLearningInstance, WatsonMachineLearningAsset
from ibm_ai_openscale.supporting_classes import Feature, InputDataType, ProblemType, FeedbackFormat
from ibm_ai_openscale_cli.api_environment import ApiEnvironment
from ibm_ai_openscale_cli.openscale.openscale_reset import OpenScaleReset
from ibm_ai_openscale_cli.utility_classes.utils import get_iam_headers

logger = FastpathLogger(__name__)
parent_dir = os.path.dirname(__file__)

WML_NGINX_HOST = 'wmlproxyservice.zen'
AIOS_NGINX_HOST = ApiEnvironment().icp_gateway_url.replace('http://', '')

class OpenScaleClient(OpenScaleReset):

    def __init__(self, args, credentials, database_credentials):
        super().__init__(args, credentials, database_credentials)
        self._binding_id = None

    def set_model(self, model):
        self._model = model
        self._subscription = None
        self._asset_details_dict = None
        self._fairness_run_once = True
        self._explainability_run_once = True

    def get_deployment_id(self):
        return self._asset_details_dict['source_entry_metadata_guid']

    def get_binding_id(self):
        return self._binding_id

    def get_subscription_id(self):
        return self._subscription.uid

    def get_datamart_details(self):
        return self._client.data_mart.get_details()

    @retry(tries=5, delay=8, backoff=2)
    def create_datamart(self):
        '''
        Create datamart schema and datamart
        '''
        logger.log_info('Creating datamart {} ...'.format(self._datamart_name))

        if self._database is None:
            logger.log_info('PostgreSQL instance: internal')
            start = time.time()
            self._client.data_mart.setup(internal_db=True)
            elapsed = time.time() - start
        else:
            self._database.create_new_schema(self._datamart_name, self._keep_schema)
            start = time.time()
            self._client.data_mart.setup(db_credentials=self._database_credentials, schema=self._datamart_name)
            elapsed = time.time() - start
        logger.log_info('Datamart {} created successfully'.format(self._datamart_name))
        logger.log_debug('TIMER: data_mart.setup in {:.3f} seconds'.format(elapsed))

    @retry(tries=5, delay=4, backoff=2)
    def bind_mlinstance(self, credentials):
        '''
        Bind ML instance
        '''
        logger.log_info('Binding {} instance to {} ...'.format(self._args.ml_engine_type.name.lower(), self._args.service_name))
        binding_name = None
        if self._args.ml_engine_type is MLEngineType.WML:
            if self._args.is_icp:
                ml_instance = WatsonMachineLearningInstance4ICP()
            else:
                ml_instance = WatsonMachineLearningInstance(credentials)
        elif self._args.ml_engine_type is MLEngineType.AZUREML:
            ml_instance = AzureMachineLearningInstance(credentials)
        elif self._args.ml_engine_type is MLEngineType.SPSS:
            ml_instance = SPSSMachineLearningInstance(credentials)
        elif self._args.ml_engine_type is MLEngineType.CUSTOM:
            ml_instance = CustomMachineLearningInstance(credentials)
        elif self._args.ml_engine_type is MLEngineType.SAGEMAKER:
            ml_instance = SageMakerMachineLearningInstance(credentials)
        binding_name = '{}{}Instance'.format(self._args.ml_engine_type.name, 'ICP' if self._args.is_icp else ' ')
        start = time.time()
        self._binding_id = self._client.data_mart.bindings.add(binding_name, ml_instance)
        elapsed = time.time() - start
        logger.log_info('Binding completed successfully')
        logger.log_debug('TIMER: data_mart.bindings.add in {:.3f} seconds'.format(elapsed))

    def use_existing_binding(self, asset_details_dict):
        if self._args.is_icp:
            self._binding_id = '999'
        else:
            self._binding_id = asset_details_dict['binding_uid']

    @retry(tries=5, delay=4, backoff=2)
    def use_existing_subscription(self, asset_details_dict):
        self._asset_details_dict = asset_details_dict
        asset_uid = asset_details_dict['source_uid']
        deployment_uid = asset_details_dict['source_entry_metadata_guid']
        logger.log_info('Get existing subscription for model {} deployment {}...'.format(asset_uid, deployment_uid))
        start = time.time()
        all_subscriptions = self._client.data_mart.subscriptions.get_details()['subscriptions']
        elapsed = time.time() - start
        logger.log_debug('TIMER: data_mart.subscriptions.get_details(ALL) in {:.3f} seconds'.format(elapsed))
        subscription_id = None
        for sub in all_subscriptions:
            if 'entity' in sub and 'asset' in sub['entity'] and 'asset_id' in sub['entity']['asset']:
                if sub['entity']['asset']['asset_id'] == asset_uid and 'deployments' in sub['entity']:
                    for dep in sub['entity']['deployments']:
                        if 'deployment_id' in dep and dep['deployment_id'] == deployment_uid:
                            if 'metadata' in sub and 'guid' in sub['metadata']:
                                subscription_id = sub['metadata']['guid']
        if not subscription_id:
            error_msg = 'ERROR: Could not find an existing subscription for model {} deployment {}'.format(asset_uid, deployment_uid)
            logger.log_error(error_msg)
            raise Exception(error_msg)
        start = time.time()
        self._subscription = self._client.data_mart.subscriptions.get(subscription_uid=subscription_id)
        elapsed = time.time() - start
        logger.log_info('Subscription {} found successfully'.format(self.get_subscription_id()))
        logger.log_debug('TIMER: data_mart.subscriptions.get(ONE) in {:.3f} seconds'.format(elapsed))

    @retry(tries=5, delay=4, backoff=2)
    def subscribe_to_model_deployment(self, asset_details_dict):
        '''
        Create subscription for the given model
        '''
        logger.log_info('Subscribing ML deployment to {} ...'.format(self._args.service_name))
        asset_metadata = self._model.configuration_data['asset_metadata']
        asset_params = {
            'source_uid' : asset_details_dict['source_uid'],
            'binding_uid' : self._binding_id
        }
        if 'problem_type' in asset_metadata:
            asset_params['problem_type'] = self._get_problem_type_object(asset_metadata['problem_type'])
        if 'input_data_type' in asset_metadata:
            asset_params['input_data_type'] = self._get_input_data_type_object(asset_metadata['input_data_type'])
        if self._model.training_data_reference:
            asset_params['training_data_reference'] = self._model.training_data_reference['cos_storage_reference']
        if 'label_column' in asset_metadata:
            asset_params['label_column'] = asset_metadata['label_column']
        if 'prediction_column' in asset_metadata:
            asset_params['prediction_column'] = asset_metadata['prediction_column']
        if 'class_probability_columns' in asset_metadata:
            asset_params['class_probability_columns'] = asset_metadata['class_probability_columns']
        if 'probability_column' in asset_metadata:
            asset_params['probability_column'] = asset_metadata['probability_column']
        if 'feature_columns' in asset_metadata:
            asset_params['feature_columns'] = asset_metadata['feature_columns']
        if 'categorical_columns' in asset_metadata:
            asset_params['categorical_columns'] = asset_metadata['categorical_columns']
        ml_asset = None
        if self._args.ml_engine_type is MLEngineType.WML:
            ml_asset = WatsonMachineLearningAsset( **asset_params )
        elif self._args.ml_engine_type is MLEngineType.AZUREML:
            ml_asset = AzureMachineLearningAsset( **asset_params )
        elif self._args.ml_engine_type is MLEngineType.SPSS:
            ml_asset = SPSSMachineLearningAsset( **asset_params )
        elif self._args.ml_engine_type is MLEngineType.CUSTOM:
            ml_asset = CustomMachineLearningAsset( **asset_params )
        elif self._args.ml_engine_type is MLEngineType.SAGEMAKER:
            ml_asset = SageMakerMachineLearningAsset( **asset_params )
        deployment_uid = asset_details_dict['source_entry_metadata_guid']
        start = time.time()
        self._subscription = self._client.data_mart.subscriptions.add(ml_asset, deployment_uids=[deployment_uid])
        elapsed = time.time() - start
        self._asset_details_dict = asset_details_dict
        logger.log_info('Subscription completed successfully (guid: {})'.format(self.get_subscription_id()))
        logger.log_debug('TIMER: data_mart.subscriptions.add in {:.3f} seconds'.format(elapsed))

    def _get_input_data_type_object(self, data):
        if data == 'STRUCTURED':
            return InputDataType.STRUCTURED
        return None

    def _get_problem_type_object(self, data):
        if data == 'BINARY_CLASSIFICATION':
            return ProblemType.BINARY_CLASSIFICATION
        elif data == 'MULTICLASS_CLASSIFICATION':
            return ProblemType.MULTICLASS_CLASSIFICATION
        elif data == 'REGRESSION':
            return ProblemType.REGRESSION
        return None

    # not actually called, because payload logging and performance monitoring are both already enabled by default
    @retry(tries=5, delay=8, backoff=2)
    def configure_subscription(self):
        '''
        Configure payload logging and performance monitoring
        '''
        logger.log_info('Enablng payload logging ...')
        start = time.time()
        self._subscription.payload_logging.enable()
        elapsed = time.time() - start
        logger.log_debug('TIMER: subscription.payload_logging.enable in {:.3f} seconds'.format(elapsed))
        logger.log_info('Payload logging enabled successfully')

        logger.log_info('Enabling performance monitoring ...')
        start = time.time()
        self._subscription.performance_monitoring.enable()
        elapsed = time.time() - start
        logger.log_debug('TIMER: subscription.performance_monitoring.enable in {:.3f} seconds'.format(elapsed))
        logger.log_info('Performance monitoring enabled successfully')

    def configure_subscription_monitors(self):
        def _get_config_params(param_key_name):
            param_name = param_key_name.split('_')[0]
            params = None
            if param_key_name in self._model.configuration_data:
                params = self._model.configuration_data[param_key_name]
                logger.log_info('Configuring {} ...'.format(param_name))
            else:
                logger.log_info('Configuration for {} not provided for this model - skipping'.format(param_name))
            return params
        self.configure_explainability()
        self.configure_fairness(_get_config_params('fairness_configuration'))
        self.configure_quality(_get_config_params('quality_configuration'))

    @retry(tries=5, delay=8, backoff=2)
    def configure_fairness(self, params):
        if params:
            if self._fairness_run_once: # in case of retry
                feature_list = []
                for elem in params['features']:
                    feature_list.append(Feature(elem['feature'], elem['majority'], elem['minority'], float(elem['threshold'])))
                params['features'] = feature_list
                if not self._model.training_data_reference:
                    if self._model.training_data_statistics:
                        params['training_data_statistics'] = self._model.training_data_statistics
                    else:
                        params['training_data'] = self._model.training_data
                params['deployment_uid'] = self._asset_details_dict['source_entry_metadata_guid']
                self._fairness_run_once = False
            start = time.time()
            self._subscription.fairness_monitoring.enable(**params)
            elapsed = time.time() - start
            logger.log_debug('TIMER: subscription.fairness_monitoring.enable in {:.3f} seconds'.format(elapsed))
            logger.log_info('Fairness configured successfully')

    @retry(tries=5, delay=8, backoff=2)
    def configure_quality(self, params):
        if params:
            start = time.time()
            self._subscription.quality_monitoring.enable(**params)
            elapsed = time.time() - start
            logger.log_debug('TIMER: subscription.quality_monitoring.enable in {:.3f} seconds'.format(elapsed))
            logger.log_info('Quality configured successfully')

    @retry(tries=5, delay=8, backoff=2)
    def add_feedback_data(self):
        if not self._model.feedback_data:
            logger.log_info('Feedback data not provided for this model - skipping')
            return
        logger.log_info('Adding feedback data ...')
        start = time.time()
        self._subscription.feedback_logging.store(self._model.feedback_data, feedback_format=FeedbackFormat.DICT)
        elapsed = time.time() - start
        logger.log_debug('TIMER: subscription.feedback_logging.store in {:.3f} seconds'.format(elapsed))
        logger.log_info('Feedback data added successfully')

    @retry(tries=5, delay=8, backoff=2)
    def configure_explainability(self):
        if 'class_probability_columns' not in self._model.configuration_data['asset_metadata'] and 'probability_column' not in self._model.configuration_data['asset_metadata']:
            logger.log_info('Explainability not available for this model')
            return
        logger.log_info('Configuring explainability ...')
        params = {}
        if self._explainability_run_once: # in case of retry
            if not self._model.training_data_reference:
                if self._model.training_data_statistics:
                    params['training_data_statistics'] = self._model.training_data_statistics
                else:
                    params['training_data'] = self._model.training_data
            self._explainability_run_once = False
        start = time.time()
        self._subscription.explainability.enable(**params)
        elapsed = time.time() - start
        logger.log_debug('TIMER: subscription.explainability.enable in {:.3f} seconds'.format(elapsed))
        logger.log_info('Explainability configured successfully')

    def generate_sample_metrics(self):
        if self._args.history < 1:
            return

        self.add_feedback_data()

        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_payload_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical payload records provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical payload records to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self.reliable_post_payloads(records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical payload records loaded successfully')

        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_performance_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical performance metrics provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical performance metrics to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self.reliable_post_metrics('performance', records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical performance metrics loaded successfully')

        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_fairness_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical fairness metrics provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical fairness metrics to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self.reliable_post_metrics('fairness', records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical fairness metrics loaded successfully')

        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_debias_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical debiased fairness metrics provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical debiased fairness metrics to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self.reliable_post_metrics('debiased_fairness', records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical debiased fairness metrics loaded successfully')

        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_manual_labeling_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical manual labeling data provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical manual labeling data to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self.reliable_post_manual_labeling(records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical manual labeling data loaded successfully')

        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_quality_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical quality metrics provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical quality metrics to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self.reliable_post_metrics('quality', records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical quality metrics loaded successfully')

        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_quality_monitor_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical quality monitor metrics provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical quality monitor metrics to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self.reliable_store_quality_monitor_metrics(records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical quality monitor metrics loaded successfully')

    @retry(tries=5, delay=4, backoff=2)
    def reliable_single_score(self, engine_client, deployment_url, score_input, score_num, totalelapsed, firststart, lastend):
        start = time.time()
        record = engine_client.deployments.score(deployment_url, score_input)
        end = time.time()
        elapsed = end - start
        totalelapsed += elapsed
        lastend = end
        duration = lastend - firststart
        timer_message = 'TIMER: WML deployments.score in {:.3f} seconds, total requests: {}, duration: {:.3f} seconds, elapsed: {:.3f} seconds'
        logger.log_debug(timer_message.format(elapsed, score_num+1, duration, totalelapsed))
        return (totalelapsed, duration, lastend, record)

    @retry(tries=5, delay=4, backoff=2)
    def generate_sample_scoring(self, engine_client, numscores, values_per_score, to_init_payload_logging=False):
        if numscores < 1:
            return
        if to_init_payload_logging:
            logger.log_info('Initialize payload logging by sending one sample scoring request')
        logger.log_info('Generating {} model scoring request(s) ...'.format(numscores))
        if values_per_score > 1:
            logger.log_info('{} values included in each scoring request'.format(values_per_score))
        records_list = []
        if self._args.ml_engine_type is MLEngineType.WML:
            engine_client = self._client.data_mart.bindings.get_native_engine_client(binding_uid=self._binding_id)
            deployment_details = engine_client.deployments.get_details(self._asset_details_dict['source_entry_metadata_guid'])
            deployment_url = engine_client.deployments.get_scoring_url(deployment_details)
            if self._args.is_icp:
                if WML_NGINX_HOST in deployment_url:
                    deployment_url = deployment_url.replace(':31002', ':443')
                    deployment_url = deployment_url.replace(':32006', ':443')
                elif AIOS_NGINX_HOST in deployment_url:
                    deployment_url = deployment_url.replace('https://', 'http://')
                    deployment_url = deployment_url.replace(':31002', ':80')
                    deployment_url = deployment_url.replace(':32006', ':80')
            pause = self._args.pause_between_scores
            if pause > 0.0:
                logger.log_info('{:.3f} second pause between each scoring request'.format(pause))
            totalelapsed = 0.0
            firststart = time.time()
            lastend = firststart
            for score_num in range(numscores):
                if pause > 0.0 and score_num > 0:
                    time.sleep(pause)
                fields, values = self._model.get_score_input(values_per_score)
                score_input = {'fields': fields, 'values': values }
                (totalelapsed, duration, lastend, record) = self.reliable_single_score(engine_client, deployment_url, score_input, score_num, totalelapsed, firststart, lastend)
            logger.log_debug('TIMER: Total score requests: {}, total scores: {}, duration: {:.3f} seconds'.format(numscores, numscores*values_per_score, duration))
            logger.log_debug('TIMER: Throughput: {:.3f} score requests per second, {:.3f} scores per second, average score request time: {:.3f} seconds'.format(numscores/duration, numscores*values_per_score/duration, totalelapsed/numscores))

        elif self._args.ml_engine_type is MLEngineType.AZUREML:
            engine_client.setup_scoring_metadata(self._subscription)
            for _ in range(numscores):
                fields, values = self._model.get_score_input(1)
                values = values[0]
                value_dict = {}
                for (index, field) in enumerate(fields):
                    value_dict[field] = values[index]
                start = time.time()
                record = engine_client.score({'Inputs':{'input1': [value_dict] },'GlobalParameters':{}})
                elapsed = time.time() - start
                logger.log_debug('TIMER: AzureML score in {:.3f} seconds'.format(elapsed))
                records_list.append(record)
        elif self._args.ml_engine_type is MLEngineType.SPSS:
            engine_client.setup_scoring_metadata(self._subscription)
            subscription_details = self._subscription.get_details()
            model_name_id = subscription_details['entity']['asset']['name']
            input_table_id = subscription_details['entity']['asset_properties']['input_data_schema']['id']
            for _ in range(numscores):
                spss_data = {'requestInputTable':[{'id': input_table_id, 'requestInputRow':[{'input':[]}]}],'id':model_name_id}
                fields, values = self._model.get_score_input(1)
                values = values[0]
                value_dict = {}
                for (index, field) in enumerate(fields):
                    entry_dict = {'name':str(field),'value':str(values[index])}
                    spss_data['requestInputTable'][0]['requestInputRow'][0]['input'].append(entry_dict)
                start = time.time()
                record = engine_client.score(spss_data)
                elapsed = time.time() - start
                logger.log_debug('TIMER: SPSS score in {:.3f} seconds'.format(elapsed))
                records_list.append(record)
        elif self._args.ml_engine_type is MLEngineType.CUSTOM:
            engine_client.setup_scoring_metadata(self._subscription)
            for _ in range(numscores):
                fields, values = self._model.get_score_input(1)
                score_input = {'fields': fields, 'values': values }
                start = time.time()
                record = engine_client.score(score_input)
                elapsed = time.time() - start
                logger.log_debug('TIMER: Custom score in {:.3f} seconds'.format(elapsed))
                records_list.append(record)
        elif self._args.ml_engine_type is MLEngineType.SAGEMAKER:
            records_list = []
            engine_client.setup_scoring_metadata(self._subscription)
            for _ in range(numscores):
                fields, values = self._model.get_score_input(1)
                values = values[0]
                start = time.time()
                record = engine_client.score(fields, values)
                elapsed = time.time() - start
                logger.log_debug('TIMER: Sagemaker score in {:.3f} seconds'.format(elapsed))
                records_list.append(record)
        if records_list:
            start = time.time()
            self._subscription.payload_logging.store(records=records_list)
            elapsed = time.time() - start
            logger.log_debug('TIMER: subscription.payload_logging.store in {:.3f} seconds'.format(elapsed))
        logger.log_debug('DEBUG: Pause 5 seconds to allow payload logging to complete')
        time.sleep(5.0)
        logger.log_info('Scoring request(s) generated successfully')

    def trigger_monitors(self):
        if self._args.no_checks:
            logger.log_info('Skip fairness and quality checks')
            return

        background_mode = not self._args.sync_checks
        if 'fairness_configuration' not in self._model.configuration_data:
            logger.log_info('Skip fairness check since fairness not configured for model')
        else:
            deployment_uid = self._asset_details_dict['source_entry_metadata_guid']
            logger.log_info('Triggering immediate fairness check ...')
            start = time.time()
            self._subscription.fairness_monitoring.run(deployment_uid, background_mode=background_mode)
            elapsed = time.time() - start
            logger.log_debug('TIMER: subscription.fairness_monitoring.run in {:.3f} seconds'.format(elapsed))
            logger.log_info('Fairness check triggered successfully')

        if 'quality_configuration' not in self._model.configuration_data:
            logger.log_info('Skip quality check since quality monitoring not configured for model')
        elif not self._model.feedback_data or self._args.history < 1:
            logger.log_info('Skip quality check for model since there is no feedback data yet')
        else:
            logger.log_info('Triggering immediate quality check ...')
            start = time.time()
            self._subscription.quality_monitoring.run(background_mode=background_mode)
            elapsed = time.time() - start
            logger.log_debug('TIMER: subscription.quality_monitoring.run in {:.3f} seconds'.format(elapsed))
            logger.log_info('Quality check triggered successfully')

    @retry(tries=5, delay=4, backoff=2)
    def reliable_post_payloads(self, records):
        '''
        Retry the loading payloads so that if a specific day fails, just retry that day, rather than retry the whole sequence
        '''
        if not records:
            logger.log_debug('No payload history provided to load - skipping')
            return
        start = time.time()
        self._subscription.payload_logging.store(records=records, deployment_id=self._asset_details_dict['source_entry_metadata_guid'])
        elapsed = time.time() - start
        logger.log_debug('TIMER: subscription.payload_logging.store in {:.3f} seconds'.format(elapsed))

    @retry(tries=5, delay=4, backoff=2)
    def reliable_post_metrics(self, metric_type, records):
        '''
        Retry the loading metrics so that if a specific day fails, just retry that day, rather than retry the whole sequence
        '''
        if not records:
            logger.log_debug('No {} history provided to load - skipping'.format(metric_type))
            return
        metrics_url = '{0}/v1/data_marts/{1}/metrics'.format(self._credentials['url'], self._credentials['data_mart_id'])
        token = self._args.iam_token if self._args.iam_token else None
        iam_headers = get_iam_headers(self._credentials, self._args.env_dict, token)
        deployment_guid = None
        model_guid = None
        model_guid = self._asset_details_dict['source_uid']
        deployment_guid = self._asset_details_dict['source_entry_metadata_guid']
        record_json = []
        for record in records:
            # update historical manual labeling table reference to be correct
            if metric_type in ['fairness', 'debiased_fairness']:
                if 'manual_labelling_store' in record:
                    record['manual_labelling_store'] = 'Manual_Labeling_' + self._get_subscription_id()
            # new-style quality metrics have a slightly different json input than other metrics
            if metric_type == 'quality monitor':
                metric_label = 'monitor_definition_id'
                metric_type_value = 'quality'
            else:
                metric_label = 'metric_type'
                metric_type_value = metric_type
            record_json.append( {
                'binding_id': self._binding_id,
                metric_label: metric_type_value,
                'timestamp': record['timestamp'],
                'subscription_id': self.get_subscription_id(),
                'value': record['value'],
                'deployment_id': deployment_guid
            })
        start = time.time()
        response = requests.post(metrics_url, json=record_json, headers=iam_headers, verify=self._verify)
        elapsed = time.time() - start
        logger.log_debug('TIMER: post data_mart {} metrics in {:.3f} seconds'.format(metric_type, elapsed))
        words = ['error', 'exception']
        if any(word in str(response.json()) for word in words):
            logger.log_warning('WARNING: while posting {} metrics: {}'.format(metric_type, str(response.json())))

    @retry(tries=5, delay=4, backoff=2)
    def reliable_post_manual_labeling(self, records):
        '''
        Retry the loading so that if a specific day fails, just retry that day, rather than retry the whole sequence
        '''
        if not records:
            logger.log_debug('No manual labeling history provided to load - skipping')
            return
        manual_labeling_url = '{0}/v1/data_marts/{1}/manual_labelings'.format(self._credentials['url'], self._credentials['data_mart_id'])
        token = self._args.iam_token if self._args.iam_token else None
        iam_headers = get_iam_headers(self._credentials, self._args.env_dict, token)

        binding_id = self._binding_id
        model_guid = self._asset_details_dict['source_uid']
        deployment_guid = self._asset_details_dict['source_entry_metadata_guid']

        record_json = []
        for record in records:
            # update the record to include required metadata
            record['binding_id'] = binding_id
            record['subscription_id'] = self.get_subscription_id()
            if 'asset_revision' in record: # if asset_revision is present, remove it
                del record['asset_revision']
            record['deployment_id'] = deployment_guid
            record_json.append(record)
        start = time.time()
        response = requests.post(manual_labeling_url, json=record_json, headers=iam_headers, verify=self._verify)
        elapsed = time.time() - start
        logger.log_debug('TIMER: post data_mart manual_labeling history in {:.3f} seconds'.format(elapsed))
        words = ['error', 'exception']
        if any(word in str(response.json()) for word in words):
            logger.log_warning('WARNING: while posting manual labeling history: {}'.format(str(response.json())))

    @retry(tries=5, delay=4, backoff=2)
    def reliable_store_quality_monitor_metrics(self, records):
        '''
        Retry the loading metrics so that if a specific day fails, just retry that day, rather than retry the whole sequence
        '''
        if not records:
            logger.log_debug('No quality_monitor history provided to load - skipping')
            return
        start = time.time()
        self._subscription.monitoring.store_measurements(monitor_uid='quality', measurements=records)
        elapsed = time.time() - start
        logger.log_debug('TIMER: post data_mart quality_monitor metrics in {:.3f} seconds'.format(elapsed))

    def get_asset_details(self, name):
        logger.log_info('Retrieving assets ...')
        asset_details = self._client.data_mart.bindings.get_asset_details()
        asset_details_dict = {}
        for detail in asset_details:
            if name == detail['source_entry']['entity']['name']:
                if self._args.ml_engine_type is MLEngineType.SPSS:
                    asset_details_dict['id'] = detail['name']
                asset_details_dict['binding_uid'] = detail['binding_uid']
                asset_details_dict['source_uid'] = detail['source_uid']
                if self._args.ml_engine_type is not MLEngineType.WML: # For WML, the scoring URL is not in the asset
                    asset_details_dict['scoring_url'] = detail['source_entry']['entity']['scoring_endpoint']['url']
                asset_details_dict['source_entry_metadata_guid'] = detail['source_entry']['metadata']['guid']
                break
        if not 'source_uid' in asset_details_dict:
            error_msg = 'ERROR: Could not find a deployment with the name: {}'.format(name)
            logger.log_error(error_msg)
            raise Exception(error_msg)
        return asset_details_dict

    @retry(tries=5, delay=1, backoff=2)
    def _generate_one_explain(self, scoring_id):
        background_mode = not self._args.sync_explains
        cem = not self._args.explain_no_cem
        start = time.time()
        explain = self._subscription.explainability.run(scoring_id, background_mode=background_mode, cem=cem)
        end = time.time()
        return (start, end, explain)

    @retry(tries=5, delay=4, backoff=2)
    def _get_available_scores(self):
        max_explain_candidates = self._args.max_explain_candidates
        start = time.time()
        payload_table = self._subscription.payload_logging.get_table_content(format='pandas', limit=max_explain_candidates)
        end = time.time()
        scoring_ids = []
        for index, row in payload_table.iterrows():
            scoring_ids.append(row['scoring_id'])
        random.shuffle(scoring_ids)
        return (start, end, scoring_ids)

    def generate_explain_requests(self):
        num_explains = self._args.num_explains
        max_explain_candidates = self._args.max_explain_candidates
        if num_explains < 1 or max_explain_candidates < 1:
            return
        pause = self._args.pause_between_explains
        logger.log_info('Finding up to {} available scores to explain...'.format(max_explain_candidates))
        (start, end, scoring_ids) = self._get_available_scores()
        elapsed = end - start
        logger.log_info('Found {} available scores for explain'.format(len(scoring_ids)))
        logger.log_debug('TIMER: Found {} available scores for explain, in {:.3f} seconds'.format(len(scoring_ids), elapsed))
        if num_explains > len(scoring_ids):
            num_explains = len(scoring_ids)
        if num_explains < 1:
            return

        if self._args.explain_start_sync:
            input('Press ENTER to start generating explain requests')

        if self._args.explain_no_cem:
            explain_mode = 'lime-only'
        else:
            explain_mode = 'lime and cem'
        logger.log_info('Generate {} explain requests ({}) ...'.format(num_explains, explain_mode))
        if pause > 0.0:
            logger.log_info('{:.3f} second pause between each explain request'.format(pause))
        for i in range(num_explains):
            if pause > 0.0 and i > 0:
                time.sleep(pause)
            scoring_id = scoring_ids[i]
            (start, end, explain) = self._generate_one_explain(scoring_id)
            elapsed = end - start
            logger.log_debug('TIMER: Request explain in {:.3f} seconds, scoring_id: {}, explain_id: {}'.format(elapsed, scoring_id, explain['metadata']['id']))
        logger.log_info('Generated {} explain requests successfully'.format(num_explains))

