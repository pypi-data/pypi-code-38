# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes import Table
from ibm_ai_openscale.base_classes.instances import AIInstance
from ibm_ai_openscale.utils import *
from concurrent.futures import ThreadPoolExecutor


@logging_class
class Bindings:
    """
    Manage bindings of machine learning services.
    """
    def __init__(self, ai_client):
        from ibm_ai_openscale.base_classes.client.client import APIClientBase
        validate_type(ai_client, "ai_client", APIClientBase, True)

        self._logger = logging.getLogger(__name__)
        self._ai_client = ai_client

    def add(self, name, instance):
        """
            Add binding.

            :param name: name of binding
            :type name: str

            :param instance: service instance type with authentication information (dict)
            :type instance: object

            :return: binding uid
            :rtype: str

            A way you might use me is:

            >>> client.data_mart.bindings.add("my wml instance", WatsonMachineLearningInstance(credentials))
        """
        validate_type(name, "name", str, True)
        validate_type(instance, "instance", AIInstance, True, subclass=True)
        request_headers = None

        payload = {
            "name": name,
            "service_type": instance._service_type,
            "instance_id": instance.source_uid,
        }

        if 'request_headers' in instance.credentials:
            request_headers = instance.credentials['request_headers']
            del instance.credentials['request_headers']

            payload["credentials"] = instance.credentials
            payload["request_headers"] = request_headers
        # TODO to remove this check
        elif 'header' in instance.credentials:
            request_headers = instance.credentials['header']
            del instance.credentials['header']

            payload["credentials"] = instance.credentials
            payload["request_headers"] = request_headers
        else:
            payload["credentials"] = instance.credentials

        response = requests_session.post(
            self._ai_client._href_definitions.get_service_bindings_href(),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        try:
            details = handle_response(201, 'bind instance', response, True)
        except ApiRequestWarning:
            ApiRequestWarning.print_msg(u'Warning during {}.'.format('bind instance'), response)
            return instance.source_uid

        return details['metadata']['guid']

    def list(self, **kwargs):
        """
             List bindings.

             :param kwargs: filtering parameters corresponding to column names (optional)
             :type kwargs: dict

             A way you might use me is:

             >>> client.data_mart.bindings.list()
             >>> client.data_mart.bindings.list(name='my binding')
             >>> client.data_mart.bindings.list(service_type='watson_machine_learning')
         """

        records = [[c['metadata']['guid'], c['entity']['name'], c['entity']['service_type'],
                    c['metadata']['created_at']] for c in self.get_details()['service_bindings']]
        table = Table(['uid', 'name', 'service_type', 'created'], records)
        table.list(filter_setup=kwargs, title="Service bindings")

    def delete(self, binding_uid, force=True, background_mode=False):
        """
             Delete binding.

             :param binding_uid: uid of managed binding
             :type binding_uid: str

             :param force: force unbinding (optional)
             :type force: bool

             :param background_mode: if set to True, run will be in asynchronous mode, if set to False it will wait for result  (optional)
             :type background_mode: bool

             A way you might use me is:

             >>> client.data_mart.bindings.delete(binding_uid)
         """
        validate_type(binding_uid, "binding_uid", str, True)
        validate_type(force, "force", bool, True)

        response = requests_session.delete(
            self._ai_client._href_definitions.get_service_binding_href(binding_uid) + '?force=' + str(force).lower(),
            headers=self._ai_client._get_headers()
        )

        handle_response(202, 'unbinding of instance', response, False)

        if background_mode:
            return

        def check_state():
            try:
                details = self.get_details(binding_uid)
                return details['entity']['status']['state']
            except:
                return 'deleted'

        def get_result():
            return "Successfully deleted binding", None, None

        return print_synchronous_run(
            'Waiting for end of deleting binding {}'.format(binding_uid),
            check_state,
            get_result=get_result,
            success_states=['deleted']
        )

    def get_details(self, binding_uid=None):
        """
              Get details of managed binding(s).

              :param binding_uid: uid of managed binding (optional)
              :type binding_uid: str

              A way you might use me is:

              >>> client.data_mart.bindings.get_details(binding_uid)
              >>> client.data_mart.bindings.get_details()
        """
        validate_type(binding_uid, "binding_uid", str, False)

        if binding_uid is None:
            response = requests_session.get(
                self._ai_client._href_definitions.get_service_bindings_href(),
                headers=self._ai_client._get_headers()
            )

            return handle_response(200, 'getting bindings details', response, True)
        else:
            response = requests_session.get(
                self._ai_client._href_definitions.get_service_binding_href(binding_uid),
                headers=self._ai_client._get_headers()
            )

            return handle_response(200, 'getting binding details', response, True)

    def get_uids(self):
        """
              Get uids of managed bindings.

              :return: bindings uids
              :rtype: list of str

              A way you might use me is:

              >>> client.data_mart.bindings.get_uids()
        """
        return [binding['metadata']['guid'] for binding in self.get_details()['service_bindings']]

    def list_assets(self, **kwargs):
        """
              List available assets. Available assets are assets that were not subscribed yet.

              :param kwargs: filtering parameters corresponding to column names (optional)
              :type kwargs: dict

              A way you might use me is:

              >>> client.data_mart.bindings.list_assets()
              >>> client.data_mart.bindings.list_assets(source_uid='123')
        """
        binding_uid = kwargs['binding_uid'] if 'binding_uid' in kwargs else None

        records = [[c['source_uid'], c['name'], c['created'], c['type'],
                    ','.join(c['frameworks']), c['binding_uid'],
                    c['is_subscribed']] for c in self.get_asset_details(binding_uid=binding_uid)]
        table = Table(['source_uid', 'name', 'created', 'type', 'frameworks', 'binding_uid', 'is_subscribed'], records)
        table.list(filter_setup=kwargs, title="Available assets")

    def list_asset_deployments(self, **kwargs):
        """
              List available asset deployments. Available asset deployments are deployments that were not subscribed yet.

              :param kwargs: filtering parameters corresponding to column names (optional)
              :type kwargs: dict

              A way you might use me is:

              >>> client.data_mart.bindings.list_asset_deployments()
              >>> client.data_mart.bindings.list_asset_deployments(deployment_uid='123')
        """
        binding_uid = kwargs['binding_uid'] if 'binding_uid' in kwargs else None

        records = [[c['deployment_id'], c['name'], c['created_at'], c['deployment_type'],
                    c['parent_asset_uid'], c['is_subscribed']] for c in self.get_asset_deployment_details(binding_uid=binding_uid)]
        table = Table(['deployment_uid', 'name', 'created', 'type', 'parent_asset_uid', 'is_subscribed'], records)
        table.list(filter_setup=kwargs, title="Available asset deployments")

    def get_asset_details(self, binding_uid=None):
        """
              Get details of available assets (models and functions). Available asset deployments are deployments that were not subscribed yet.

              :param binding_uid: uid of binding (optional)
              :type binding_uid: str

              :return: asset details
              :rtype: dict or list of dicts

              A way you might use me is:

              >>> client.data_mart.bindings.get_asset_details()
        """
        if binding_uid is not None:
            clients = [self._ai_client._clients_manager.get_client(binding_uid=binding_uid)]
        else:
            clients = self._ai_client._clients_manager.get_all().values()

        mapping = {s['entity']['asset']['asset_id']: s['metadata']['guid'] for s in self._ai_client.data_mart.subscriptions.get_details()['subscriptions']}

        def get_asset_json(asset, is_subscribed):
            asset = asset.to_json()
            asset['is_subscribed'] = is_subscribed
            return asset

        def safe_get_artifacts(client):
            try:
                return client.get_artifacts()
            except Exception as e:
                print("Warning: Failure during getting artifacts for binding: {}.".format(client.binding_uid), e)
                return []

        with ThreadPoolExecutor(max_workers=10) as executor:
            clients = [(client) for client in clients]
            clients_artifacts = executor.map(safe_get_artifacts, clients)

        assets = [get_asset_json(asset, asset.source_uid in mapping) for artifacts in clients_artifacts for asset in
                  artifacts]

        return assets

    def get_asset_deployment_details(self, binding_uid=None):
        """
              Get details of available asset deployments (for models and functions). Available asset deployments are deployments that were not subscribed yet.

              :param binding_uid: uid of binding (optional)
              :type binding_uid: str

              :return: asset deployment details
              :rtype: dict or list of dicts

              A way you might use me is:

              >>> client.data_mart.bindings.get_asset_deployment_details()
        """
        if binding_uid is not None:
            clients = [self._ai_client._clients_manager.get_client(binding_uid=binding_uid)]
        else:
            clients = self._ai_client._clients_manager.get_all().values()

        subscribed_deployments = [deployment['deployment_id']
                                  for subscription in self._ai_client.data_mart.subscriptions.get_details()['subscriptions']
                                  for deployment in subscription['entity']['deployments']]

        def get_deployment_json(deployment, parent_asset_uid, is_subscribed):
            deployment = deployment._to_json()
            deployment['parent_asset_uid'] = parent_asset_uid
            deployment['is_subscribed'] = is_subscribed
            return deployment

        def safe_get_artifacts(client):
            try:
                return client.get_artifacts()
            except Exception as e:
                print("Warning: Failure during getting artifacts for binding: {}.".format(client.binding_uid), e)
                return []

        with ThreadPoolExecutor(max_workers=10) as executor:
            clients = [(client) for client in clients]
            assets = [asset for result in executor.map(safe_get_artifacts, clients) for asset in result]

        return [get_deployment_json(deployment, asset.source_uid, deployment.guid in subscribed_deployments) for asset in assets for deployment in asset.deployments]

    def get_asset_uids(self):
        """
              Get uids of available assets.

              :return: asset uids
              :rtype: list of str

              A way you might use me is:

              >>> client.data_mart.bindings.get_asset_uids()
        """
        return [asset['source_uid'] for asset in self.get_asset_details()]

    def get_native_engine_client(self, binding_uid):
        """
        Returns native client for engine instance added to AIOS.

        :param binding_uid: UID of binding for which the client should be obtained
        :type: str

        :return: native client for particular binding
        :rtype: specific for particular engine, e.g for wml it will be WatsonMachineLearningAPIClient

        """
        client = self._ai_client._clients_manager.get_client(binding_uid)

        try:
            return client._get_native_client()
        except:
            raise ClientError('Getting native client for this binding instance is not possible.')

