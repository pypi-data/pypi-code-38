import requests
from urllib.parse import urljoin

class APIBase:
  def __init__(self, api_token, testbed=True):
    self.api_token = api_token

    if testbed:
      self.base_url = 'https://api-testbed.giftbit.com/papi/v1/'
    else:
      self.base_url = 'https://api.giftbit.com/papi/v1/'

  def _url(self, resource):
    return urljoin(self.base_url, resource)

  def _request(self, resource, method='GET', **kwargs):
    headers = {
      'Authorization': f'Bearer {self.api_token}',
      'Content-Type': 'application/json',
    }

    if kwargs.get('headers'):
      headers.update(kwargs.get('headers'))

    response = requests.request(
      method,
      self._url(resource),
      **kwargs,
      headers=headers,
    )

    response.raise_for_status()

    return response.json()

  def _make_request(self, method):
    def inner(*args, **kwargs):
      return self._request(*args, **kwargs, method=method)

    return inner

  @property
  def get(self):
    return self._make_request('GET')

  @property
  def post(self):
    return self._make_request('POST')

  @property
  def put(self):
    return self._make_request('PUT')

  @property
  def delete(self):
    return self._make_request('DELETE')
