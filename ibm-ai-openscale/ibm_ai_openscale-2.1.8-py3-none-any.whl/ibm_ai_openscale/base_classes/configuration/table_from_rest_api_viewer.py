# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes import Table
from ibm_ai_openscale.utils import *
from ibm_ai_openscale.utils.client_errors import ClientError
from ibm_ai_openscale.supporting_classes import InputDataType
from base64 import b64decode


_DEFAULT_LIST_LENGTH = 50


@logging_class
class TableFromRestApiViewer:

    def __init__(self, ai_client, subscription, configuration, table_name=None):
        self._ai_client = ai_client
        self._subscription = subscription
        self._configuration = configuration
        self._table_name = table_name

    def _get_table_name(self):
        if self._table_name is not None:
            return self._table_name

        configuration_details = self._configuration.get_details()

        if not configuration_details['enabled']:
            raise ClientError('Required monitoring/logging is not enabled.')

        if 'parameters' in configuration_details and 'table_name' in configuration_details['parameters']:
            if '.' in configuration_details['parameters']['table_name']:
                table_name = configuration_details['parameters']['table_name'].split('.')[1]
            else:
                table_name = configuration_details['parameters']['table_name']
        elif 'table_name' in configuration_details['parameters']['feedback_data_reference']['location']:
            if '.' in configuration_details['parameters']['feedback_data_reference']['location']['table_name']:
                table_name = configuration_details['parameters']['feedback_data_reference']['location']['table_name'].split('.')[1]
            else:
                table_name = configuration_details['parameters']['feedback_data_reference']['location']['table_name']
        else:
            raise ClientError('Either parameters of monitoring/logging are missing or table_name is not defined.')

        return table_name

    def _get_data_from_rest_api(self, limit=None):
        raise NotImplemented()

    def _get_schema(self):
        raise NotImplemented()

    def _get_fields(self):
        return [field['name'] for field in self._get_schema()['fields']]

    def show_table(self, limit=10):
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

        result = self.get_table_content(format='python', limit=limit)

        rows = result['values']
        col_names = result['fields']

        table_name = self._get_table_name()

        Table(col_names, rows).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="{} (binding_id={}, subscription_id={})".format(
                table_name,
                self._subscription.binding_uid,
                self._subscription.uid
            )
        )

    def print_table_schema(self):
        """
        Show table schema.
        """
        schema = self._get_schema()

        schema_records = [[field['name'], field['type'], field['nullable']] for field in schema['fields']]

        Table(['name', 'type', 'nullable'], schema_records).list(
            title='Schema of ' + self._get_table_name())

    def get_table_content(self, format='pandas', limit=None):
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

        input_data_type = get_asset_property(self._subscription, 'input_data_type')

        if format not in ['python', 'pandas']:
            raise ClientError('Unsupported format chosen: {}'.format(format))

        rows = self._get_data_from_rest_api(limit=limit)

        if limit is not None:
            rows = rows[0:limit]

        fields = self._get_fields()

        for row_index, row in enumerate(rows):
            row_array = []
            for value_index, value in enumerate(row):
                if input_data_type != InputDataType.STRUCTURED and type(value) == str and 'scoring_input' in fields and value_index == fields.index('scoring_input'):
                    row_array.append(decode_hdf5(value))
                else:
                    row_array.append(value)

            rows[row_index] = tuple(row_array)

        if format == 'python':
            return {'fields': fields, 'values': rows}
        elif format == 'pandas':
            import pandas as pd
            return pd.DataFrame.from_records(rows, columns=self._get_fields())
        else:
            raise ClientError('Unsupported format chosen: {}'.format(format))

    def describe_table(self, limit=None):
        """
        Prints description of the content of table (pandas style). It will remove columns with unhashable values.

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> client.describe_table()
        """

        df = self.get_table_content(format='pandas', limit=limit)

        columns_to_remove = []
        for column_name in list(df):
            try:
                df[column_name].describe()
            except:
                columns_to_remove.append(column_name)

        df = df.drop(columns=columns_to_remove)
        description = df.describe()
        print(description)


    def _translate_type(self, el, el_type):
        if el_type == 'timestamp':
            from dateutil import parser
            return parser.parse(el)
        elif el_type == 'json':
            return json.loads(el)
        else:
            return el

    def _prepare_row(self, row, schema):
        if type(row) == dict:
            row = [row[field['name']] for field in schema['fields']]

        if type(row) == list:
            return [self._translate_type(el, schema['fields'][i]['type']) for i, el in enumerate(row)]
        else:
            raise ClientError("Unexpected row type: {}".format(type(row)))
