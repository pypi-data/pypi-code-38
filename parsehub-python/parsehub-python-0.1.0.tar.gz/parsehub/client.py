import requests


class Client(object):
    BASE_URL = 'https://www.parsehub.com/api/v2/'

    def __init__(self, api_key):
        self.api_key = api_key

    def _get(self, url, params=None, **kwargs):
        _params = {
            'api_key': self.api_key,
        }
        if params:
            _params.update(params)
        return self._request('GET', url, params=_params, **kwargs)

    def _post(self, url, data=None, **kwargs):
        _data = {
            'api_key': self.api_key,
        }
        if data:
            _data.update(data)
        return self._request('POST', url, data=_data, **kwargs)

    def _put(self, url, **kwargs):
        return self._request('PUT', url, **kwargs)

    def _delete(self, url, **kwargs):
        return self._request('DELETE', url, **kwargs)

    def _request(self, method, url, **kwargs):
        return self._parse(requests.request(method, url, timeout=60, **kwargs))

    def _parse(self, response):
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            r = response.text

        return r

    def list_projects(self, offset=None, limit=None, include_options=None):
        params = {
            'offset': offset,
            'limit': limit,
            'include_options': include_options,
        }
        return self._get(self.BASE_URL + '/projects', params=params)

    def get_project(self, project_token, offset=None, include_options=None):
        params = {
            'offset': offset,
            'include_options': include_options,
        }
        return self._get(self.BASE_URL + '/projects/' + project_token, params=params)

    def run_project(self, project_token, start_url=None, start_template=None, start_value_override=None,
                    send_email=None):
        data = {
            'start_url': start_url,
            'start_template': start_template,
            'start_value_override': start_value_override,
            'send_email': send_email,
        }
        return self._post(self.BASE_URL + '/projects/' + project_token + '/run', data=data)

    def get_run(self, run_token):
        return self._get(self.BASE_URL + '/runs/' + run_token)

    def get_run_data(self, run_token, format=None):
        params = {
            'format': format,
        }
        return self._get(self.BASE_URL + '/runs/' + run_token + '/data', params=params)

    def get_last_ready_data(self, project_token, format=None):
        params = {
            'format': format,
        }
        return self._get(self.BASE_URL + '/projects/' + project_token + '/last_ready_run/data', params=params)

    def cancel_run(self, run_token):
        return self._post(self.BASE_URL + '/runs/' + run_token + '/cancel')

    def delete_run(self, run_token):
        return self._delete(self.BASE_URL + '/runs/' + run_token)
