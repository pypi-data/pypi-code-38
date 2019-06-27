# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.supporting_classes import *
from ibm_ai_openscale.subscriptions import Subscriptions
from ibm_ai_openscale.bindings import Bindings
from ibm_ai_openscale.monitors import Monitors
from ibm_ai_openscale.base_classes import Table
from concurrent.futures import ThreadPoolExecutor
import inspect


@logging_class
class DataMart:
    """
    Manages DB instance.

    :var bindings: Manage bindings of you Watson OpenScale instance.
    :vartype bindings: Bindings
    :var subscriptions: Manage subscriptions of your IBM OpenScale instance.
    :vartype subscriptions: Subscriptions
    """
    def __init__(self, ai_client):
        from ibm_ai_openscale.base_classes.client.client import APIClientBase
        validate_type(ai_client, 'ai_client', APIClientBase, True)
        self._logger = logging.getLogger(__name__)
        self._ai_client = ai_client
        self._internal_db = False
        self.bindings = Bindings(ai_client)
        self.subscriptions = Subscriptions(ai_client)
        self.monitors = Monitors(ai_client)

    def _prepare_db_credentials_payload(self, db_credentials=None, schema=None, internal_db=False):
        if internal_db is False:
            validate_type(db_credentials, 'db_credentials', [dict, DatabaseCredentials], True)
            validate_type(schema, 'schema', str, False)

            if issubclass(db_credentials.__class__, DatabaseCredentials):
                credentials = db_credentials.credentials
            else:
                credentials = db_credentials
                db_credentials = None

            # determine db_type

            if db_credentials is None:
                if 'db_type' in credentials:
                    db_type = credentials['db_type']
                else:
                    cred_str = str(credentials)

                    if 'postgres' in cred_str:
                        db_type = "postgresql"
                    elif 'db2' in cred_str:
                        db_type = "db2"
                    else:
                        raise ClientError("Unsupported type of db.")
            else:
                if type(db_credentials) == DB2:
                    db_type = "db2"
                elif type(db_credentials) == PostgreSQL:
                    db_type = "postgresql"

            # prepare request

            if 'name' in credentials.keys():
                db_name = credentials['name']
            else:
                db_name = str(db_type)

            database_configuration = {
                "database_type": db_type,
                "name": db_name,
                "credentials": credentials,
                "location": {}
            }

            if schema is not None:
                database_configuration['location']['schema'] = schema

            payload = {"database_configuration": database_configuration}
        else:
            self._internal_db = internal_db
            payload = {"internal_database": internal_db}

        return payload

    def setup(self, db_credentials=None, schema=None, internal_db=False):
        """
        Setups db instance.

        :param db_credentials: describes the instance which should be connected
        :type db_credentials: dict

        :param schema: schema in your database under which the tables should be created
        :type schema: str

        :param internal_db: you can use internally provided database. Please note that this db comes with limitations.
        :type internal_db: bool

        Examples of usage (postgres):

        >>> postgres_credentials = {
        >>>     "db_type": "postgresql",
        >>>     "uri_cli_1": "xxx",
        >>>     "maps": [],
        >>>     "instance_administration_api": {
        >>>         "instance_id": "xxx",
        >>>         "root": "xxx",
        >>>         "deployment_id": "xxx"
        >>>     },
        >>>     "name": "xxx",
        >>>     "uri_cli": "xxx",
        >>>     "uri_direct_1": "xxx",
        >>>     "ca_certificate_base64": "xxx",
        >>>     "deployment_id": "xxx",
        >>>     "uri": "xxx"
        >>> }
        >>>
        >>> # option 1:
        >>> ai_client.data_mart.setup(db_credentials=postgres_credentials)
        >>> # option 2:
        >>> ai_client.data_mart.setup(db_credentials=PostgreSQL(postgres_credentials))

        Examples of usage (db2):

        >>> db2_credentials = {
        >>>     "hostname": "xxx",
        >>>     "password": "xxx",
        >>>     "https_url": "xxx",
        >>>     "port": 50000,
        >>>     "ssldsn": "xxx",
        >>>     "host": "xxx",
        >>>     "jdbcurl": "xxx",
        >>>     "uri": "xxx",
        >>>     "db": "BLUDB",
        >>>     "dsn": "xxx",
        >>>     "username": "xxx",
        >>>     "ssljdbcurl": "xxx"
        >>> }
        >>>
        >>> # option 1:
        >>> ai_client.data_mart.setup(db_credentials=db2_credentials)
        >>> # option 2:
        >>> ai_client.data_mart.setup(db_credentials=DB2(db2_credentials))

        Example of usage (internal db):

        >>> ai_client.data_mart.setup(internal_db=True)
        """

        payload = self._prepare_db_credentials_payload(db_credentials, schema, internal_db)

        response = requests_session.put(
            self._ai_client._href_definitions.get_data_mart_href(),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        try:
            handle_response(200, "setup of data mart", response, False)
        except ApiRequestWarning:
            ApiRequestWarning.print_msg(error_msg=u'Warning during {}.'.format('setup of data mart'), response=response)
            return

    def update(self, db_credentials=None, schema=None):
        """
         Updates data mart configuration to work with new db instance. There is no data migration.

         :param db_credentials: describes the instance which should be connected
         :type db_credentials: dict

         :param schema: schema in your database under which the tables should be created (optional)
         :type schema: str
        """

        payload = self._prepare_db_credentials_payload(db_credentials, schema, False)

        response = requests_session.put(
            self._ai_client._href_definitions.get_data_mart_href() + '?force=true',
            json=payload,
            headers=self._ai_client._get_headers()
        )

        handle_response(200, "setup of data mart", response, False)

    def get_details(self):
        """
        Get db instance details.

        :return: db instance details
        :rtype: dict
        """

        response = requests_session.get(
            self._ai_client._href_definitions.get_data_mart_href(),
            headers=self._ai_client._get_headers()
        )

        result = handle_response(200, "getting data mart details", response, True)

        if ("internal_database" in result.keys()) and result['internal_database'] and ('._ai_client' not in str(inspect.stack()[1])):
            return handle_credentials(result)
        else:
            return result

    def get_deployment_metrics(self, subscription_uid=None, asset_uid=None, deployment_uid=None, metric_type=None):
        """
        Gets metrics. Returns metrics grouped by deployments.

        :param subscription_uid: UID of subscription for which the metrics which be prepared (optional)
        :type subscription_uid: str

        :param asset_uid: UID of asset for which the metrics which be prepared (optional)
        :type asset_uid: str

        :param deployment_uid: UID of deployment for which the metrics which be prepared (optional)
        :type deployment_uid: str

        :param metric_type: metric type which should be returned (optional)
        :type metric_type: str

        :return: metrics
        :rtype: dict
        """
        validate_type(subscription_uid, 'subscription_uid', str, False)
        validate_type(asset_uid, 'asset_uid', str, False)
        validate_type(deployment_uid, 'deployment_uid', str, False)
        validate_enum(metric_type, 'metric_type', MetricTypes, False)

        response = requests_session.get(
            self._ai_client._href_definitions.get_deployment_metrics_href(),
            headers=self._ai_client._get_headers()
        )

        details = handle_response(200, "getting deployment metrics", response, True)['deployment_metrics']

        if subscription_uid is not None:
            details = list(filter(lambda x: x['subscription']['subscription_id'] == subscription_uid, details))

        if asset_uid is not None:
            details = list(filter(lambda x: x['asset']['asset_id'] == asset_uid, details))

        if deployment_uid is not None:
            details = list(filter(lambda x: x['deployment']['deployment_id'] == deployment_uid, details))

        if metric_type is not None:
            for record in details:
                record['metrics'] = list(filter(lambda m: m['metric_type'] == metric_type, record['metrics']))

        return {'deployment_metrics': details}

    def delete(self, force=True, background_mode=False):
        """
        Delete data_mart configuration.

        :param force: force configuration deletion (optional)
        :type force: bool

        :param background_mode: if set to True, run will be in asynchronous mode, if set to False it will wait for result  (optional)
        :type background_mode: bool

        """
        validate_type(force, 'force', bool, True)
        response = requests_session.delete(
            self._ai_client._href_definitions.get_data_mart_href() + '?force=' + str(force).lower(),
            headers=self._ai_client._get_headers()
        )

        handle_response(202, "delete of data mart", response, False)

        if background_mode:
            return

        def check_state():
            try:
                details = self.get_details()
                return details['entity']['status']['state']
            except:
                return 'deleted'

        def get_result():
            return "Successfully deleted data mart", None, None

        return print_synchronous_run(
            'Waiting for end of deleting data mart',
            check_state,
            get_result=get_result,
            success_states=['deleted']
        )

    def show_issues(self):
        """
        Show existing metrics issues.
        """
        subscriptions_details = self.subscriptions.get_details()

        def get_metrics(data):
            binding_uid, subscription_uid, monitor_definition_id = data

            url = self._ai_client._href_definitions.get_ootb_metrics_get_href(
                    monitor_definition_id=monitor_definition_id,
                    result_format='samples',
                    start='2000-01-01T00:00:00.000Z',
                    end=datetime.datetime.utcnow().isoformat() + 'Z',
                    binding_id=binding_uid,
                    subscription_id=subscription_uid
                )

            response = requests_session.get(
                url,
                headers=self._ai_client._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                return []

        with ThreadPoolExecutor(max_workers=10) as executor:
            data = [(s['entity']['service_binding_id'], s['metadata']['guid'], c['monitor_definition_id']) for s in subscriptions_details['subscriptions'] for c in s['entity']['configurations']]
            results = executor.map(get_metrics, data)

        def add_issue_info(el):
            def add_metric_issue_info(m):
                m['issues'] = []
                if 'lower_limit' in m and m['lower_limit'] > m['value']:
                    m['issues'].append({
                        'type': 'lower_limit exceeded',
                        'details': 'lower_limit: {}'.format(m['lower_limit'])
                    })

                if 'upper_limit' in m and m['upper_limit'] < m['value']:
                    m['issues'].append({
                        'type': 'upper_limit exceeded',
                        'details': 'upper_limit: {}'.format(m['upper_limit'])
                    })

                return m

            el['metrics'] = [add_metric_issue_info(m) for m in el['metrics']]
            return el

        results = [add_issue_info(el2) for el in results for el2 in el]

        rows = [[r['ts'], r['subscription_id'], ', '.join(['{}: {}'.format(el['id'], el['value']) for el in r['tags']]), r['monitor_definition_id'], m['id'], m['value'], i['type'], i['details']] for r in results for m in r['metrics'] if len(m['issues']) > 0 for i in m['issues']]
        col_names = ['ts', 'subscription_id', 'tags', 'monitor_definition_id', 'metric_id', 'value', 'issue', 'additional_info']

        Table(col_names, rows, date_field_name='ts').list(title='Issues', sort_by='ts')






