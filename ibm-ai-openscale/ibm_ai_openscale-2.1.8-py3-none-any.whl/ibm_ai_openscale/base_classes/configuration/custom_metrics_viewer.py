# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2019
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from datetime import datetime, timedelta
from ibm_ai_openscale.utils import *
from ibm_ai_openscale.supporting_classes import MetricsFormat
from concurrent.futures import ThreadPoolExecutor
from ibm_ai_openscale.base_classes import Table
from ibm_ai_openscale.base_classes.configuration.table_from_rest_api_viewer import TableFromRestApiViewer


_DEFAULT_LIST_LENGTH = 50


@logging_class
class CustomMetricsViewer(TableFromRestApiViewer):
    def __init__(self, ai_client, subscription, metric_type, table_name):
        TableFromRestApiViewer.__init__(self, ai_client, subscription, self, table_name)
        self._ai_client = ai_client
        self._subscription = subscription
        self._metric_type = metric_type

    def get_metrics(self, deployment_uid=None, format="samples", monitor_uid=None, start_time=None):
        validate_type(deployment_uid, 'deployment_uid', str, False)
        validate_enum(format, 'format', MetricsFormat, True)
        validate_type(start_time, 'start_time', str, False)

        subscription_details = self._subscription.get_details()
        weeks_number = 12

        if start_time is None:
            try:
                start_time = datetime.strptime(subscription_details['metadata']['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")\
                             - timedelta(weeks=weeks_number)
            except:
                start_time = datetime.strptime(subscription_details['metadata']['created_at'], "%Y-%m-%dT%H:%M:%SZ")\
                                 - timedelta(weeks=weeks_number)
            start_time = start_time.isoformat() + 'Z'

        monitor_definition_id = self._metric_type if monitor_uid is None else monitor_uid

        response = requests_session.get(
            self._ai_client._href_definitions.get_ootb_metrics_get_href(
                monitor_definition_id=monitor_definition_id,
                result_format=format,
                start=start_time,
                end=datetime.utcnow().isoformat() + 'Z',
                binding_id=self._subscription.binding_uid,
                subscription_id=self._subscription.uid
            ) + ("&deployment_uid={}".format(deployment_uid) if deployment_uid is not None else ""),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, "getting {} metrics".format(monitor_definition_id), response, True)

    def _get_data_from_rest_api(self, limit=None, monitor_uid=None): # Warning - limit not used
        def get_rows(deployment_uid): # TODO - asynchronous?
            result = self.get_metrics(deployment_uid=deployment_uid, monitor_uid=monitor_uid)

            return [row for metrics in result for row in self._prepare_rows(metrics, deployment_uid)]

        deployment_uids = self._subscription.get_deployment_uids()

        with ThreadPoolExecutor(max_workers=10) as executor:
            deployment_uids = [(uid) for uid in deployment_uids]
            prepared_rows = executor.map(get_rows, deployment_uids)
        return [row for rows in prepared_rows for row in rows]

    def _prepare_rows(self, obj, deployment_uid=''):
        # def get_limit(row, limit_type):
        #     try:
        #         return list(filter(lambda x: x['type'] == limit_type, row['thresholds']))['value']
        #     except:
        #         return ''

        def prepare_row(row):
            return [
                obj['ts'],
                row['id'],
                obj['measurement_id'] if 'measurement_id' in obj else '',
                row['value'],
                row['lower_limit'] if 'lower_limit' in row else '',
                row['upper_limit'] if 'upper_limit' in row else '',
                ', '.join(['{}: {}'.format(t['id'], t['value']) for t in obj['tags']]) if 'tags' in obj else '',
                self._subscription.binding_uid,
                self._subscription.uid,
                deployment_uid
            ]

        return [self._prepare_row(prepare_row(metric_record), self._get_schema()) for metric_record in obj['metrics']]

    def _get_schema(self):
        return {
            'fields': [
                {'name': 'ts', 'type': 'timestamp', 'nullable': False},
                {'name': 'id', 'type': 'string', 'nullable': False},
                {'name': 'measurement_id', 'type': 'string', 'nullable': True},
                {'name': 'value', 'type': 'float', 'nullable': False},
                {'name': 'lower limit', 'type': 'float', 'nullable': True},
                {'name': 'upper limit', 'type': 'float', 'nullable': True},
                {'name': 'tags', 'type': 'string', 'nullable': False},
                {'name': 'binding_id', 'type': 'string', 'nullable': False},
                {'name': 'subscription_id', 'type': 'string', 'nullable': False},
                {'name': 'deployment_id', 'type': 'string', 'nullable': True}
            ]
        }

    def show_table(self, limit=10, monitor_uid=None):
        """
        Show records in payload logging table. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> client.payload_logging.show_table()
        >>> client.payload_logging.show_table(limit=20)
        >>> client.payload_logging.show_table(limit=None)
        """
        validate_type(limit, u'limit', int, False)

        result = self.get_table_content(format='python', monitor_uid=monitor_uid, limit=limit)

        rows = result['values']
        col_names = result['fields']

        Table(col_names, rows, date_field_name='ts').list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="{} (binding_id={}, subscription_id={})".format(
                self._get_table_name(),
                self._subscription.binding_uid,
                self._subscription.uid
            )
        )

    def get_table_content(self, format='pandas', limit=None, monitor_uid=None):
        """
        Get content of table in chosen format. Supported only for structured data.
        By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas'
        :type format: {str_type}

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> pandas_table_content = client.get_table_content()
        >>> table_content = client.get_table_content(format='python')
        >>> pandas_table_content = client.get_table_content(format='pandas')
        """

        validate_type(format, u'format', str, True)

        if format not in ['python', 'pandas']:
            raise ClientError('Unsupported format chosen: {}'.format(format))

        rows = self._get_data_from_rest_api(monitor_uid=monitor_uid, limit=limit)

        if limit is not None:
            rows = rows[0:limit]

        for row_index, row in enumerate(rows):
            row_array = []
            for value in row:
                if type(value) == memoryview: # TODO will this be needed?
                    row_array.append(decode_hdf5(value))
                else:
                    row_array.append(value)

            rows[row_index] = tuple(row_array)

        if format == 'python':
            return {'fields': self._get_fields(), 'values': rows}
        elif format == 'pandas':
            import pandas as pd
            return pd.DataFrame.from_records(rows, columns=self._get_fields())
        else:
            raise ClientError('Unsupported format chosen: {}'.format(format))

    def describe_table(self, monitor_uid=None, limit=None):
        """
        Prints description of the content of table (pandas style). It will remove columns with unhashable values.

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.monitoring.describe_table(monitor_uid='123')
        """

        df = self.get_table_content(format='pandas', monitor_uid=monitor_uid, limit=limit)

        columns_to_remove = []
        for column_name in list(df):
            try:
                df[column_name].describe()
            except:
                columns_to_remove.append(column_name)

        df = df.drop(columns=columns_to_remove)
        description = df.describe()
        print(description)

    def show_confusion_matrix(self, measurement_id, monitor_uid=None):
        monitor_definition_id = self._metric_type if monitor_uid is None else monitor_uid

        response = requests_session.get(
            self._ai_client._href_definitions.get_measurement_href(measurement_id, monitor_definition_id),
            headers=self._ai_client._get_headers()
        )

        result = handle_response(200, "getting {} measurement".format(measurement_id), response, True)

        confusion_matrix_list = list(filter(lambda x: x['id'] == 'confusion_matrix_1', result['sources']))
        if len(confusion_matrix_list) > 0:
            confusion_matrix = confusion_matrix_list[0]['data']

            col_names = ['actual \ predicted'] + confusion_matrix['labels'] + ['recall', 'precision']
            rows = [[confusion_matrix['labels'][i]] + row + [confusion_matrix['recall_per_label'][i] if 'recall_per_label' in confusion_matrix else '-', confusion_matrix['precision_per_label'][i] if 'precision_per_label' in confusion_matrix else '-'] for i, row in enumerate(confusion_matrix['values'])]

            Table(col_names, rows).list(
                title="Confusion matrix for (measurement_id={})".format(measurement_id)
            )

        else:
            print("No confusion matrix found for measurement id.")
