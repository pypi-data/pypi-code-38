# REST API MixIn
# Author: Spencer Hanson, for Swimlane
import requests
from urlparse import urljoin
import polling


class WrappedSession(requests.Session):
    """A wrapper for requests.Session to override 'verify' property, ignoring REQUESTS_CA_BUNDLE environment variable.

    This is a workaround for https://github.com/kennethreitz/requests/issues/3829 (will be fixed in requests 3.0.0)
    Code sourced from user intgr https://github.com/kennethreitz/requests/issues/3829
    """
    def merge_environment_settings(self, url, proxies, stream, verify, *args, **kwargs):
        if self.verify is False:
            verify = False

        return super(WrappedSession, self).merge_environment_settings(url, proxies, stream, verify, *args, **kwargs)


class RestAPIMixin(object):
    """
    Superclass Mix In, for custom APIs
    """

    def __init__(self, host, verify=True, proxy=None, auth=None, raise_for_status=True):
        """
        Create an API adapter class
        :param host: Full URL, including schema for the base of the API. Ex: http://google.com/v1/api
        :param verify: Optional boolean to verify SSL certificates in the requests, defaults to True
        :param proxy: Optional proxy for the requests session. A given string value will be used for both HTTP/HTTPS
        :param auth: Optional requests session authentication
        :param raise_for_status: Optional to raise for status errors after each request, defaults to True
        """

        self.host = host
        self.session = WrappedSession()
        self.session.verify = verify
        self.session.proxies = {
            "http": proxy,
            "https": proxy
        }

        self.session.auth = auth
        self.raise_for_status = raise_for_status

    def request(self, method, endpoint, **kwargs):
        """
        Make a request using the requests library, given a method, endpoint and keyword arguments
        :param method: HTTP Method to use to make the request
        :param endpoint: Endpoint to hit on the host, Ex: '/update'
        :param kwargs: Extra keyword arguments to add to the request func call
        :return: Requests response object
        """
        response = self.session.request(method, urljoin(self.host, endpoint), **kwargs)
        if self.raise_for_status:
            try:
                response.raise_for_status()
            except Exception as e:
                raise  # For debugging, put a breakpoint here
        return response

    def set_user_agent(self, bundle_name=None, bundle_version=None, swimlane_version=None, **kwargs):
        """
        Set the user agent to be Swimlane-specific
        :param bundle_name: name of the bundle making the request
        :param bundle_version: version of the bundle
        :param swimlane_version: version of Swimlane being used
        :param kwargs: additional arguments to include in the user agent
        :return: user_agent string
        """
        user_agent = ''
        if bundle_name and bundle_version:
            user_agent = '{}/{} '.format(bundle_name, bundle_version)
        if swimlane_version:
            user_agent += 'Swimlane/{} '.format(swimlane_version)
        if kwargs:
            for key, val in kwargs.items():
                user_agent += '{}/{} '.format(key, val)
        if user_agent:
            user_agent = user_agent.rstrip()
            self.session.headers.update({'User-Agent': user_agent})

    def poll_request(self, method, endpoint, step=5, timeout=60, poll_func=None, **kwargs):
        """
        :param method: HTTP Method to use in the polling requests
        :param endpoint: Endpoint to hit when polling
        :param step: Seconds between polled requests
        :param timeout: Total time of polling before the request fails
        :param poll_func: Polling function with form f(method, endpoint, kwargs) -> Truth value of the returned determines whether the polling request succeeds
        :return: result of poll_func when result is true
        """
        if not poll_func:
            def poll_func(m, e, kwa):
                result = self.request(m, e, **kwa)
                if result.status_code in (200, 201):
                    return result
                else:
                    return False

        return polling.poll(
            poll_func,
            args=[method, endpoint, kwargs],
            step=step,
            timeout=timeout
        )


class BasicRestEndpoint(RestAPIMixin):
    """
    Basic rest endpoint mix in, should be sufficient for most APIs
    """
    endpoint = ""
    kwargs = {}
    method = "GET"

    def get_endpoint(self):
        """
        Endpoint relative to the host, ie '/v2/update'
        """
        return self.endpoint

    def parse_response(self, response):
        """
        Given a requests response, process it
        :param response: Requests response object
        :return: dict or data from response
        """
        return response.json()

    def get_req_method(self):
        """
        Request method to use, valid: GET, POST, PUT, PATCH, DELETE
        :return: String for request method to use
        """
        return self.method

    def get_kwargs(self):
        """
        Optional keyword arguments to pass to the request
        :return: dict
        """
        return self.kwargs

    def execute(self):
        """
        Run the request, and return the processed response
        :return: dict
        """
        response = self.request(self.get_req_method(), self.get_endpoint(), **self.get_kwargs())
        return self.parse_response(response)


class BasicRestPaginationEndpoint(BasicRestEndpoint):
    """
    If the API has pagination support, this class makes it easy to query them all
    Just define next_page which is run until it returns None, marking the end of the pages
    each request is run through parse_response, which, by default, doesn't touch the response object
    Then combine_pages is given the list of response objects, to finalize the execution
    """

    def get_next_page(self, response):
        """
        Function to return the next endpoint to hit, given the previous response
        If it returns None, it's finished
        :param response: The previous requests response
        :return: URL to use for the next request call
        """
        raise NotImplementedError

    def combine_responses(self, results):
        """
        Take all the response objects from the pages and combine them into the final result
        :param results: List of responses
        :return: Combined responses for final output
        """
        raise NotImplementedError

    def execute(self):
        """
        Continually run the request, making sure to check if there are more pages, returns output from combine_responses
        :return:
        """
        results = []

        response = self.request(self.get_req_method(), self.get_endpoint(), **self.get_kwargs())
        results.append(response)
        next_page = self.get_next_page(response)
        while next_page:
            response = self.request(self.get_req_method(), next_page, **self.get_kwargs())
            results.append(response)
            next_page = self.get_next_page(response)

        return self.combine_responses(map(self.parse_response, results))

   
class LinkHeadersPaginationEndpoint(BasicRestPaginationEndpoint):
    def get_next_page(self, response):
        return self.parse_link(response.links)

    def parse_link(self, links):
        """
        Overridable function to parse the links from the response. Return None if it's the last page
        :param links: Dictionary of links data parsed from response
        :return: URL to use for the next request call
        """
        return links["next"]["url"]

    def combine_responses(self, results):
        raise NotImplementedError

   
class GETMixin(BasicRestEndpoint):
    """
    Mixin for GET requests
    """
    
    method = "GET"
   
    
class POSTMixin(BasicRestEndpoint):
    """
    Mixin for POST requests
    """
    
    method = "POST"


class PUTMixin(BasicRestEndpoint):
    """
    Mixin for PUT requests
    """

    method = "PUT"


class DELETEMixin(BasicRestEndpoint):
    """
    Mixin for DELETE requests
    """

    endpoint = "DELETE"


class PATCHMixin(BasicRestEndpoint):
    """
    Mixin for PATCH requests
    """

    endpoint = "PATCH"
