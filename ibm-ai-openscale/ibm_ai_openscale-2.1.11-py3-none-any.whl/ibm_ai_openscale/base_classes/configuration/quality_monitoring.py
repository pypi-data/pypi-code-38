# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
from ibm_ai_openscale.base_classes.configuration.custom_metrics_viewer import CustomMetricsViewer
from ibm_ai_openscale.supporting_classes.enums import *
from ibm_ai_openscale.utils import validate_asset_properties


_DEFAULT_LIST_LENGTH = 50


@logging_class
class QualityMonitoring:
    """Manage fairness monitoring for asset."""

    def __init__(self, subscription, ai_client):
        self._ai_client = ai_client
        self._subscription = subscription
        self._custom_metrics_viewer = CustomMetricsViewer(ai_client, subscription, MetricTypes.QUALITY_MONITORING, 'QualityMetrics')

    def enable(self, threshold, min_records, **kwargs):
        """
        Enables model quality monitoring. The monitor is being run hourly.

        :param threshold: the threshold for quality metric (accuracy, areaUnderROC or r2).
        :type threshold: float

        :param min_records: minial feedback record count that triggers monitoring
        :type min_records: int

        A way you might use me is:

        >>> subscription.quality_monitoring.enable(threshold=0.8, min_records=5)
        """

        if bool(kwargs):
            raise IncorrectParameter(parameter_name=', '.join(list(kwargs.keys())),
                                 reason='Asset properties should be specified using subscriptions.add() or subscription.update() methods.')

        asset_properties = self._subscription.get_details()['entity']['asset_properties']
        validate_asset_properties(asset_properties, ['problem_type', 'output_data_schema'])

        if threshold is None or min_records is None:
            raise MissingValue('Missing one of required parameters: threshold, min_records.')

        params = {
                    "evaluation_definition": {
                        "method": asset_properties['problem_type'],
                        "threshold": threshold
                    },
                    "min_feedback_data_size": min_records,
                  }

        response = requests_session.put(
            self._ai_client._href_definitions.get_quality_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": True,
                "parameters": params
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'quality monitoring setup', response)

    def run(self, model_type='original', background_mode=True):
        """
        Run model quality evaluation on demand.

        :param model_type: type of model, by default `original` (expected one of values: `all`, `original`, `recommended`)
        :type model_type: str

        :param background_mode: if set to True, run will be in asynchronous mode, if set to False it will wait for result (optional)
        :type background_mode: bool

        :return: result of run, or run details if in background mode
        :rtype: str
        """

        response = requests_session.post(
            self._ai_client._href_definitions.get_evaluation_href(self._subscription.binding_uid, self._subscription.uid) + '?model_type=' + model_type,
            headers=self._ai_client._get_headers()
        )

        result = handle_response(202, u'quality evaluation run', response)

        request_id = result['id']

        if background_mode:
            return result

        def check_state():
            details = self.get_run_details(request_id)
            return details['status']

        def get_result():
            details = self.get_run_details(request_id)
            state = details['status']

            if state in ['completed']:
                return "Successfully finished run", None, details
            else:
                return "Run failed with status: {}".format(state), 'Reason: {}'.format(details['error']), details

        return print_synchronous_run(
            'Waiting for end of quality monitoring run {}'.format(request_id),
            check_state,
            get_result=get_result,
            success_states=['completed']
        )

    def get_run_details(self, run_uid=None):
        """
        Returns details of run.

        :param run_id: id of run (it can be taken from `run` function when background_mode == True) (optional)
        :type run_id: str

        :return: details of run
        :rtype: str
        """

        if run_uid is not None:
            response = requests_session.get(self._ai_client._href_definitions.get_evaluation_run_details_href(self._subscription.binding_uid, self._subscription.uid, run_uid),
                headers = self._ai_client._get_headers())
        else:
            response = requests_session.get(
                self._ai_client._href_definitions.get_evaluation_href(self._subscription.binding_uid, self._subscription.uid),
                headers=self._ai_client._get_headers())


        return handle_response(200, u'quality evaluation run details', response)

    def get_details(self):
        """
        Returns details of quality monitoring configuration.

        :return: configuration of quality monitoring
        :rtype: dict
        """
        response = requests_session.get(
            self._ai_client._href_definitions.get_quality_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'quality monitoring configuration', response)

    def disable(self):
        """
        Disables quality monitoring.
        """
        if not self.get_details()['enabled']:
            raise ClientError('Monitor is not enabled, so it cannot be disabled.')

        response = requests_session.put(
            self._ai_client._href_definitions.get_quality_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": False
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'quality monitoring unset', response)

    def get_deployment_metrics(self, deployment_uid=None):
        """
        Gets last quality metrics grouped by deployments.

        :param deployment_uid: UID of deployment for which the metrics which be prepared (optional)
        :type deployment_uid: str

        :return: metrics
        :rtype: dict
        """
        return self._subscription.get_deployment_metrics(deployment_uid=deployment_uid, metric_type=MetricTypes.QUALITY_MONITORING)

    def get_metrics(self, deployment_uid=None, format='samples', start_time=None):
        """
        Returns quality metrics of specified type and format for selected subscription

        :param deployment_uid: deployment uid for which the metrics will be retrieved (optional)
        :type deployment_uid: str

        :param format: format of returned metrics, possible values: `samples`, `time_series` (optional, default value: `samples`) (optional)
        :type format: str

        :param start_time: start time ("2019-05-22T00:00:00Z") - returns metrics from that timestamp to current time. By default last 3 months are used.
        :type start_time: str

        :return: metrics for deployment
        :rtype: dict
        """

        return self._custom_metrics_viewer.get_metrics(deployment_uid=deployment_uid, format=format, start_time=start_time)

    def show_table(self, limit=10):
        """
        Show records in quality metrics view. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.quality_monitoring.show_table()
        >>> subscription.quality_monitoring.show_table(limit=20)
        >>> subscription.quality_monitoring.show_table(limit=None)
        """
        self._custom_metrics_viewer.show_table(limit=limit)

    def print_table_schema(self):
        """
        Show quality metrics view schema.
        """
        self._custom_metrics_viewer.print_table_schema()

    def get_table_content(self, format='pandas', limit=None):
        """
        Get content of quality metrics view in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas' (optional)
        :type format: {str_type}

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        :return: quality table content
        :rtype: pandas or dict depending on format

        A way you might use me is:

        >>> pandas_table_content = subscription.quality_monitoring.get_table_content()
        >>> table_content = subscription.quality_monitoring.get_table_content(format='python')
        >>> pandas_table_content = subscription.quality_monitoring.get_table_content(format='pandas')
        """
        return self._custom_metrics_viewer.get_table_content(format=format, limit=limit)

    def describe_table(self, limit=None):
        """
        Prints description of the content of quality monitoring table (pandas style). It will remove columns with unhashable values.

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.quality_metrics.describe_table(limit=limit)
        """
        self._custom_metrics_viewer.describe_table()

    def show_confusion_matrix(self, measurement_id):
        """
        Prints confusion matrix for measurement_id which can be found using `show_table` function.

        :param measurement_id: measurement_id which can be found using `show_table` function
        :type measurement_id: str
        """
        self._custom_metrics_viewer.show_confusion_matrix(measurement_id)
