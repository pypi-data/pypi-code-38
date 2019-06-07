import requests
from urllib.parse import urljoin

from ..exceptions import MissingFieldException, MissingReferrerException
from ..utils import validate_enum

class APIBase:
  base_url = 'https://app.viral-loops.com/api/v2/'

  def __init__(self, api_token):
    if not api_token:
      raise MissingFieldException('Missing API token argument to constructor')

    self.api_token = api_token

  def _url(self, resource):
    return urljoin(self.base_url, resource)

  @property
  def _default_body(self):
    return {
      'apiToken': self.api_token,
    }

  def _body(self, method, body=None, wrap=True):
    if method == 'GET' and not wrap:
      return body

    if not body:
      return self._default_body

    result = self._default_body.copy()

    if wrap:
      result['params'] = body
    else:
      result.update(body)

    return result

  def _request(self, resource, body=None, method=None, wrap=True):
    validate_enum(method, ['GET', 'POST'])

    querystring_params = None

    if method == 'GET':
      # For some reason the token is passed in the URL for GET requests
      #   but in an additional layer on top of the actual body for POST
      querystring_params = {'apiToken': self.api_token}

    return requests.request(
      method,
      self._url(resource),
      json=self._body(method, body=body, wrap=wrap),
      headers={
        'Content-Type': 'application/json',
      },
      params=querystring_params,
    ).json()

  def user_object(self, email, referral_code):
    result = {}

    if email:
      result['email'] = email

    if referral_code:
      result['referralCode'] = referrral_code

    return result

  def get(self, *args, **kwargs):
    return self._request(*args, **kwargs, method='GET')

  def post(self, *args, **kwargs):
    return self._request(*args, **kwargs, method='POST')
