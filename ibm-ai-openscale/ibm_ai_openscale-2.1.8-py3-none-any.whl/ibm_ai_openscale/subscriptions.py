# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes import Table
from ibm_ai_openscale.supporting_classes import *
from ibm_ai_openscale.base_classes.assets import Asset, KnownServiceAsset
from ibm_ai_openscale.engines.watson_machine_learning import WatsonMachineLearningAsset
from ibm_ai_openscale.utils.client_errors import *
from concurrent.futures import ThreadPoolExecutor
import uuid


@logging_class
class Subscriptions:
    """
    Manages subscriptions of machine learning models deployments.
    """
    def __init__(self, ai_client):
        from ibm_ai_openscale.base_classes.client.client import APIClientBase
        validate_type(ai_client, "ai_client", APIClientBase, True)
        self._ai_client = ai_client
        self._list_header = ['uid', 'name', 'type', 'binding_uid', 'created']
        self._subscriptions_table_fields = ['uid', 'url', 'name', 'type', 'binding_uid', 'source_uid', 'source_url', 'created']

    def _get_records(self):

        records = [
            [
                a['metadata']['guid'],
                a['metadata']['url'],
                a['entity']['asset']['name'],
                a['entity']['asset']['asset_type'],
                a['entity']['service_binding_id'],
                a['entity']['asset']['asset_id'],
                a['entity']['asset']['url'] if 'url' in a['entity']['asset'] else None,
                a['metadata']['created_at']
            ] for a in self.get_details()['subscriptions']
        ]


        return records # deployments?

    def _get_binding_uid_for_subscription_uid(self, subscription_uid):
        binding_uids = [details['entity']['service_binding_id'] for details in self.get_details()['subscriptions'] if details['metadata']['guid'] == subscription_uid]

        if len(binding_uids) == 0:
            raise ClientError('Subscription with uid={} not found.'.format(subscription_uid))
        elif len(binding_uids) == 1:
            return binding_uids[0]
        else:
            raise ClientError('More than one binding for this subscription uid. Please provide \'binding_uid\'.')

    def get_details(self, subscription_uid=None, binding_uid=None):
        """
        Get details of managed asset(s).

        :param subscription_uid: uid of managed asset (optional)
        :type subscription_uid: str

        :param binding_uid: uid of binding (optional)
        :type binding_uid: str

        A way you might use me is:

        >>> client.data_mart.subscriptions.get_details(subscription_uid)
        >>> client.data_mart.subscriptions.get_details(subscription_uid, binding_uid)
        >>> client.data_mart.subscriptions.get_details()
        """
        validate_type(subscription_uid, "subscription_uid", str, False)
        validate_type(binding_uid, "binding_uid", str, False)

        if subscription_uid is None:
            if binding_uid is not None:
                response = requests_session.get(
                    self._ai_client._href_definitions.get_subscriptions_href(binding_uid),
                    headers=self._ai_client._get_headers()
                )

                return handle_response(200, 'getting subscriptions details', response, True)
            else:
                binding_uids = self._ai_client.data_mart.bindings.get_uids()

                with ThreadPoolExecutor(max_workers=10) as executor:
                    binding_uids = [(uid) for uid in binding_uids]
                    subscription_details = executor.map(lambda binding_uid: self.get_details(binding_uid=binding_uid)['subscriptions'], binding_uids)
                result = {'subscriptions': [sub_info for details in subscription_details for sub_info in details]}

                return result
        else:
            if binding_uid is None:
                binding_uid = self._get_binding_uid_for_subscription_uid(subscription_uid)

            response = requests_session.get(
                self._ai_client._href_definitions.get_subscription_href(binding_uid, subscription_uid),
                headers=self._ai_client._get_headers()
            )

            return handle_response(200, 'getting subscription details', response, True)

    def get_uids(self):
        """
        Get uids of managed subscriptions.

        :return: uids of subscriptions
        :rtype: list of strings

        A way you might use me is:

        >>> client.data_mart.subscriptions.get_uids()
        """
        return [subscription['metadata']['guid'] for subscription in self.get_details()['subscriptions']]

    def list(self, **kwargs):
        """
              List managed assets.

              :param kwargs: filtering parameters corresponding to column names (optional)
              :type kwargs: dict

              A way you might use me is:

              >>> client.data_mart.subscriptions.list()
              >>> client.data_mart.subscriptions.list(name="subscription_name")
        """
        Table(self._subscriptions_table_fields, self._get_records()).list(filter_setup=kwargs, title="Subscriptions", column_list=self._list_header)

    def get(self, subscription_uid=None, choose=None, **kwargs):
        """
            Get object to managed subscriptions.

            :param subscription_uid: managed asset uid
            :type subscription_uid: str
            :param choose: strategy of choosing result if more than one, possible values:

                - None - if more than one exception will be thrown
                - 'random' - random one will be choosen
                - 'first' - first created will be choosen
                - 'last' - last created will be choosen
            :type choose: str
            :param kwargs: are used to determine result when asset_uid is unset
            :type kwargs: dict

            :return: subscription object
            :rtype: Subscription

            A way you might use me is:

            >>> asset_1 = client.data_mart.subscriptions.get(subscription_uid)
            >>> asset_2 = client.data_mart.subscriptions.get(name='my test asset')
            >>> asset_3 = client.data_mart.subscriptions.get(name='my test asset', binding_uid=1234)
            >>> asset_4 = client.data_mart.subscriptions.get(name='my test asset', choose='last')
        """
        validate_type(subscription_uid, "subscription_uid", str, False)
        validate_type(choose, "choose", str, False)
        validate_enum(choose, "choose", Choose, False)

        constraints = kwargs

        if subscription_uid is not None:
            constraints['uid'] = subscription_uid

        table = Table(self._subscriptions_table_fields, self._get_records())
        record = table.get_record(choose, **constraints)
        binding_uid = record[table.header.index('binding_uid')]
        if subscription_uid is None:
            subscription_uid = record[table.header.index('uid')]

        subscription_url = record[table.header.index('url')]
        source_uid = record[table.header.index('source_uid')]
        source_url = record[table.header.index('source_url')]

        client = self._ai_client._clients_manager.get_client(binding_uid)
        return client.get_subscription(subscription_uid, subscription_url, source_uid, source_url, self._ai_client)

    def add(self, asset, deployment_uids=None, _training_data_schema=None, _input_data_schema=None, **kwargs):
        """
             Add asset (model or function) to managed subscriptions. By default, payload logging and performance monitoring are enabled.

             :param asset: asset object
             :type asset: Asset
             :param deployment_uids: deployment uid which should be added for this asset. Only one deployment can be pointed at this stage. You need to create separate subscription for remaining one.
             :type deployment_uids: string or None

             :return: added subscription
             :rtype: Subscription

             A way you might use me is:

             >>> from ibm_ai_openscale.engines import WatsonMachineLearningAsset
             >>>
             >>> subscription_1 = client.data_mart.subscriptions.add(WatsonMachineLearningAsset(source_uid=model_uid, prediction_column='prediction'))
             >>> subscription_2 = client.data_mart.subscriptions.add(WatsonMachineLearningAsset(source_uid=model_uid), deployment_uids='1224')
        """

        # TODO - remove at some point add_all_deployments completely
        add_all_deployments = True

        validate_type(asset, "asset", [KnownServiceAsset], True, subclass=True)

        # get client
        if asset.binding_uid is not None:
            client = self._ai_client._clients_manager.get_client(asset.binding_uid)
        elif isinstance(asset, KnownServiceAsset):
            clients = self._ai_client._clients_manager.get_all()

            def safe_contains(key):
                try:
                    return clients[key].contains_source_uid(asset.source_uid)
                except Exception as e:
                    print("Warning: Failure during checking uids for binding: {}.".format(clients[key].binding_uid))
                    return False

            clients = dict(list(filter(lambda x: x[1].service_type == asset.service_type, clients.items())))

            keys = list(filter(safe_contains, clients))

            if not keys:
                raise IncorrectValue('source_uid', 'The asset with source_uid ' + asset.source_uid + ' cannot be found.')
            else:
                client = clients[keys[0]]
        else:
            raise UnexpectedType('asset', [KnownServiceAsset], asset.__class__)

        if asset.service_type != client.service_type:
            raise IncorrectValue(str(type(asset)), 'The type of the asset is not compatible with ml engine type.')

        # use client to get artifact and deployments
        artifact = client.prepare_artifact(asset, add_all_deployments, deployment_uids)

        if asset.service_type == WatsonMachineLearningAsset.service_type \
                and any(['scikit' in f for f in artifact.frameworks]) \
                and asset.input_data_type is not None \
                and asset.input_data_type != InputDataType.STRUCTURED:
            raise ClientError("Only structured input data type is supported for scikit models.")

        # transform deployments to deployment records
        deployment_records = [d._to_json() for d in artifact.deployments]
        number_deployments = len(deployment_records)

        if number_deployments != 1:
            raise IncorrectValue('deployment_uids',
                                 'Subscription can be created for one deployment only. ' + str(number_deployments)
                                 + ' deployments are available for this asset. Specify the deployment id using deployment_uids parameter.')

        asset_properties = artifact.properties
        if _input_data_schema is not None:
            asset_properties['input_data_schema'] = _input_data_schema
        if _training_data_schema is not None:
            asset_properties['training_data_schema'] = _training_data_schema

        response = requests_session.put(
            self._ai_client._href_definitions.get_subscription_href(artifact.binding_uid, str(uuid.uuid4())),
            json={
                "asset": {
                    "asset_id": artifact.source_uid,
                    "url": artifact.source_url,
                    "name": artifact.name,
                    "asset_type": artifact.type,
                    "created_at": artifact.created
                    },
                "asset_properties": asset_properties,
                "deployments": deployment_records
            },
            headers = self._ai_client._get_headers()
        )

        try:
            details = handle_response(201, 'subscription of asset', response, True)
        except ApiRequestWarning:
            ApiRequestWarning.print_msg(u'Warning during {}.'.format('subscription of asset'), response)

            if artifact.source_uid in self.get_uids():
                return self.get(artifact.source_uid)
            else:
                return

        subscription = self.get(details['metadata']['guid'])
        subscription.payload_logging.enable()
        subscription.performance_monitoring.enable()

        return subscription

    def import_configuration(self, configuration_data, binding_uid=None):
        """
        Import subscription configuration. Creates subscription based on provided configuration.

        :param configuration_data: configuration of subscription
        :type configuration_data: dict

        :param binding_uid: uid of binding (optional if only one engine is bound)
        :type binding_uid: str

        :return: subscription object
        :rtype: Subscription

        A way you might use me is:

        >>> subscription=client.data_mart.subscriptions.import_configuration(configuration_data=subscription_config)
        """

        validate_meta_prop(configuration_data, 'asset', dict, mandatory=True)
        validate_meta_prop(configuration_data['asset'], 'asset_id', str, mandatory=True)
        subscription_uid = configuration_data['asset']['asset_id']

        validate_type(subscription_uid, "subscription_uid", str, True)

        if binding_uid is None:
            binding_uids = self._ai_client.data_mart.bindings.get_uids()
            if len(binding_uids) == 1:
                binding_uid = binding_uids[0]
            else:
                raise MissingValue('binding_uid',
                               reason='binding_uid needs to be provided.')
        else:
            validate_type(binding_uid, "binding_uid", str, False)

        response = requests_session.put(
            self._ai_client._href_definitions.get_subscription_configuration_href(binding_uid, subscription_uid),
            json=configuration_data,
            headers=self._ai_client._get_headers()
        )

        try:
            response_text = handle_response(200, 'importing subscription configuration', response, True)

            for action in response_text:
                if action['success'] is False:
                    raise ApiRequestFailure('Unable to create subscription from configuration.', response, reason=action['message'])
        except ApiRequestWarning:
            ApiRequestWarning.print_msg(u'Warning during {}.'.format('subscription configuration import. Subscription already exists.'), response)

        return self.get(subscription_uid)

    def export_configuration(self, subscription_uid, binding_uid=None):
        """
        Get subscription configuration.

        :param subscription_uid: subscription uid
        :type subscription_uid: str

        :param binding_uid: uid of binding (optional)
        :type binding_uid: str


        :return: subscription configuration
        :rtype: dict

        A way you might use me is:

        >>> configuration=client.data_mart.subscriptions.export_configuration(subscription_uid)
        """
        
        validate_type(subscription_uid, "subscription_uid", str, True)
        validate_type(binding_uid, "binding_uid", str, False)

        if binding_uid is None:
            binding_uid = self._get_binding_uid_for_subscription_uid(subscription_uid)

        response = requests_session.get(
            self._ai_client._href_definitions.get_subscription_configuration_href(binding_uid, subscription_uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, 'getting subscription configuration', response, True)

    def delete(self, subscription_uid, binding_uid=None, force=True):  # TODO also should have background_mode param
        """
              Unsubscribe asset.

              :param subscription_uid: subscription uid
              :type subscription_uid: str

              :param binding_uid: uid of binding (optional)
              :type binding_uid: str

              :param force: force unbinding (optional)
              :type force: bool

              A way you might use me is:

              >>> client.data_mart.subscriptions.delete(subscription_uid)
        """
        validate_type(subscription_uid, "subscription_uid", str, True)
        validate_type(binding_uid, "binding_uid", str, False)

        if binding_uid is None:
            binding_uid = self._get_binding_uid_for_subscription_uid(subscription_uid)

        response = requests_session.delete(
            self._ai_client._href_definitions.get_subscription_href(binding_uid, subscription_uid) + '?force=' + str(force).lower(),
            headers=self._ai_client._get_headers()
        )

        handle_response(202, 'deletion of asset', response, False)

        start_time = time.time()
        elapsed_time = 0
        timeout = 120
        while True and elapsed_time < timeout:
            try:
                self.get_details(subscription_uid=subscription_uid)
                elapsed_time = time.time() - start_time
                time.sleep(10)
            except ClientError as ex:
                if "not found" in str(ex.error_msg):
                    return
                else:
                    raise ex
