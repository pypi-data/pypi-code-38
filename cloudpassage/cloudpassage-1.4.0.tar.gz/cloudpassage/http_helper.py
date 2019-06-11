"""HttpHelper class.  Primary-level object, facilitates
GET / POST / PUT / DELETE requests against API.
"""

from .exceptions import CloudPassageValidation
from .utility import Utility as utility
# This is for Python 3 compatibility
try:
    from urllib.parse import urlsplit
except ImportError:
    from urlparse import urlsplit


class HttpHelper(object):
    """This class handles communication with the CloudPassage API.

    When instantiating this class, pass in a :class:`cloudpassage.HaloSession`
    object (referred to here as connection, as it defines connection parameters
    for interacting with the API).

    """

    def __init__(self, connection):
        self.connection = connection

    def get(self, endpoint, **kwargs):
        """This method performs a GET against Halo's API.

        It will attempt to authenticate using the credentials (required
        to instantiate the object) if the session has either:
        1) Not been authenticated yet
        2) OAuth Token has expired

        This is a primary method, meaning it reaches out directly to the Halo
        API, and should only be utilized by secondary methods with a more
        specific purpose, like gathering events from /v1/events.  If you're
        using this method because the SDK doesn't provide a more specific
        method, please reach out to toolbox@cloudpassage.com so we can get
        an enhancement request in place for you.

        Args:
            endpoint (str): URL- everything between api.cloudpassage.com and
                any parameters to be passed. Example: /v1/events

        Keyword Args:
            params (dict): This is a dictionary object,
                represented like this: {"k1": "two,too"}
                which goes into the URL looking like this: ?k1=two,too.
                If you use a list as the value in a dictionary here, you'll get
                two k/v pairs represented in the URL and the CloudPassage API
                doesn't operate like that.  Only the last instance of that
                variable will be considered, and your results may be confusing.
                So don't do it.  Dictionaries should be {str:str}.
        """
        params = kwargs["params"] if "params" in kwargs else None
        response = self.connection.interact('get', endpoint, params)
        return response.json()

    def get_paginated(self, endpoint, key, max_pages, **kwargs):
        """This method returns a concatenated list of objects
        from the Halo API.

        It's really a wrapper for the get() method.  Pass in the
        path as with the get() method, and a maxpages number.
        Maxpages is expected to be an integer between 2 and 100

        Args:
            endpoint (str): Path for initial query
            key (str): The key in the response containing the objects of
                interest.  For instance, the /v1/events endpoint will have the
                "events" key, which contains a list of dictionary objects
                representing Halo events.
            maxpages (int): This is a number from 2-100.  More than 100 pages
                can take quite a while to return, so beyond that you should
                consider using this SDK as a component in a multi-threaded
                tool.
        Keyword Args:
            params (dict): This is a dictionary object,
                represented like this: {"k1": "two,too"}
                which goes into the URL looking like this: ?k1=two,too .
                If you use a list as the value in a dictionary here, you'll get
                two k/v pairs represented in the URL and the CloudPassage API
                doesn't operate like that.  Only the last instance of that
                variable will be considered, and your results may be confusing.
                So don't do it.  Dictionaries should be {str:str}.

        """

        max_pages_valid, pages_invalid_msg = utility.verify_pages(max_pages)
        if not max_pages_valid:
            raise CloudPassageValidation(pages_invalid_msg)
        more_pages = False
        response_accumulator = []
        if "params" in kwargs and kwargs["params"] != {}:
            initial_page = self.get(endpoint, params=kwargs["params"])
        else:
            initial_page = self.get(endpoint)
        response, next_page = self.process_page(initial_page, key)
        response_accumulator.extend(response)
        pages_parsed = 1
        if next_page is not None:
            more_pages = True
        while more_pages:
            page = self.get(next_page)
            response, next_page = self.process_page(page, key)
            response_accumulator.extend(response)
            pages_parsed += 1
            if next_page is None:
                more_pages = False
            if pages_parsed >= max_pages:
                more_pages = False
        return response_accumulator

    @classmethod
    def get_next_page_path(cls, page):
        next_page = None
        if "pagination" in page:
            if "next" in page["pagination"]:
                nextpage = page["pagination"]["next"]
                endpoint = "{}?{}".format(urlsplit(nextpage).path,
                                          urlsplit(nextpage).query)
                next_page = endpoint
        return next_page

    @classmethod
    def process_page(cls, page, key):
        """Page goes in, list data comes out."""
        response_accumulator = []
        if key not in page:
            fail_msg = ("Requested key %s not found in page"
                        % key)
            raise CloudPassageValidation(fail_msg)
        for k in page[key]:
            response_accumulator.append(k)
        next_page = cls.get_next_page_path(page)
        return response_accumulator, next_page

    def post(self, endpoint, reqbody):
        """This method performs a POST against Halo's API.

        As with the GET method, it will attempt to (re)authenticate the session
        if the key is expired or has not yet been retrieved.

        Also like the GET method, it is not intended for direct use (though
        we won't stop you).  If you need something that the SDK doesn't already
        provide, please reach out to toolbox@cloudpassage.com and let us get an
        enhancement request submitted for you.

        Args:
            endpoint (str): path component of URL
            reqbody (dict): Dictionary to be converted to JSON for insertion as
                payload for request.

        """
        return self.connection.interact("post", endpoint, None, reqbody).json()

    def put(self, endpoint, reqbody):
        """This method performs a PUT against Halo's API.

        As with the GET method, it will attempt to (re)authenticate the session
        if the key is expired or has not yet been retrieved.

        Also like the GET method, it is not intended for direct use (though
        we won't stop you).  If you need something that the SDK doesn't already
        provide, please reach out to toolbox@cloudpassage.com and let us get an
        enhancement request submitted for you.

        Args:
            endpoint (str): Path component of URL
            reqbody (dict): Dictionary to be converted to JSON for insertion
                as payload for request.

        """
        response = self.connection.interact("put", endpoint, None, reqbody)
        try:
            return response.json()
        except ValueError:  # Sometimes we don't get json back...
            return response.text

    def delete(self, endpoint, **kwargs):
        """This method performs a Delete against Halo's API.

        It will attempt to authenticate using the credentials (required
        to instantiate the object) if the session has either:

        1) Not been authenticated yet

        2) OAuth Token has expired

        This is a primary method, meaning it reaches out directly to the Halo
        API, and should only be utilized by secondary methods with a more
        specific purpose, like gathering events from /v1/events.  If you're
        using this method because the SDK doesn't provide a more specific
        method, please reach out to toolbox@cloudpassage.com so we can get
        an enhancement request in place for you.

        Args:
            endpoint (str): Path component of URL

        """
        params = kwargs["params"] if "params" in kwargs else None
        response = self.connection.interact('delete', endpoint, params)
        try:
            return response.json()
        except ValueError:  # Sometimes we don't get json back...
            return response.text
