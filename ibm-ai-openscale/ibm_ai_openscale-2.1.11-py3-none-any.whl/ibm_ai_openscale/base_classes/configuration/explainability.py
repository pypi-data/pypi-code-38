# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.supporting_classes import *
from ibm_ai_openscale.base_classes.configuration.table_from_rest_api_viewer import TableFromRestApiViewer
from ibm_ai_openscale.supporting_classes.enums import *
from ibm_ai_openscale.utils import validate_asset_properties, get_asset_property
from pandas.core.frame import DataFrame
from ibm_ai_openscale.utils.training_stats import TrainingStats
from ibm_ai_openscale.base_classes import Table



_DEFAULT_LIST_LENGTH = 50


@logging_class
class Explainability(TableFromRestApiViewer):
    """Manage explainability for asset."""

    def __init__(self, subscription, ai_client):
        TableFromRestApiViewer.__init__(
            self, ai_client, subscription, self, 'Explanations')
        self._ai_client = ai_client
        self._subscription = subscription
        self._engine = subscription._ai_client.data_mart.bindings.get_details(
            subscription.binding_uid)['entity']['service_type']

    def enable(self, training_data_statistics=None, training_data=None, **kwargs):
        """
        Enables explainability.

        :param training_data_statistics: dictionary with training data characteristics (optional). Structured/tabular data only.
        :type training_data_statistics: dict

        :param training_data: pandas DataFrame with training data (optional). Structured/tabular data only.
        :type training_data: DataFrame

        A way you might use me is:

        >>> subscription.explainability.enable(training_data_statistics=stats_dict)
        >>> subscription.explainability.enable(training_data=pandas_df)
        """

        if bool(kwargs):
            raise IncorrectParameter(parameter_name=', '.join(list(kwargs.keys())),
                                     reason='Asset properties should be specified using subscriptions.add() or subscription.update() methods.')

        subscription_details = self._subscription.get_details()
        asset_properties = subscription_details['entity']['asset_properties']
        validate_asset_properties(asset_properties, ['input_data_type'])
        input_data_type = asset_properties['input_data_type']
        params = {}

        if input_data_type == InputDataType.STRUCTURED:

            validate_asset_properties(asset_properties, ['output_data_schema', 'feature_fields', 'label_column',
                                                         'problem_type'])

            if training_data_statistics is not None:
                validate_meta_prop(training_data_statistics, 'explainability_configuration', dict, True)
                params['training_statistics'] = training_data_statistics["explainability_configuration"]

            elif training_data is not None:
                validate_type(training_data, 'training_data', DataFrame, True)
                subscription_details = self._subscription.get_details()
                asset_properties = subscription_details['entity']['asset_properties']

                training_data_information = {
                    'label_column': asset_properties['label_column'],
                    'feature_columns': asset_properties['feature_fields'],
                    'categorical_columns': asset_properties['categorical_fields'],
                    'problem_type': asset_properties['problem_type']
                }

                # Compute explainability stats
                training_stats = TrainingStats(
                    training_data, training_data_information, fairness=False)
                explain_config = training_stats.get_training_statistics()
                training_data_statistics_4_explainability = explain_config.get("explainability_configuration")

                if 'd_means' in training_data_statistics_4_explainability.keys():
                    params['training_statistics'] = training_data_statistics_4_explainability
                else:
                    raise IncorrectValue(
                        'training data statistics', reason='training data statistics are missing one of required fields.')

            elif 'training_data_reference' not in asset_properties.keys():
                    raise MissingMetaProp('training_data_reference or training_data_statistics or training_data')

        response = requests_session.post(
            self._ai_client._href_definitions.get_model_explanation_configurations_href(),
            json={
                "data_mart_id": self._ai_client._service_credentials['data_mart_id'],
                "service_binding_id": self._subscription.binding_uid,
                "model_id": self._subscription.source_uid,
                "enabled": True,
                "parameters": params
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'explainability setup', response)

    def get_details(self):
        """
        Will return details of explainability. Info about configuration.

        :return: configuration of explainability
        :rtype: dict
        """
        response = requests_session.get(
            self._ai_client._href_definitions.get_explainability_href(
                self._subscription.binding_uid, self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'explainability get details', response)

    def disable(self):
        """
        Disables explainability.
        """

        if not self.get_details()['enabled']:
            raise ClientError('Monitor is not enabled, so it cannot be disabled.')

        response = requests_session.put(
            self._ai_client._href_definitions.get_explainability_href(
                self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": False
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'explainability unset', response)

    def get_run_details(self, run_uid):
        """
        Returns details of run.

        :param run_id: id of run (it can be taken from `run` function when background_mode == True)
        :type run_id: str

        :return: details of run
        :rtype: str
        """
        validate_type(run_uid, "run_uid", str, True)

        response = requests_session.get(
            self._ai_client._href_definitions.get_model_explanation_run_href(
                run_uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'explainability get details', response, True)

    def run(self, transaction_id, background_mode=False, cem=True):
        """
        Runs explainability.

        :param transaction_id: id of transaction used for scoring
        :type transaction_id: str

        :param background_mode: if set to True, run will be in asynchronous mode, if set to False it will wait for result
        :type background_mode: bool

        :param cem: (contrastive explanations) if set to False, only Lime is used for explanation
        :type cem: bool

        :return: result of run, or run details if in background mode
        :rtype: str
        """

        headers = self._ai_client._get_headers()

        endpoint_url = self._ai_client._href_definitions.get_model_explanations_href()

        response = requests_session.post(
            endpoint_url,
            json={
                "scoring_id": transaction_id,
                "cem": 'true' if cem else 'false'
            },
            headers=headers
        )

        result = handle_response(202, u'explainability run', response, True)

        request_id = result['metadata']['id']

        if background_mode:
            return result

        def check_state():
            try:
                details = self.get_run_details(request_id)
                return details['entity']['status']['state']
            except:
                return 'error'

        def get_result():
            try:
                details = self.get_run_details(request_id)
                state = details['entity']['status']['state']
            except ApiRequestFailure as e:
                details = e.response.json()
                return "Run failed with status: error", 'Reason: {}'.format(details['errors']), None

            if state in ['success', 'finished'] and details['entity']['status']['cem_state'] == 'error':
                return "Partially successfully finished run, cem_error=\"{}\"".format(details['entity']['error_cem']['error_msg']), None, details
            if state in ['success', 'finished'] and details['entity']['status']['lime_state'] == 'error':
                return "Partially successfully finished run, lime_error=\"{}\"".format(details['entity']['error_lime']['error_msg']), None, details
            if state in ['success', 'finished']:
                return "Successfully finished run", None, details
            else:
                return "Run failed with status: {}".format(state), 'Reason: {}'.format(details['entity']['error']['error_msg']) if 'error' in details['entity'] else None, details

        return print_synchronous_run(
            'Looking for explanation for {}'.format(transaction_id),
            check_state,
            get_result=get_result,
            run_states=['in_progress']
        )

    def show_table(self, limit=10):
        """
        Show records in explainability view. By default 10 records will be shown. Maximal number of records is 1000.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.explainability.show_table()
        >>> subscription.explainability.show_table(limit=20)
        >>> subscription.explainability.show_table(limit=None)
        """
        super(Explainability, self).show_table(limit=limit)

    def print_table_schema(self):
        """
        Show explainability view schema.
        """
        super(Explainability, self).print_table_schema()

    def get_table_content(self, format='pandas', limit=None):
        """
        Get content of explainability view in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas' (optional)
        :type format: {str_type}

        :param limit: maximal number of fetched rows (upper limit is 1000). (optional)
        :type limit: int

        :return: explainability table content
        :rtype: pandas or dict depending on format

        A way you might use me is:

        >>> pandas_table_content = subscription.explainability.get_table_content()
        >>> table_content = subscription.explainability.get_table_content(format='python')
        >>> pandas_table_content = subscription.explainability.get_table_content(format='pandas')
        """
        return super(Explainability, self).get_table_content(format=format, limit=limit)

    def describe_table(self, limit=None):
        """
        Prints description of the content of explainability table (pandas style). It will remove columns with unhashable values.

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.explainability.describe_table()
        """
        super(Explainability, self).describe_table(limit=limit)

    def _prepare_row(self, row, schema):
        return [
            row['request_id'],
            row['scoring_id'],  # transaction_id
            row['explanation']['entity']['asset']['id'] if 'explanation' in row else None,
            row['explanation']['entity']['asset']['type'] if 'explanation' in row else None,
            row['deployment_id'],
            row['subscription_id'],
            row['binding_id'],
            row['explanation'] if 'explanation' in row else None,
            row['error'] if 'error' in row else None,
            row['explanation']['entity']['status'] if 'explanation' in row else None,
            row['created_by'],
            row['created_at']
        ]

    def _get_data_from_rest_api(self, limit=None):
        if limit is None:
            limit = 1000

        response = requests_session.get(
            self._ai_client._href_definitions.get_explainability_storing_href(
            ) + "?limit={}&subscription_id={}".format(limit, self._subscription.uid) if limit is not None else "",
            headers=self._ai_client._get_headers()
        )

        response_json = handle_response(
            200, u'getting stored explainability records', response)

        schema = self._get_schema()
        return [self._prepare_row(x, schema) for x in response_json['explanations']]

    def _get_schema(self):
        return {
            'fields': [
                {'name': 'request_id', 'type': 'string', 'nullable': False},
                {'name': 'transaction_id', 'type': 'string', 'nullable': False},
                {'name': 'asset_id', 'type': 'string', 'nullable': False},
                {'name': 'asset_type', 'type': 'string', 'nullable': False},
                {'name': 'deployment_id', 'type': 'string', 'nullable': False},
                {'name': 'subscription_id', 'type': 'string', 'nullable': False},
                {'name': 'service_binding_id', 'type': 'string', 'nullable': False},
                {'name': 'explanation', 'type': 'json', 'nullable': False},
                {'name': 'error', 'type': 'json', 'nullable': False},
                {'name': 'status', 'type': 'string', 'nullable': False},
                {'name': 'created_by', 'type': 'timestamp', 'nullable': False},
                {'name': 'created_at', 'type': 'timestamp', 'nullable': False}
            ]
        }

    def list_explanations(self, limit=None):
        validate_type(limit, u'limit', int, False)

        if limit is None:
            limit = 1000

        response = requests_session.get(
            self._ai_client._href_definitions.get_explainability_storing_href(
            ) + "?limit={}&subscription_id={}".format(limit, self._subscription.uid) if limit is not None else "",
            headers=self._ai_client._get_headers()
        )

        result = handle_response(200, u'getting stored explainability records', response)

        def sort_prediction(p):
            if p is not None and 'explanation' in p:
                p['explanation'] = sorted(p['explanation'], key=lambda e: -e['weight'] if 'weight' in e else float('inf'))
            return p

        def prepare_feature_value(e):
            if 'feature_value' in e:
                return e['feature_value']

            if 'feature_range' in e:
                return '{}{},{}{}'.format(
                    '[' if 'min_inclusive' in e['feature_range'] and e['feature_range']['min_inclusive'] else '(',
                    e['feature_range']['min'] if 'min' in e['feature_range'] else '-inf',
                    e['feature_range']['max'] if 'max' in e['feature_range'] else 'inf',
                    ']' if 'max_inclusive' in e['feature_range'] and e['feature_range']['max_inclusive'] else ')'
                )

            return '-'

        rows = [
            [
                r['request_id'],
                r['scoring_id'],
                'lime: {}\ncem: {}'.format(r['explanation']['entity']['status_lime'], r['explanation']['entity']['status_cem']) if 'explanation' in r else 'error',
                p['value'] if p is not None else '',
                (p['probability'] if 'probability' in p else '-') if p is not None else '',
                '\n'.join([e['feature_name'] for e in p['explanation']]) if p is not None and 'explanation' in p else '',
                '\n'.join([str(prepare_feature_value(e)) for e in p['explanation']]) if p is not None and 'explanation' in p else '',
                '\n'.join([str(e['weight']) if 'weight' in e else '-' for e in p['explanation']]) if p is not None and 'explanation' in p else '',
                r['error']['error_msg'] if 'error' in r and 'error_msg' in r['error'] else ''
            ] for r in result['explanations']
            for p_not_sorted in (r['explanation']['entity']['predictions'] if 'explanation' in r and 'entity' in r['explanation'] and 'predictions' in r['explanation']['entity'] else ([None] if 'error' in r else []))
            for p in [sort_prediction(p_not_sorted)]
        ]
        col_names = ['request_id', 'transaction_id', 'status', 'value', 'probability', 'feature_name', 'feature_value', 'weight', 'error']

        Table(col_names, rows).list(
            limit=limit,
            title="Explanations"
        )
