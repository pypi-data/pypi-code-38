################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from watson_machine_learning_client.libs.repo.swagger_client.apis.repository_api import RepositoryApi
from watson_machine_learning_client.libs.repo.swagger_client.rest import ApiException

import requests, certifi, os

try:
    import urllib3
except ImportError:
    raise ImportError('urllib3 is missing')

try:
    # for python3
    from urllib.parse import urlencode
except ImportError:
    # for python2
    from urllib import urlencode

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()
)


class MLRepositoryApi(RepositoryApi):
    """
    MLRepositoryApi extends RepositoryApi.
    """
    def __init__(self, api_client):
        super(MLRepositoryApi, self).__init__(api_client)

    def upload_pipeline_version(self, pipeline_id, version_id, content_stream):
        os.environ["DEPLOYMENT_PLATFORM"] = "private"
        if 'DEPLOYMENT_PLATFORM' in os.environ and os.environ['DEPLOYMENT_PLATFORM'] == 'private':
            r = requests.put('{}/v3/ml_assets/training_definitions/{}/versions/{}/content'.format(
                self.api_client.repository_path,
                pipeline_id,
                version_id
            ),
                headers=self.api_client.default_headers,
                data=content_stream,
                verify=False
            )
            if r.status_code != 200:
                raise ApiException(r.status_code, r.text)
        else:
            r = requests.put('{}/v3/ml_assets/training_definitions/{}/versions/{}/content'.format(
                self.api_client.repository_path,
                pipeline_id,
                version_id
            ),
                headers=self.api_client.default_headers,
                data=content_stream
            )
            if r.status_code != 200:
                raise ApiException(r.status_code, r.text)

    def upload_pipeline_model_version(self, model_id, version_id, content_stream, query_param=None):
        if query_param is not None:
            query_parameters = query_param
        else:
            query_parameters = {}


        if 'DEPLOYMENT_PLATFORM' in os.environ and os.environ['DEPLOYMENT_PLATFORM'] == 'private':
            r = requests.put('{}/v4/models/{}/content'.format(
                self.api_client.repository_path,
                model_id

            ),
                headers=self.api_client.default_headers,
                data=content_stream,
                params=query_parameters,
                verify=False
            )
            if (r.status_code != 200 and r.status_code !=202):
                raise ApiException(r.status_code, r.text)
        else:
            r = requests.put('{}/v4/models/{}/content'.format(
                self.api_client.repository_path,
                model_id

            ),
                headers=self.api_client.default_headers,
                data=content_stream,
                params=query_parameters
            )

            if (r.status_code != 200 and r.status_code !=202):
                raise ApiException(r.status_code, r.text)

    def get_model_size(self, content_href):
        return(self.v3_ml_assets_models_artifact_size_get(content_href))

    def get_presigned_url(self, content_href):
        return(self.v3_ml_assets_models_artifact_content_get(content_href))

    def get_async_status(self, url):
        return(self.v3_ml_assets_models_async_status_get(url))

    def download_artifact_content(self, artifact_content_href, presigned_url, accept='application/octet-stream'):
        query_params = {}
        header_params = {'Accept': accept}
        if presigned_url == 'true':
            splitOne = artifact_content_href.rsplit('?')
            splitTwo = splitOne[0].rsplit('/', 1)
            baseUrl = splitTwo[0]
            url = splitTwo[1]
            splitThree = splitOne[1].rsplit('&')
            query_params_list = {}
            for elem in splitThree:
                key_value = elem.split('=')
                query_params_list[key_value[0]]=key_value[1].replace('%2F', '/')


            artifact_content_href = (baseUrl+"/"+url)
            query_params = query_params_list
        try:
            return self.api_client.download_file(
                   artifact_content_href,
                   presigned_url,
                   query_params,
                   header_params
               )

        except ApiException as ex:
            raise ApiException(500, 'Internal server error during download content for: {}. Error message: {}'.format(artifact_content_href, ex))
        #else:
        #    raise ValueError('The artifact content href: {} is not within the client host: {}'
        #                     .format(artifact_content_href,
        #                             self.api_client.repository_path))


    def upload_function_revision(self, function_id, revision_id, content_stream):

        os.environ["DEPLOYMENT_PLATFORM"] = "private"
        if 'DEPLOYMENT_PLATFORM' in os.environ and os.environ['DEPLOYMENT_PLATFORM'] == 'private':
            r = requests.put('{}/v4/functions/{}/revisions/{}/content'.format(
                self.api_client.repository_path,
                function_id,
                revision_id
            ),
                headers=self.api_client.default_headers,
                data=content_stream,
                verify=False
            )
            if r.status_code != 200:
                raise ApiException(r.status_code, r.text)
        else:
            r = requests.put('{}/v4/functions/{}/revisions/{}/content'.format(
                self.api_client.repository_path,
                function_id,
                revision_id
            ),
                headers=self.api_client.default_headers,
                data=content_stream
            )
            if r.status_code != 200:
                raise ApiException(r.status_code, r.text)

    def upload_libraries(self, library_id, content_stream):

        if 'DEPLOYMENT_PLATFORM' in os.environ and os.environ['DEPLOYMENT_PLATFORM'] == 'private':
            r = requests.put('{}/v4/libraries/{}/content'.format(
                self.api_client.repository_path,
                library_id),
                headers=self.api_client.default_headers,
                data=content_stream,
                verify=False
            )
            if r.status_code != 200 and r.status_code !=202:
                raise ApiException(r.status_code, r.text)
        else:
            r = requests.put('{}/v4/libraries/{}/content'.format(
                self.api_client.repository_path,
                library_id),
                headers=self.api_client.default_headers,
                data=content_stream
            )
            if r.status_code != 200 and r.status_code !=202:
                raise ApiException(r.status_code, r.text)

    def upload_runtimes(self, runtimespec_id, content_stream):
        header_params = {'Content-Type': 'text/plain'}
        tmp_headers = self.api_client.default_headers.copy()
        tmp_headers.update(header_params)

        if 'DEPLOYMENT_PLATFORM' in os.environ and os.environ['DEPLOYMENT_PLATFORM'] == 'private':
            r = requests.put('{}/v4/runtimes/{}/content'.format(
                self.api_client.repository_path,
                runtimespec_id
            ),
                headers=tmp_headers,
                data=content_stream,
                verify=False
            )
            if r.status_code != 200 and r.status_code !=202:
                raise ApiException(r.status_code, r.text)
        else:
            r = requests.put('{}/v4/runtimes/{}/content'.format(
                self.api_client.repository_path,
                runtimespec_id
            ),
                headers=tmp_headers,
                data=content_stream
            )
            if r.status_code != 200 and r.status_code !=202:
                raise ApiException(r.status_code, r.text)
