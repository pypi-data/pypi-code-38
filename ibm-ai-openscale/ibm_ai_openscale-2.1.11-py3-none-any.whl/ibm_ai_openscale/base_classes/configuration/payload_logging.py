# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
from ibm_ai_openscale.supporting_classes import PayloadRecord, InputDataType
from ibm_ai_openscale.base_classes.configuration.table_from_rest_api_viewer import TableFromRestApiViewer
from ibm_ai_openscale.base_classes.configuration.data_distribution import DataDistribution


_DEFAULT_LIST_LENGTH = 50


@logging_class
class PayloadLogging(TableFromRestApiViewer):
    """
    Manage payload logging for asset.

    :var data_distribution: Manage data distribution runs
    :vartype data_distribution: DataDistribution
    """

    def __init__(self, subscription, ai_client):
        TableFromRestApiViewer.__init__(self, ai_client, subscription, self)
        self._ai_client = ai_client
        self.data_distribution = DataDistribution(ai_client, subscription, 'payload')

    def enable(self, dynamic_schema_update=None):
        """
        Enables payload logging.

        :param dynamic_schema_update: schema will be automatically updated when asset will be scored (optional)
        :type dynamic_schema_update: bool
        """

        payload = {
            "enabled": True,
        }

        if dynamic_schema_update is not None:
            payload['parameters'] = {
                'dynamic_schema_update': dynamic_schema_update
            }

        response = requests_session.put(
            self._ai_client._href_definitions.get_payload_logging_href(self._subscription.binding_uid, self._subscription.uid),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'payload logging setup', response)

    def get_details(self):
        """
        Will return details of payload logging. Info about configuration.

        :return: configuration of payload logging
        :rtype: dict
        """
        response = requests_session.get(
            self._ai_client._href_definitions.get_payload_logging_href(self._subscription.binding_uid, self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'payload logging configuration', response)

    def disable(self):
        """
        Disables payload logging.
        """

        if not self.get_details()['enabled']:
            raise ClientError('Payload logging is not enabled, so it cannot be disabled.')

        response = requests_session.put(
            self._ai_client._href_definitions.get_payload_logging_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": False
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'payload logging unset', response)

    def store(self, records=None, deployment_id=None):
        """
         Stores payload records in payload logging table.

         :param records: PayloadRecord objects containing request, response and additional metrics to be stored. (optional)
         :type records: list of PayloadRecord objects

         :param deployment_id: deployment identifier (optional). If not provided first deployment id from subscription is taken. (optional)
         :type deployment_id: str


         A way you might use me is:

         >>> from ibm_ai_openscale.supporting_classes import PayloadRecord
         >>>
         >>> records_list = [PayloadRecord(request=request1, response=response1, response_time=time1), PayloadRecord(request=request2, response=response2, response_time=time2)]
         >>> subscription.payload_logging.store(records_list)

        """

        validate_type(records, "records", list, True)
        validate_type(records[0], "record", PayloadRecord, True)
        validate_type(deployment_id, "deployment_id", str, False)

        if deployment_id is not None:
            deployment_uid = deployment_id
        else:
            deployments = self._subscription.get_details()['entity']['deployments']
            if len(deployments) > 0:
                deployment_uid = deployments[0]['deployment_id']
            else:
                deployment_uid = 'generic_deployment'

        payload = []

        for record in records:
            payload.append(record._to_json(binding_uid=self._subscription.binding_uid, subscription_uid=self._subscription.uid, deployment_uid=deployment_uid))

        headers = self._ai_client._get_headers()
        headers['Prefer'] = 'return=minimal'

        response = requests_session.post(
            self._ai_client._href_definitions.get_payload_logging_storage_href(),
            json=payload,
            headers=headers
        )

        if response.status_code == 202: # TODO only 204 should remain when header Prefer will start working
            handle_response(202, u'payload logging storage', response)
        else:
            handle_response(204, u'payload logging storage', response, json_response=False)

    def show_table(self, limit=10):
        """
        Show records in payload logging table. By default 10 records will be shown. Maximal number of records is 1000.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.payload_logging.show_table()
        >>> subscription.payload_logging.show_table(limit=20)
        >>> subscription.payload_logging.show_table(limit=None)
        """
        super(PayloadLogging, self).show_table(limit=limit)

    def print_table_schema(self):
        """
        Show payload logging table schema.
        """
        super(PayloadLogging, self).print_table_schema()

    def get_table_content(self, format='pandas', limit=1000):
        """
        Get content of payload logging table in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas' (optional)
        :type format: {str_type}

        :param limit: maximal number of fetched rows (by default set to 1000, can be set to None to get all existing rows)
        :type limit: int

        :return: payload table content
        :rtype: pandas or dict depending on format

        A way you might use me is:

        >>> pandas_table_content = subscription.payload_logging.get_table_content()
        >>> table_content = subscription.payload_logging.get_table_content(format='python')
        >>> pandas_table_content = subscription.payload_logging.get_table_content(format='pandas')
        """
        return super(PayloadLogging, self).get_table_content(format=format, limit=limit)

    def describe_table(self, limit=1000):
        """
        Prints description of the content of payload logging table (pandas style). It will remove columns with unhashable values.

        :param limit: maximal number of fetched rows. (by default for payload logging it is set to 1000)
        :type limit: int

        A way you might use me is:

        >>> subscription.payload_logging.describe_table()
        """
        return super(PayloadLogging, self).describe_table(limit=limit)

    def _get_data_from_rest_api(self, limit=None):

        def validate(response):
            handle_response(200, u'payload logging transactions', response)

        def merge(result, response):
            response_json = response.json()

            if result['fields'] is None:
                result['fields'] = response_json['fields']

            result['values'] += response_json['values']

            return result

        def get_number_of_elements(response):
            response_json = response.json()
            return len(response_json['values'])


        result = get_paged_resource(
            requests_session.get,
            self._ai_client._href_definitions.get_payload_transactions_href(self._subscription.uid),
            self._ai_client._get_headers(),
            limit,
            {'fields': None, 'values': []},
            validate,
            merge,
            get_number_of_elements,
            join_character='&',
            default_limit=1000
        )

        values = (result['scoring_payload'] if 'scoring_payload' in result else result)['values']

        return [self._prepare_row(value, self._get_schema()) for value in values]

    def _get_schema(self):
        response = requests_session.get(
            self._ai_client._href_definitions.get_payload_logging_schema_href(self._subscription.binding_uid,
                                                                              self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'payload logging get table schema', response)['table_schema']

    def _get_table_name(self):
        table_name = self.get_details()['parameters']['table_name']

        return table_name.split('.')[-1]
