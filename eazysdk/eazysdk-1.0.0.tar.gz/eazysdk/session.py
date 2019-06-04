import requests
from requests import session
from .settings import Settings as s
from .exceptions import UnsupportedHTTPMethodError
from .exceptions import InvalidEnvironmentError
from json import JSONDecodeError


class Session:
    def __init__(self):
        """
        Creates a new instance of the EazySDK session
        """
        # The environment used for requests sent to EazyCustomerManager
        self.environment = None
        # The client settings for the client, stores API and client code
        self.client_settings = None
        # The client code stored within client_settings
        self.client_code = None
        # The API key stored within client_settings
        self.api_key = None
        # The base URL for requests sent to EazyCustomerManager
        self.base_url = None
        # The headers sent along with the request to EazyCustomerManager
        self.headers = None
        # The parameters sent with the request to EazyCustomerManager
        self.params = None
        # The endpoint (x.com{{/end/point}} of the request URL
        self.endpoint = None
        # The HTTP method of the request sent to EazyCustomerManager
        self.method = None
        # The URL to be sent to EazyCustomerManager
        self.request_url = None
        self.session = session()

    def request(self, method, endpoint, headers=None, params=None):
        """
        Create a request to be sent to EazyCustomerManager

        :Required args:
        - method - The HTTP method of the request to be sent to
            EazyCustomerManager
        - endpoint - The path of the request URL

        :Optional args:
        - headers - Headers sent to EazyCustomerManager along with the
            request
        - params - Parameters to be sent to EazyCustomerManager with the
            request


        :Example:
        request('GET', 'customers')

        :Returns:
        request JSON objects
        """
        # Get the current environment from the settings file
        self.environment = s.current_environment['env'].lower()

        # Ensure the environment is valid
        acceptable_environments = {
            'ecm3',
            'sandbox',
        }
        if self.environment not in acceptable_environments:
            raise InvalidEnvironmentError(
                '%s is not a valid environment. The acceptable environments'
                ' are \n- sandbox - A server for testing the functionality of'
                ' EazyCustomerManager\n - ecm3 - The production'
                ' EazyCustomerManager environment' % self.environment
            )
        # Get the client settings from the settings file
        elif self.environment == 'ecm3':
            self.client_settings = s.ecm3_client_details
        else:
            self.client_settings = s.sandbox_client_details

        # Get the client code from the settings file
        self.client_code = self.client_settings['client_code']
        # Get the API key from the settings file
        self.api_key = self.client_settings['api_key']
        # The base URL for all requests to EazyCustomerManager
        self.base_url = 'https://%s.eazycollect.co.uk/api/v3/client/%s/' \
                        % (self.environment, self.client_code)
        # we need to instantiate the headers object
        self.headers = headers
        # Get the API key from the settings file
        self.api_key = self.client_settings['api_key']
        # Create the headers object
        self.headers = {
            'apiKey': self.api_key,
            'Content-Length': '0',
        }

        # Get the endpoint and append it to the base URL
        self.request_url = self.base_url + endpoint
        # Get the HTTP method of the request
        self.method = method
        # Raise an error if an unsupported HTTP method is used
        if method not in (['GET', 'POST', 'PATCH', 'DELETE']):
            raise UnsupportedHTTPMethodError(
                '%s is not a supported HTTP method when communicating'
                ' with EazyCustomerManager. Valid methods are GET,'
                ' POST, PATCH and DELETE' % method
            )

        # Get the params if there are any
        self.params = self.params
        request_call = getattr(requests, self.method.lower())
        response = request_call(
            self.request_url,
            params=self.params,
            headers=self.headers,
        )
        try:
            if response.text:
                response_json = response.text
            else:
                response_json = {}
        except JSONDecodeError:
            response_json = {}
        return response_json

    def get(self):
        """
        Send a GET request to EazyCustomerManager
        """
        return self.request('GET', self.endpoint, self.params)

    def post(self):
        """
        Send a POST request to EazyCustomerManager
        """
        return self.request('POST', self.endpoint, self.params)

    def patch(self):
        """
        Send a PATCH request to EazyCustomerManager
        """
        return self.request('PATCH', self.endpoint, self.params)

    def delete(self):
        """
        Send a DELETE request to EazyCustomerManager
        """
        return self.request('DELETE', self.endpoint, self.params)
