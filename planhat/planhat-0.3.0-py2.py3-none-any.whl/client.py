import requests
import requests.auth


class Planhat(object):

    def __init__(self, api_url, tenant_id, api_token):
        self._api_url = api_url
        self._tenant_id = tenant_id
        self._api_token = api_token

        self._session = requests.Session()
        self._session.auth = BearerAuth(api_token)

    def request(self, method, route, **kwargs):
        """Wrapper around requests session"""
        response = self._session.request(
            method,
            self._api_url + '/' + route,
            **kwargs
        )
        response.raise_for_status()
        return response

    def get_companies(self, segment_id=None):
        """https://docs.planhat.com/#companies"""
        return self.request('GET', 'companies', params={
            's': segment_id
        }).json()

    def get_users(self):
        """https://docs.planhat.com/#team"""
        return self.request('GET', 'users').json()

    def get_user(self, user_id):
        """https://docs.planhat.com/#team"""
        return self.request('GET', 'users/{}'.format(user_id)).json()

    def get_segments(self):
        return self.request('GET', 'segments').json()


class BearerAuth(requests.auth.AuthBase):

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer {}'.format(self.token)
        return request
