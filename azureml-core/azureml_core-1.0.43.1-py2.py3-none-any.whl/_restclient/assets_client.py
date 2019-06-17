# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Access AssetsClient"""

import datetime
import requests

from .workspace_client import WorkspaceClient
ASSETS_SERVICE_VERSION = "2018-11-19"


class AssetsClient(WorkspaceClient):
    """Asset client class"""
    def get_rest_client(self, user_agent=None):
        """get service rest client"""
        return self._service_context._get_assets_restclient(user_agent=user_agent)

    def create_asset(self, model_name, artifact_values, metadata_dict,
                     project_id=None, run_id=None, tags=None, properties=None):
        """
        :param model_name:
        :type model_name str:
        :param artifact_values:
        :type artifact_values list:
        :param metadata_dict:
        :type metadata_dict dict:
        :param project_id:
        :type project_id str:
        :param run_id:
        :type run_id str:
        :param tags:
        :type tags dict:
        :param properties:
        :type properties dict:
        :return:
        """
        create_asset_host = self.get_cluster_url()
        create_asset_url = "{}/api/{}/assets?api-version={}".format(
            create_asset_host,
            self.get_workspace_uri_path().strip("/"),
            ASSETS_SERVICE_VERSION)

        created_time = str(datetime.datetime.utcnow())
        payload = {"name": model_name,
                   "description": "{} saved during run {} in project {}".format(model_name,
                                                                                run_id,
                                                                                project_id),
                   "artifacts": artifact_values,
                   "kvTags": tags,
                   "properties": properties,
                   "runid": run_id,
                   "projectid": project_id,
                   "meta": metadata_dict,
                   "CreatedTime": created_time}
        headers = self.auth.get_authentication_header()
        self._logger.debug("Create Asset url: {}\nPayload: {}".format(
            create_asset_url, str(payload)))
        result = requests.post(create_asset_url, json=payload, headers=headers)
        if result.status_code != 200:
            message = "Create asset request error. Code: {}\n: {}".format(result.status_code,
                                                                          result.text)
            self._logger.error(message)
            raise Exception(message)
        return result

    def get_assets_by_run_id_and_name(self, run_id, name):
        """
        Get assets filtered on run ID and asset name
        :param run_id: the run ID to filter on
        :type run_id: string
        :param name: the asset name to filter on
        :type name: string
        :return: a list of assets which have run IDs and names matching the params
        :rtype: list[~_restclient.models.Asset]
        """
        return self._execute_with_workspace_arguments(self._client.asset.list_query,
                                                      runid=run_id,
                                                      name=name).value

    def get_asset_by_id(self, asset_id):
        """
        Get events of a run by its run_id
        :rtype: ~_restclient.models.Asset or ~msrest.pipeline.ClientRawResponse
        """
        return self._execute_with_workspace_arguments(self._client.asset.query_by_id,
                                                      id=asset_id)

    def list_assets(self):
        """
        Get events of a run by its run_id
        :rtype: ~_restclient.models.Asset or ~msrest.pipeline.ClientRawResponse
        """
        return self._execute_with_workspace_arguments(self._client.asset.list_query)
