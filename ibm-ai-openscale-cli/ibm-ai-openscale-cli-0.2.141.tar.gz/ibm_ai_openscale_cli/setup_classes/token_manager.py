# coding=utf-8
import requests
import time
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from retry import retry
from ibm_ai_openscale_cli.utility_classes.utils import get_error_message

DEFAULT_IAM_URL = 'https://iam.bluemix.net/identity/token'
DEFAULT_UAA_URL = 'https://login.ng.bluemix.net/UAALoginServerWAR/oauth/token'
CONTENT_TYPE = 'application/x-www-form-urlencoded'
ACCEPT = 'application/json'
DEFAULT_IAM_AUTHORIZATION = 'Basic Yng6Yng='
DEFAULT_UAA_AUTHORIZATION = 'Basic Y2Y6'
IAM_TOKEN_GRANT_TYPE = 'urn:ibm:params:oauth:grant-type:apikey'
UAA_TOKEN_GRANT_TYPE = 'password'
UAA_USERNAME = 'apikey'
IAM_TOKEN_RESPONSE_TYPE = 'cloud_iam'
IAM_REFRESH_TOKEN_GRANT_TYPE = 'refresh_token'

logger = FastpathLogger(__name__)
class TokenManager(object):
    def __init__(self, apikey=None, access_token=None, url=None, iam_token=True):
        self.apikey = apikey
        self.user_access_token = access_token
        self.iam_token = iam_token
        self.url = url if url else (
            DEFAULT_IAM_URL if iam_token else DEFAULT_UAA_URL)
        self.token_info = {
            'access_token': None,
            'refresh_token': None,
            'token_type': None,
            'expires_in': None,
            'expiration': None,
        }

    def _request(self, method, url, headers=None, params=None, data=None, accept_json=True, **kwargs):
        response = requests.request(method=method, url=url,
                                    headers=headers, params=params,
                                    data=data, **kwargs)
        if 200 <= response.status_code <= 299:
            return response.json() if accept_json else response.text

        raise Exception(get_error_message(response))

    @retry(tries=5, delay=1, backoff=2)
    def get_token(self):
        """
        The source of the token is determined by the following logic:
        1. If user provides their own managed access token, assume it is valid and send it
        2. If this class is managing tokens and does not yet have one, make a request for one
        3. If this class is managing tokens and the token has expired refresh it. In case the refresh token is expired, get a new one
        If this class is managing tokens and has a valid token stored, send it
        """
        logger.log_debug('TokenManager.get_{}_token()'.format('iam' if self.iam_token else 'uaa'))
        if self.user_access_token:
            return self.user_access_token
        elif not self.token_info.get('access_token'):
            token_info = self._request_token()
            self._save_token_info(token_info)
            return self.token_info.get('access_token')
        elif self._is_token_expired():
            if self._is_refresh_token_expired():
                token_info = self._request_token()
            else:
                token_info = self._refresh_token()
            self._save_token_info(token_info)
            return self.token_info.get('access_token')
        else:
            return self.token_info.get('access_token')

    def _request_token(self):
        """
        Request a token using an API key
        """
        headers = {
            'Content-type': CONTENT_TYPE,
            'accept': ACCEPT,
            'Authorization': DEFAULT_IAM_AUTHORIZATION if self.iam_token else DEFAULT_UAA_AUTHORIZATION
        }
        data = dict()
        if self.iam_token:
            data.update({
                'grant_type': IAM_TOKEN_GRANT_TYPE,
                'apikey': self.apikey,
                'response_type': IAM_TOKEN_RESPONSE_TYPE
            })
        else:
            data.update({
                'username': UAA_USERNAME,
                'password': self.apikey,
                'grant_type': UAA_TOKEN_GRANT_TYPE
            })

        response = self._request(
            method='POST',
            url=self.url,
            headers=headers,
            data=data)
        return response

    def _refresh_token(self):
        """
        Refresh a token using a refresh token
        """
        headers = {
            'Content-type': CONTENT_TYPE,
            'accept': ACCEPT,
            'Authorization': DEFAULT_IAM_AUTHORIZATION if self.iam_token else DEFAULT_UAA_AUTHORIZATION
        }
        data = {
            'grant_type': IAM_REFRESH_TOKEN_GRANT_TYPE if self.iam_token else UAA_TOKEN_GRANT_TYPE,
            'refresh_token': self.token_info.get('refresh_token')
        }
        response = self._request(
            method='POST',
            url=self.url,
            headers=headers,
            data=data)
        return response

    def set_access_token(self, access_token):
        """
        Set a self-managed access token.
        The access token should be valid and not yet expired.
        """
        self.user_access_token = access_token

    def set_apikey(self, apikey):
        """
        Set the api key
        """
        self.apikey = apikey

    def _is_token_expired(self):
        """
        Check if currently stored token is expired.
        Using a buffer to prevent the edge case of the
        oken expiring before the request could be made.
        The buffer will be a fraction of the total TTL. Using 80%.
        """
        fraction_of_ttl = 0.8
        time_to_live = self.token_info.get('expires_in')
        expire_time = self.token_info.get('expiration')
        refresh_time = expire_time - (time_to_live * (1.0 - fraction_of_ttl))
        current_time = int(time.time())
        return refresh_time < current_time

    def _is_refresh_token_expired(self):
        """
        Used as a fail-safe to prevent the condition of a refresh token expiring,
        which could happen after around 30 days. This function will return true
        if it has been at least 7 days and 1 hour since the last token was set
        """
        if self.token_info.get('expiration') is None:
            return True

        seven_days = 7 * 24 * 3600
        current_time = int(time.time())
        new_token_time = self.token_info.get('expiration') + seven_days
        return new_token_time < current_time

    def _save_token_info(self, token_info):
        """
        Save the response from the service request to the object's state.
        """
        self.token_info = token_info
