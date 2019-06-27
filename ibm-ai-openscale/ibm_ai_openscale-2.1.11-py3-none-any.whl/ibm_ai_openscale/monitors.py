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
from ibm_ai_openscale.utils.client_errors import *


@logging_class
class Monitors:
    """
    Manages monitors used to analyze subscribed deployments.
    """
    def __init__(self, ai_client):
        from ibm_ai_openscale.base_classes.client.client import APIClientBase
        validate_type(ai_client, "ai_client", APIClientBase, True)
        self._ai_client = ai_client

        self._list_header = ['uid', 'name', 'description', 'metrics']
        self._monitors_table_fields = ['uid', 'name', 'description', 'metrics']

    def _get_records(self):

        records = [
            [
                a['metadata']['guid'],
                a['entity']['name'],
                a['entity']['description'] if 'description' in a else None,
                [m['id'] for m in a['entity']['metrics']],
            ] for a in self.get_details()['monitor_definitions']
        ]

        return records

    def get_details(self, monitor_uid=None):
        """
        Get details of registered monitor(s).

        :param monitor_uid: uid of defined monitor (optional)
        :type monitor_uid: str

        :return: registered monitors details
        :rtype: dict

        A way you might use me is:

        >>> client.data_mart.monitors.get_details(monitor_uid)
        >>> client.data_mart.monitors.get_details()
        """

        validate_type(monitor_uid, 'monitor_uid', str, False)

        if monitor_uid is None:
            url = self._ai_client._href_definitions.get_monitor_definitions_href()
        else:
            url = self._ai_client._href_definitions.get_monitor_definition_href(monitor_uid)

        headers = self._ai_client._get_headers()
        headers["Cache-Control"] = "no-cache"

        response = requests_session.get(
                url=url,
                headers=headers
            )

        return handle_response(200, u'getting monitor details', response)

    def get_uids(self, name=None):
        """
        Get uids of defined monitors.

        :param name: name of the monitor (optional). If not provided uids for all defined monitors are returned
        :type name: list of str

        A way you might use me is:

        >>> client.data_mart.monitors.get_uids()
        """

        validate_type(name, 'name', str, False)
        monitors_details = self.get_details()

        if name is None:
            uids = [definition['metadata']['guid'] for definition in monitors_details['monitor_definitions']]
        else:
            uids = [definition['metadata']['guid'] for definition in monitors_details['monitor_definitions']
                    if definition['entity']['name'] == name]

        return uids

    def list(self, **kwargs):
        """
        List defined monitors.

        :param kwargs: filtering parameters corresponding to column names (optional)
        :type kwargs: dict

        A way you might use me is:

        >>> client.data_mart.monitors.list()
        """
        Table(self._monitors_table_fields, self._get_records()).list(filter_setup=kwargs, title="Monitors",
                                                                      column_list=self._list_header)

    def add(self, name, metrics, description=None, tags=None, parameters_schema=None):
        """
         Add custom monitor.

         :param name: name of the monitor
         :type name: str

         :param metrics: list of Metric class objects defining custom metrics
         :type metrics: Metric

         :param description: description of the monitor (optional)
         :type description: str

         :param tags: list of Tag class objects defining custom tags (optional)
         :type tags: list

         :param parameters_schema: monitor configuration parameters (optional)
         :type parameters_schema: dict


         :return: registered monitor details
         :rtype: dict

         A way you might use me is:

         >>> from ibm_ai_openscale.supporting_classes import Metric, Tag
         >>>
         >>> metrics = [Metric(name='log_loss', lower_limit=0.8), Metric(name='brier_score_loss', lower_limit=0.75)]
         >>> tags = [Tag(name='region', description='customer geographical region')]
         >>>
         >>> model_monitor = client.data_mart.monitors.add(name='model performance', metrics=metrics, tags=tags)
        """

        validate_type(name, 'name', str, True)
        validate_type(metrics, 'metrics', list, True)
        validate_type(tags, 'tags', list, False)
        validate_type(description, 'description', str, False)
        validate_type(parameters_schema, 'parameters_schema', dict, False)

        payload = {
                    "name": name,
                    "description": description if not None else '',
                    "metrics": [metric._to_json() for metric in metrics]
        }

        if tags is not None:
            payload['tags'] = [tag._to_json() for tag in tags]

        if parameters_schema is not None:
            payload['parameters_schema'] = parameters_schema

        response = requests_session.post(
            url=self._ai_client._href_definitions.get_monitor_definitions_href(),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        try:
            monitor_details = handle_response(201, 'bind instance', response, True)
            return monitor_details
        except ApiRequestWarning:
            ApiRequestWarning.print_msg(u'Warning during {}.'.format('monitor registration'), response)
            monitor_details = self.get_details(monitor_uid=self.get_uids(name=name)[0])
            return monitor_details

    def delete(self, monitor_uid):
        """
              Delete custom monitor definition.

              :param monitor_uid: monitor uid
              :type monitor_uid: str

              A way you might use me is:

              >>> client.data_mart.monitors.delete(monitor_uid)
        """

        validate_type(monitor_uid, 'monitor_uid', str, False)

        response = requests_session.delete(
            self._ai_client._href_definitions.get_monitor_definition_href(monitor_uid),
            headers=self._ai_client._get_headers()
        )

        handle_response(204, 'deletion of monitor', response, False)
