# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.configuration.metrics_viewer import MetricsViewer
from ibm_ai_openscale.supporting_classes import *
from ibm_ai_openscale.engines.watson_machine_learning import WMLConsts
from pandas.core.frame import DataFrame


_DEFAULT_LIST_LENGTH = 50


@logging_class
class FairnessMonitoring(MetricsViewer):
    """Manage fairness monitoring for asset."""

    def __init__(self, subscription, ai_client):
        MetricsViewer.__init__(self, ai_client, subscription, MetricTypes.FAIRNESS_MONITORING, "FairnessMetrics")
        self._engine = subscription._ai_client.data_mart.bindings.get_details(subscription.binding_uid)['entity']['service_type']

    def enable(self, features=None, deployment_uid=None, favourable_classes=None, unfavourable_classes=None, min_records=None, training_data=None, training_data_statistics=None, **kwargs):
        """
        Enables fairness monitoring.

        :param features: the features for fairness monitoring. Feature is represented by `Feature` class object. More details can be found in `supporting_classes.Feature` section.
                         This field is optional if training_data_statistics are provided.
        :type features: list of Feature class objects

        :param deployment_uid: deployment uid for which the fairness will be enabled (optional if only one deployment is available)
        :type deployment_uid: str

        :param favourable_classes: list of favourable classes (optional)
        :type favourable_classes: list of str

        :param unfavourable_classes: list of unfavourable classes (optional)
        :type unfavourable_classes: list of str

        :param min_records: minimal number of records (optional)
        :type min_records: int

        :param training_data: pandas DataFrame with training data (optional)
        :type training_data: DataFrame

        :param training_data_statistics: dictionary with training data characteristics (optional)
        :type training_data_statistics: dict


        A way you might use me is:
        >>> from ibm_ai_openscale.supporting_classes.feature import Feature
        >>>
        >>> subscription.fairness_monitoring.enable(
        >>>    features=[
        >>>        Feature("AGE", majority=[[20,50],[60,70]], minority=[[51,59]], threshold=0.8)],
        >>>    favourable_classes=['drugY'],
        >>>    unfavourable_classes=['drugA', 'drugB', 'drugC'],
        >>>    min_records=12)
        """

        if bool(kwargs):
            raise IncorrectParameter(parameter_name=', '.join(list(kwargs.keys())),
                                 reason='Asset properties should be specified using subscriptions.add() or subscription.update() methods.')

        input_data_type = get_asset_property(self._subscription, 'input_data_type')

        if input_data_type != InputDataType.STRUCTURED:
            raise UnsupportedActionForDataType('fairness monitoring', input_data_type, InputDataType.STRUCTURED)

        if deployment_uid is None:
            uids = self._subscription.get_deployment_uids()
            if len(uids) == 0:
                raise ClientError('No deployments existing for subscription.')
            elif len(uids) > 1:
                raise ClientError('More than one deployments existing for subscription: {}'.format(uids))

            deployment_uid = uids[0]

        payload = {
                "data_mart_id": self._ai_client._service_credentials['data_mart_id'],
                "asset_id": self._subscription.uid,
                "deployment_id": deployment_uid,
        }

        if training_data_statistics is not None:
            validate_type(training_data_statistics, 'training_data_statistics', dict, False)

            if "fairness_configuration" in training_data_statistics.keys():
                payload["distributions"] = training_data_statistics["fairness_configuration"]["distributions"]
                payload["parameters"] = training_data_statistics["fairness_configuration"]["parameters"]
        elif training_data is not None:
            validate_type(training_data, 'training_data', DataFrame, True)
            validate_type(features, 'features', list, True)

            for feature in features:
                validate_type(feature, 'feature', Feature, True)

            validate_type(favourable_classes, 'favourable_classes', [str, list], True)
            validate_type(unfavourable_classes, 'unfavourable_classes', [str, list], True)
            validate_type(min_records, 'min_records', int, True)
            subscription_details = self._subscription.get_details()
            asset_properties = subscription_details['entity']['asset_properties']
            validate_asset_properties(asset_properties, ['output_data_schema', 'feature_fields', 'categorical_fields',
                                                         'label_column', 'problem_type',
                                                         ['predicted_target_field', 'prediction_field']])

            training_data_information = {
                'label_column': asset_properties['label_column'],
                'feature_columns': asset_properties['feature_fields'],
                'categorical_columns': asset_properties['categorical_fields'],
                'problem_type': asset_properties['problem_type'],
                'fairness_inputs': {
                    'min_records': min_records,
                    'fairness_attributes': [feature._to_json() for feature in features],
                    'favourable_class': favourable_classes,
                    'unfavourable_class': unfavourable_classes
                }
            }

            from ibm_ai_openscale.utils.training_stats import TrainingStats

            training_data_statistics_4_fairness = TrainingStats(training_data, training_data_information, explain=False)._TrainingStats__get_fairness_configuration()

            if "distributions" in training_data_statistics_4_fairness.keys() and "parameters" in training_data_statistics_4_fairness.keys():
                payload["distributions"] = training_data_statistics_4_fairness["distributions"]
                payload["parameters"] = training_data_statistics_4_fairness["parameters"]
            else:
                raise IncorrectValue('training data statistics', reason='Either parameters or distributions are missing in generated training data statistics.')
        else:
            validate_type(features, 'features', list, True)

            for feature in features:
                validate_type(feature, 'feature', Feature, True)

            validate_type(favourable_classes, 'favourable_classes', [str, list], True)
            validate_type(unfavourable_classes, 'unfavourable_classes', [str, list], True)
            validate_type(min_records, 'min_records', int, True)


            subscription_details = self._subscription.get_details()
            asset_properties = subscription_details['entity']['asset_properties']
            validate_asset_properties(asset_properties, ['training_data_reference', 'output_data_schema', 'label_column',
                                                         ['predicted_target_field', 'prediction_field']])

            payload['parameters'] = {
                "class_label": asset_properties['label_column'],
                "features": [feature._to_json() for feature in features],
                "favourable_class": favourable_classes,
                "unfavourable_class": unfavourable_classes,
                "min_records": min_records
            }

        payload_logging_details = self._subscription.payload_logging.get_details()

        if not payload_logging_details['enabled']:
            self._subscription.payload_logging.enable()

        response = requests_session.post(
            self._ai_client._href_definitions.get_fairness_monitoring_configuration_href(),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        handle_response(202, u'fairness monitoring setup', response)

    def get_details(self):
        """
        Returns details of fairness monitoring configuration.

        :return: configuration of fairness monitoring
        :rtype: dict
        """
        response = requests_session.get(
            self._ai_client._href_definitions.get_fairness_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'fairness monitoring configuration', response)

    def disable(self):
        """
        Disables fairness monitoring.
        """

        if not self.get_details()['enabled']:
            raise ClientError('Monitor is not enabled, so it cannot be disabled.')

        response = requests_session.put(
            self._ai_client._href_definitions.get_fairness_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": False
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'fairness monitoring unset', response)

    def get_deployment_metrics(self, deployment_uid=None):
        """
        Gets last fairness metrics grouped by deployments.

        :param deployment_uid: UID of deployment for which the metrics which be prepared (optional)
        :type deployment_uid: str

        :return: metrics
        :rtype: dict
        """
        return self._subscription.get_deployment_metrics(deployment_uid=deployment_uid, metric_type=MetricTypes.FAIRNESS_MONITORING)

    def get_run_details(self, deployment_uid=None):
        """
        Returns details of run by deployment_uid.

        :param deployment_uid: id of runned deployment, may be omitted if subscription has only one deployment
        :type deployment_uid: str

        :return: details of run
        :rtype: str
        """
        validate_type(deployment_uid, "deployment_uid", str, False)

        if deployment_uid is None:
            uids = self._subscription.get_deployment_uids()
            if len(uids) == 0:
                raise ClientError('No deployments existing for subscription.')
            elif len(uids) > 1:
                raise ClientError('More than one deployments existing for subscription: {}'.format(uids))

            deployment_uid = uids[0]

        response = requests_session.get(
            self._ai_client._href_definitions.get_fairness_monitoring_run_details_href(self._subscription.binding_uid, self._subscription.uid, deployment_uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'explainability get run details', response, True)

    def run(self, deployment_uid=None, background_mode=True):
        """
        Runs fairness check.

        :param deployment_uid: id of deployment to run, may be omitted if subscription has only one deployment
        :type deployment_uid: str

        :param background_mode: if set to True, run will be in asynchronous mode, if set to False it will wait for result
        :type background_mode: bool

        :return: result of run, or run details if in background mode
        :rtype: str
        """
        if deployment_uid is None:
            uids = self._subscription.get_deployment_uids()
            if len(uids) == 0:
                raise ClientError('No deployments existing for subscription.')
            elif len(uids) > 1:
                raise ClientError('More than one deployments existing for subscription: {}'.format(uids))

            deployment_uid = uids[0]

        response = requests_session.post(
            self._ai_client._href_definitions.get_fairness_monitoring_runs_href(self._subscription.uid),
            json={
                "data_mart_id": self._ai_client._service_credentials['data_mart_id'],
                "deployment_id": deployment_uid,
                "subscription_id": self._subscription.uid
            },
            headers=self._ai_client._get_headers()
        )

        result = handle_response(202, u'fairness monitoring run', response)

        if background_mode:
            return result

        success_states = ['FINISHED']
        failure_states = ['FINISHED WITH ERRORS']

        def extract_status(details):
            return details['entity']['parameters']['last_run_status']

        def check_state():
            details = self.get_run_details(deployment_uid)
            return extract_status(details)

        def get_result():
            details = self.get_run_details(deployment_uid)
            state = extract_status(details)

            if state in success_states:
                return "Successfully finished run", None, details
            else:
                return "Run failed with status: {}".format(state), 'Reason: {}'.format(details['entity']['parameters']['last_run_info_code'] if 'last_run_info_code' in details['entity']['parameters'] else '<missing last_run_info_code>'), details

        return print_synchronous_run(
            'Counting bias for deployment_uid={}'.format(deployment_uid),
            check_state,
            get_result=get_result,
            success_states=success_states,
            failure_states=failure_states,
            run_states=['RUNNING']
        )

    def get_metrics(self, deployment_uid, format='samples', start_time=None):
        """
        Returns fairness metrics of specified type and format for selected subscription

        :param deployment_uid: deployment uid for which the metrics will be retrieved
        :type deployment_uid: str

        :param format: format of returned metrics, possible values: `samples`, `time_series` (optional, default value: `samples`)
        :type format: str

        :param start_time: start time ("2019-05-22T00:00:00Z")- returns metrics from that timestamp to current time. By default last 3 months are used.
        :type start_time: str

        :return: metrics for deployment
        :rtype: dict
        """
        return super(FairnessMonitoring, self).get_metrics(deployment_uid, format, start_time=start_time)

    def show_table(self, limit=10):
        """
        Show records in fairness metrics view. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.fairness_monitoring.show_table()
        >>> subscription.fairness_monitoring.show_table(limit=20)
        >>> subscription.fairness_monitoring.show_table(limit=None)
        """
        super(FairnessMonitoring, self).show_table(limit=limit)

    def print_table_schema(self):
        """
        Show fairness metrics view schema.
        """
        super(FairnessMonitoring, self).print_table_schema()

    def get_table_content(self, format='pandas', limit=None):
        """
        Get content of fairness metrics view in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas' (optional)
        :type format: {str_type}

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        :return: fairness table content
        :rtype: pandas or dict depending on format

        A way you might use me is:

        >>> pandas_table_content = subscription.fairness_monitoring.get_table_content()
        >>> table_content = subscription.fairness_monitoring.get_table_content(format='python')
        >>> pandas_table_content = subscription.fairness_monitoring.get_table_content(format='pandas')
        """
        return super(FairnessMonitoring, self).get_table_content(format=format, limit=limit)

    def describe_table(self, limit=None):
        """
        Prints description of the content of fairness monitoring table (pandas style). It will remove columns with unhashable values.

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.fairness_metrics.describe_table()
        """
        super(FairnessMonitoring, self).describe_table(limit=limit)

    def debias(self, payload, deployment_uid=None):
        """
        Computes the bias mitigation/remediation.
        Makes an online prediction and de-bias prediction on a given data values.

        :param payload: scoring payload
        :type payload: dict

        :param deployment_uid: uid of deployment (optional if subscription contains single deployment)
        :type deployment_uid: str

        :return: debiased scoring response
        :rtype: dict
        """

        validate_type(deployment_uid, "deployment_uid", str, False)
        validate_type(payload, "payload", dict, True)

        if deployment_uid is None:
            uids = self._subscription.get_deployment_uids()
            if len(uids) == 0:
                raise ClientError('No deployments existing for subscription.')
            elif len(uids) > 1:
                raise ClientError('More than one deployments existing for subscription: {}'.format(uids))

            deployment_uid = uids[0]

        response = requests_session.post(
            self._ai_client._href_definitions.get_fairness_debias_run_href(self._subscription.binding_uid,
                                                                           self._subscription.uid,
                                                                           deployment_uid),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'debias run', response, True)

    def _prepare_rows(self, obj, deployment_uid=''):
        schema = self._get_schema()

        return [self._prepare_row([
                    obj['timestamp'],
                    metrics['feature'],
                    value['value'],
                    value['is_biased'],
                    value['fairness_value'],
                    value['fav_class_percent'],
                    self._subscription.binding_uid,
                    self._subscription.uid,
                    obj['asset_revision'],
                    deployment_uid,
                    ''
                ], schema) for metrics in obj['value']['metrics'] for value in metrics['minority']['values']]

    def _get_schema(self):
        return {
            'fields': [
                {'name': 'ts', 'type': 'timestamp', 'nullable': False},
                {'name': 'feature', 'type': 'string', 'nullable': False},
                {'name': 'feature_value', 'type': 'object', 'nullable': False},
                {'name': 'fairness_biased', 'type': 'boolean', 'nullable': False},
                {'name': 'fairness_value', 'type': 'int', 'nullable': False},
                {'name': 'fairness_fav_class', 'type': 'int', 'nullable': False},
                {'name': 'binding_id', 'type': 'string', 'nullable': False},
                {'name': 'subscription_id', 'type': 'string', 'nullable': False},
                {'name': 'asset_revision', 'type': 'string', 'nullable': True},
                {'name': 'deployment_id', 'type': 'string', 'nullable': True},
                {'name': 'process', 'type': 'string', 'nullable': False}
            ]
        }