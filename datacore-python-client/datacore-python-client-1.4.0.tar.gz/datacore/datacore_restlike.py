"""
Created on Sep 15, 2016

@author: Vincent Medina, EveryMundo, vincent@everymundo.com


This module represents a RESTful-like end-user interface for interacting with datacore. This is to be distinguished
from the MongoDB-like interface that is currently in development. This provides a lower-level, yet object-oriented
interface into datacore, that is geared to be imported or lend inheritance to specific applications.

TODO: support multiprocessing for large batches for improved resolution time.
"""

# Standard library imports
import collections
import datetime
import json
import logging
import os
import time
import random
from math import inf
from typing import AnyStr, Any, Dict, Generator, Iterable, Optional, Sequence, SupportsInt, Union

# Non-standard library imports
import requests

# Package imports
from datacore.types import AggregationQuery, EndpointDefinition, Header, Query, Payload
from datacore.exceptions import DatacoreException, DatacoreTypeError


# Set the constant (either from env var or from default value)
try:
    TIMEOUT = float(os.environ.get("DATACORE_TIMEOUT"))
except KeyError:
    TIMEOUT = 120.0
except TypeError:
    TIMEOUT = 120.0
except ValueError:
    logging.warning("Invalid environmental variable")
    TIMEOUT = 120.0


class Endpoints(collections.UserDict):
    """
    This class defines a simple, small object that holds the endpoints.

    This was chosen in favor of dictionaries as in previous versions of this package for greater ease of usage when
    extending the Access object in implementations that require several endpoints to datacore.
    """
    def __init__(self, read: AnyStr, write: AnyStr, bulk: AnyStr, agg: AnyStr, test_read: AnyStr, version: SupportsInt):
        """

        :param read: Read endpoint (now defaults to agg due to implementation changes)
        :param write: write endpoint
        :param bulk: bulk endpoint
        :param agg: aggregation endpoint
        :param test_read: Original 'read' endpoint. Kept for testing/debugging cases
        :param version: version number
        """
        super().__init__({"read": read, "write": write, "bulk": bulk, "agg": agg, "version": version})
        self._test_read = str(test_read)
        self._read = str(read)  # type: str
        self._write = str(write)  # type: str
        self._bulk = str(bulk)  # type: str
        self._agg = str(agg)  # type: str
        self._version = int(version)  # type: int

    def __repr__(self):
        return "(Endpoints){u}".format(u=self.data)

    def __getitem__(self, key: AnyStr) -> Any:
        """
        Returns the value from the data attribute as if it were a direct netry of the Endpoints obejct itself.
        :param key:
        :return:
        """
        try:
            return self.data[key]
        except KeyError as error:
            raise DatacoreTypeError(
                "BadItemAttribute",
                "Attempted to access nonexistant Endpoint value/attribute at key: {k}".format(
                    k=key
                )
            ) from error

    def __setitem__(self, key: AnyStr, value: Any) -> None:
        """
        This method will raise a DatacoreTypeException no matter how it is called in the event of an attempt to
        overwrite attributes.

        :param key: Dictionary key to assign the value to
        :param value: Value to assign
        :return: None
        """
        if key in {"version", "agg", "bulk", "read", "write"}:
            try:
                self.data[key] = value
                setattr(self, "_{k}".format(k=key), value)
            except Exception as error:
                raise DatacoreTypeError(
                    "InvalidKey",
                    "Bad assignment of value {v} to key {k}".format(
                        v=value,
                        k=key
                    )
                ) from error
        else:
            raise DatacoreTypeError(
                "InvalidKey",
                "Attempted to change a non-existant key {k}".format(k=key)
            )

    @property
    def read(self) -> str:
        """
        Read only access to read attribute.
        :return:
        """
        return self._read

    @property
    def write(self) -> str:
        """
        Read only access to write attribute.
        :return:
        """
        return self._write

    @property
    def bulk(self) -> str:
        """
        Read only access to bulk attribute.
        :return:
        """
        return self._bulk

    @property
    def agg(self) -> str:
        """
        Read only access to agg attribute.
        :return:
        """
        return self._agg

    @property
    def version(self) -> int:
        """
        Read only access to version atribute.
        :return:
        """
        return self._version

    @property
    def test_read(self) -> str:
        """
        Test read attribute
        :return:
        """
        return self._test_read

    @classmethod
    def from_definition(cls, endpoint_definition: EndpointDefinition, user: AnyStr):
        """
        Creates and returns an Endpoints object from the definition provided in the dictionary format.

        Requires the input of datacore username to complete the url.

        :param endpoint_definition:
        :param user:
        :return:
        """
        endpoints = Endpoints(
            read="{b}/r/{t}/{v}/{u}".format(
                b=endpoint_definition["base_read"],
                t=endpoint_definition["api_name"],
                v=endpoint_definition["api_version"],
                u=user
            ),
            write="{b}/w/{t}/{v}/{u}".format(
                b=endpoint_definition["base_write"],
                t=endpoint_definition["api_name"],
                v=endpoint_definition["api_version"],
                u=user
            ),
            bulk="{b}/w/bulk/{t}/{v}/{u}".format(
                b=endpoint_definition["base_write"],
                t=endpoint_definition["api_name"],
                v=endpoint_definition["api_version"],
                u=user
            ),
            agg="{b}/r/agg/{t}/{v}/{u}".format(
                b=endpoint_definition["base_read"],
                t=endpoint_definition["api_name"],
                v=endpoint_definition["api_version"],
                u=user
            ),
            test_read="{b}/r/{t}/{v}/{u}".format(
                b=endpoint_definition["base_read"],
                t=endpoint_definition["api_name"],
                v=endpoint_definition["api_version"],
                u=user
            ),
            version=endpoint_definition["api_version"]
        )
        return endpoints


class Access(object):
    """
    This class serves as an API/wrapper with the datacore REST API service.

    Serves as a base for any access client.

    Is used currently as a base class for table-specific implementations.
    """
    # Class constant used for pagination standards
    _PAGE_SIZE = 10000

    def __init__(self, user: AnyStr=None, secret: AnyStr=None):
        """
        The actual object itself requires the user and secret as the only parameters, which may be specified by keyword
        or by position. The credentials are used to create the appropriate https headers, and to help in the creation
        of an Endpoints object.

        The credentials are not directly mutable, though, they can be reset with a call to new_authentication().

        :param user: datacore user
        :type user: AnyStr
        :param secret: datacore secret
        :type secret: AnyStr
        """
        self._user = ''
        self._auth = ''
        # Standard headers
        self._headers = {}
        # Synchronous headers
        self._sync_headers = {}
        self.new_authentication(user, secret)

    @property
    def user(self) -> str:
        """

        :return user: username
        :rtype: str
        """
        return self._user

    @property
    def auth(self) -> str:
        """

        :return authentication: secret to access datacore endpoint
        :rtype: str
        """
        return self._auth

    @property
    def headers(self) -> Header:
        """

        :return headers: Headers to be used in datacore restful interactions
        :rtype: dict
        """
        return self._headers

    @headers.setter
    def headers(self, headers: Header) -> None:
        """

        :param headers:
        :return:
        """
        assert "Authorization" in headers.keys(), "'Authorization' must be present in the headers"
        self._headers = headers

    @property
    def sync_headers(self) -> Header:
        """
        Same as headers, but with an extra "X-Sync" key and value for synchronous posting for large or real-time
        posts.

        :return sync_headers:
        :rtype: dict
        """
        return self._sync_headers

    @sync_headers.setter
    def sync_headers(self, sync_headers: Header) -> None:
        """

        :param sync_headers:
        :type sync_headers: dict
        """
        self._sync_headers = sync_headers

    def endpoints_from_definition(self, endpoint_definition: EndpointDefinition) -> Endpoints:
        """
        Concatenates the necessary components of the EndpointDefinition to produce a dictionary of endpoints,
        whose keys are as follows: "read", "write", "bulk", "agg".

        The EndpointDefinition MUST have the following fields: "base_read", "base_write", "api_name", "api_version",
        and have none of which has a null value.

        The output Endpoints object will be in dictionary form with the values "read", "write", "bulk", "agg", and
        "version".
        :param endpoint_definition:
        :return: endpoints
        :rtype: Endpoints
        """
        return Endpoints.from_definition(endpoint_definition, self.user)

    def new_authentication(self, user: AnyStr, secret: AnyStr) -> None:
        """
        When setting new authentication for a new table, do not directly use the setters if possible. Use
        new_authentication, which will also update the headers value.

        :param user: Datacore Username
        :param secret: Datacore Secret
        :type user: AnyStr
        :type secret: AnyStr
        """
        self._user = user
        self._auth = secret
        self.headers = {
            'Content-Type': 'application-json',
            'Accept': 'application-json',
            'Authorization': self.auth
        }
        self.sync_headers = {
            'X-Sync': "True",
            'Content-Type': 'application-json',
            'Accept': 'application-json',
            'Authorization': self.auth
        }

    def number_of_entries(self, url: AnyStr, query: AggregationQuery) -> Optional[int]:
        """
        This method checks for the number of rows for a given query (if no query is passed, then this returns the
        total number of rows in the collection accessed at the endpoint given).

        If the header is returned as "undefined", then this method returns None.

        This method does not currently have support of aggregation queries.

        :param url: Read endpoint to check.
        :param query: Query to count over
        :return:
        """
        headers = self.head(
            url,
            query=query
        )
        try:
            count = headers["X-Count"] if "X-Count" in headers.keys() and headers["X-Count"] else 0
            if count.lower() == "undefined":
                return None
            return int(count)
        except Exception as error:
            logging.error("Issue returning headers and count.")
            logging.error(headers)
            raise DatacoreException("BadHeaderRetrieved", "Error retrieving headers and query counts.") from error

    def check_date(self, url: AnyStr, match: Query, group: Query, date_field: AnyStr) -> Optional[datetime.date]:
        """
        Checks for a report date (date of data, not of reporting.) If
        the date is in record, returns true, if not, returns false.

        Untested, and as of yet, unsupported for that reason.

        :param url: datacore aggregation endpoint to query form
        :type url: str
        :param match: mongodb json query match object
        :type match: dict
        :param group: mongodb json query group object
        :type group: dict
        :return date_in_datacore:
        :rtype datetime.date:
        """
        response = self.get(
            url=url,
            query=[
                match,
                group
            ],
            agg=True
        )
        logging.info(response)
        if response is None:
            logging.info("No data found")
            # Error in the pull -- bad data
            return None
        elif not response:
            logging.info("No data found-- empty response")
            # No last date
            return None
        else:
            logging.info("Data found, and is valid.")
            # We have a response that we can deal with
            date_str = response[0][date_field].replace("-", "")
            return datetime.date(
                int(date_str[0:4]),
                int(date_str[4:6]),
                int(date_str[6:8])
            )

    def _check_table(self, table_url: AnyStr, query: Query, **kwargs: Dict[str, Any]) -> bool:
        """
        Checks table at table_url for existance of data with conditions query. Returns boolean.

        :param table_url: read endpoint of  table
        :param query: query to pose (<body> in ?q=<body>)
        :arg kwargs: keyword arguments to be passed to Access.get()
        :type table_url: str
        :type query: dict
        :returns in_table:
        :rtype: bool
        """
        data = self.get(table_url, query=query, **kwargs)
        if len(data) >= 1:
            return True
        else:
            return False

    def post_lines(self, dest_url: AnyStr, data: Payload, sync=False, verbose=False) -> None:
        """Posts lines to datacore, one at a time. This is very time exhaustive,
        and is meant to be used only for purposes of debugging and testing.

        :param dest_url: datacore write endpoint
        :type dest_url: str
        :param data: data to upload
        :type data: list of dict
        :param sync: Set to true if accessing synchronous endpoint
        :type sync: bool
        :param verbose: if true, then much more visibility. Exposes data, so only use during development. Defaults to
            False
        :type verbose: bool
        :raises DatacoreException: upon failure
        """
        # Do nothing if there is no data to upload
        if not data:
            return None
        logging.info("="*75)
        logging.info("Uploading to dataCORE")
        data_set = data
        for line in data_set:
            # Line by line
            for j in range(10):
                # Incremental backoff
                try:
                    # For debugging purposes only
                    if verbose:
                        logging.info(json.dumps(line))
                    # Determine which headers should be used.
                    if not sync:
                        response = requests.post(
                            dest_url.strip(),
                            data=json.dumps(line),
                            headers=self.headers,
                            timeout=TIMEOUT
                        )
                    # Synchronous headers, keeps the connection open until the backend completes the post
                    else:
                        response = requests.post(
                            dest_url.strip(),
                            data=json.dumps(line),
                            headers=self.sync_headers,
                            timeout=TIMEOUT
                        )
                    # debugging purposes only
                    if verbose:
                        logging.info(json.loads(response.text))
                    if response.status_code in [200, 202]:
                        # Success.
                        logging.info("Sub-post uploaded.")
                        logging.info("-" * 75)
                        break
                    elif response.status_code == 413:
                        # This actually should never happen
                        raise DatacoreException(
                            '413',
                            "Sub-post still too big: {b}".format(b=response.text)
                        )
                    elif response.status_code == 502:
                        # Internet issues
                        if j == 9:
                            logging.warning("Couldn't communicate with datacore.")
                            raise DatacoreException(
                                response.status_code,
                                "Couldn't establish a connection. Please check your connection." + response.text
                            )
                        logging.info(
                            "Bad Gateway... Possible internet connection issues... will try again shortly.")
                        response = None
                    elif response.status_code >= 500:
                        # Other misc issues
                        if j == 9:
                            logging.warning("Couldn't communicate with datacore.")
                            raise DatacoreException(
                                response.status_code,
                                "Datacore API service is likely down. Please try again at another time." + response.text
                            )
                    else:
                        logging.info("Subpacket post error")
                        logging.info("Status: " + str(response.status_code))
                        logging.info(response.text)
                        raise DatacoreException(response.status_code, response.text)
                except requests.exceptions.Timeout:
                    pass
                except requests.exceptions.ConnectionError:
                    pass
                time.sleep(2 ** j + random.random())
            logging.info("Uploaded a line of data.")
            logging.info("-"*75)

    def aggregate(self, url: AnyStr, query: AggregationQuery, limit: int=None) -> Payload:
        """
        Aggregation query string uses nearly any mongodb acceptable aggregation pipeline syntax, supported as
        json-like input to be serialized for https transport.

        Similar to self.get(), but without the extra bloat for standard mongo queries.

        Also, the aggregation query does not need or require pagination mechanisms, these are handled here. Any existing
        sort, match and limit components are handled "inside" the match, sort and limit components handled here.



        :param url:
        :param query: Query to be passed over into aggregation pipeline.
        :param limit: Limit the number of results returned.
        :return:
        """
        # @TODO(Set up new aggregation method for easier requests.)
        return self.get(url, query=query, agg=True, limit=limit)

    def get(self, url: AnyStr, query: Union[AggregationQuery, Query]=None, fields: Optional[Sequence[str]]=None,
            agg: bool=False, limit: int=inf, sync: bool=False) -> Payload:
        """
        Returns dataCore results for a given period. For best results, use Access.aggregation() for deliberate
        aggregation pipeline queries.

        (New in 1.2.0: No longer supports 'sort' parameter -- Only sort in aggregation pipelines)

        (New in 1.2.0: All queries, even standard queries, will be passed through to the underlying mongodb as an
            aggregation query)

        :param url: Endpoint URL
        :type url: str
        :param fields: (optional) List of fieldnames
        :type fields: list
        :param query: Query (either aggregation or standard query match statement)
        :type query: list or dict
        :param agg: (Optional) Specifies if the query should yield
        :type agg: bool
        :param limit: Total number of desired rows
        :type limit: int
        :param sync: (Optional) Use synchronous headers. Default False.
        :type sync: bool
        :return data: data where entries are dicts. May be empty.
        :rtype Payload:

        :raises DatacoreException: when the issue is in the interaction with datacore
        """
        base = url
        if "/agg/" in base:
            agg = True
        # Output
        data = []
        # Pagination index
        page = 0
        if limit < inf:
            if limit < self._PAGE_SIZE:
                # Keep the input.
                final_limit = limit
                page_limit = self._PAGE_SIZE
            else:
                # Otherwise paginate up to the limit
                final_limit = limit % self._PAGE_SIZE if limit % self._PAGE_SIZE else self._PAGE_SIZE
                page_limit = self._PAGE_SIZE
        else:
            final_limit = self._PAGE_SIZE
            page_limit = self._PAGE_SIZE
        max_page = 1
        # While there are still pages to get
        while page < max_page:
            # Page up to (first index) or (next index)
            page += 1
            if page >= max_page:
                if limit < self._PAGE_SIZE:
                    page_limit = final_limit
                elif max_page > 1:
                    page_limit = final_limit
            if page_limit == 0:
                break
            # Reset the Query URL
            if not agg:
                # Full pagination functionality
                qurl = base + "?limit={l}&page={p}".format(l=page_limit, p=page)
            else:
                # Does not fully support pagination currently
                qurl = base + "?limit={l}".format(l=page_limit)
            if query:
                # Query parameters
                par = json.dumps(query)
                qurl += "&q={p}".format(p=par)
                # put in the query parameters
            if fields:
                # Specific fields from the table to return
                qurl += "&s="
                for col in fields:
                    # add in each of the urls
                    qurl += "{c},".format(c=col)
                # ditch that last comma
                qurl = qurl[0:len(url) - 1]
            # Loop controls, once broken, raises Exceptions
            i = 0
            # Once set to False, get loop ends
            getting = True
            # Attempt get of page
            while i <= 2 and getting:
                # Most if not all errors this method will find will occur here.
                try:
                    # First big one: perform the GET request
                    if not sync:
                        # Use standard (asyncronous) headers
                        response = requests.get(qurl.strip(), headers=self.headers, timeout=TIMEOUT)
                    else:
                        # Use synchronous headers
                        response = requests.get(qurl.strip(), headers=self.sync_headers, timeout=TIMEOUT)
                    logging.info("Datacore GET status code: {s}".format(s=response.status_code))
                    if response.status_code in [200, 202]:
                        # We got a good thing going
                        # This should be good -- try to read through
                        body = json.loads(response.text)
                        if ("count" in body.keys()) or ("numOfDocs" in body.keys()):
                            # if there is a non empty response returned
                            logging.info(
                                "Retrieved {l} rows of document from datacore".format(
                                    l=len(body["data"])
                                )
                            )
                            # Count returns the number of rows that fit the query
                            # If we have data in our query, add it to our output
                        data.extend(
                            body["data"]
                        )
                        if len(body["data"]) == 0 and page != 0:
                            # If there should be data, but nothing is returned.
                            logging.info("Zero Rows returned. Expecting {x} pages total".format(x=max_page))
                        if page == 1:
                            # Important, reset max_page if we have more rows than was given
                            if agg or limit <= self._PAGE_SIZE:
                                # Different key name for aggregation endpoint and read endpoint
                                max_page = 0
                            else:
                                # Read endpoint key
                                if int(body["count"]) > limit:
                                    if limit % page_limit == 0:
                                        max_page = limit // page_limit
                                    else:
                                        max_page = (limit // page_limit) + 1
                                else:
                                    if int(body["count"]) % page_limit == 0:
                                        max_page = int(body["count"]) // page_limit
                                    else:
                                        max_page = (int(body["count"]) // page_limit) + 1
                                # Visibility
                                logging.info("There are {x} total number of pages to process.".format(x=max_page))
                        getting = False
                        break
                    elif response.status_code == 504:
                        # When datacore backend times out before completing the transaction
                        logging.warning("STATUS 504")
                        # Bad, but can happen during periods of high traffic. Wait a moment before trying again.
                        if i < 2:
                            logging.info("This can occur during periods of high traffic. Retrying in a few seconds...")
                            i += 1
                            time.sleep(30 + random.random())
                        else:
                            raise DatacoreException('504', "Timeout.")
                    elif response.status_code >= 500:
                        # Bad, and undefined error from datacore
                        logging.warning("STATUS {r}".format(r=response.status_code))
                        if i == 0:
                            # If the error is resolvable, we wait and try again.
                            i += 1
                            time.sleep(2 ** i + random.random())
                        else:
                            # If we have already tried, then raise.
                            message = response.text if response.text else "Unknown datacore error produced status 500."
                            raise DatacoreException(response.status_code, message)
                    else:
                        logging.warning("UNKNOWN ERROR: {e}".format(e=response.text))
                        # Somehow we didn't catch it
                        if i == 0:
                            # Retry
                            time.sleep(4 + random.random())
                            i += 1
                        else:
                            # Assuming this did it
                            raise DatacoreException(response.status_code, response.text)
                except json.decoder.JSONDecodeError as error:
                    # Bad upload possibly? Probably unlikely, but possible?
                    logging.warning(
                        "Bad string returned from datacore: {t}".format(
                            t=response.text
                        )
                    )
                    raise DatacoreException.from_error(
                        error,
                        "FormatError",
                        "Data was returned in a bad formatting.",
                    )
                except requests.exceptions.ConnectionError as error:
                    if i == 2:
                        # This only happens as a client-side connection issue. Only happened once.
                        raise DatacoreException.from_error(
                            error,
                            "ConnectionError",
                            "There was an issue connecting to datacore. (Are you connected to the internet?)"
                        )
                    else:
                        # We should retry. Very likely just due to load on datacore.
                        time.sleep(8 + random.random())
                        logging.warning("Connection error during datacore pull... Retrying...")
                        time.sleep(4)
                        i += 1
                except requests.exceptions.Timeout as error:
                    if i == 2:
                        # This occurs when no data is returned
                        raise DatacoreException.from_error(
                            error,
                            "TimeoutError",
                            "Read connection timed out while attempting to connect."
                        )
                    else:
                        time.sleep(8 + random.random())
                        logging.warning("Connection error during datacore pull... Retrying...")
                        time.sleep(4)
                        i += 1
            # Remind us what page we are on currently
            logging.info("Page: {p}".format(p=page))
        return data

    def yield_get(self, url: AnyStr, query: Union[AggregationQuery, Query]=None, fields: Optional[Sequence[str]]=None,
            agg: bool=False, limit: int=None, sync: bool=False) -> Generator[Payload, None, None]:
        """
        Yields dataCore results for a given period, one page per iteration.

        (New in 1.2.0: No longer supports 'sort' parameter -- Only sort in aggregation pipelines)

        :param url: Endpoint URL
        :param fields: (optional) List of fieldnames
        :param query: Query (either aggregation or standard query match statement)
        :param limit: Total number of desired rows
        :param sync: (Optional) Use synchronous headers. Default False.
        :return data: data where entries are dicts. May be empty.

        :raises DatacoreException: when the issue is in the interaction with datacore
        """
        base = url
        if "/agg/" in base:
            raise DatacoreException(
                "AggregationNotSupported",
                "Aggregation urls are not supported in the yield_get method."
            )
        # Pagination index
        page = 0
        if limit < inf:
            if limit < self._PAGE_SIZE:
                # Keep the input.
                final_limit = limit
                page_limit = self._PAGE_SIZE
            else:
                # Otherwise paginate up to the limit
                final_limit = limit % self._PAGE_SIZE if limit % self._PAGE_SIZE else self._PAGE_SIZE
                page_limit = self._PAGE_SIZE
        else:
            final_limit = self._PAGE_SIZE
            page_limit = self._PAGE_SIZE
        max_page = 1
        # While there are still pages to get
        while page < max_page:
            # Page up to (first index) or (next index)
            page += 1
            if page >= max_page:
                if limit < self._PAGE_SIZE:
                    page_limit = final_limit
                elif max_page > 1:
                    page_limit = final_limit
            if page_limit == 0:
                break
            # Reset the Query URL
            if not agg:
                # Full pagination functionality
                qurl = base + "?limit={l}&page={p}".format(l=page_limit, p=page)
            else:
                # Does not fully support pagination currently
                qurl = base + "?limit={l}".format(l=page_limit)
            if query:
                # Query parameters
                par = json.dumps(query)
                qurl += "&q={p}".format(p=par)
                # put in the query parameters
            if fields:
                # Specific fields from the table to return
                qurl += "&s="
                for col in fields:
                    # add in each of the urls
                    qurl += "{c},".format(c=col)
                # ditch that last comma
                qurl = qurl[0:len(url) - 1]
            # Loop controls, once broken, raises Exceptions
            i = 0
            # Once set to False, get loop ends
            getting = True
            # Attempt get of page
            while i <= 2 and getting:
                # Most if not all errors this method will find will occur here.
                try:
                    # First big one: perform the GET request
                    if not sync:
                        # Use standard (asyncronous) headers
                        response = requests.get(qurl.strip(), headers=self.headers, timeout=TIMEOUT)
                    else:
                        # Use synchronous headers
                        response = requests.get(qurl.strip(), headers=self.sync_headers, timeout=TIMEOUT)
                    logging.info("Datacore GET status code: {s}".format(s=response.status_code))
                    if response.status_code in [200, 202]:
                        # We got a good thing going
                        # This should be good -- try to read through
                        body = json.loads(response.text)
                        if ("count" in body.keys()) or ("numOfDocs" in body.keys()):
                            # if there is a non empty response returned
                            logging.info(
                                "Retrieved {l} rows of document from datacore".format(
                                    l=len(body["data"])
                                )
                            )
                            # Count returns the number of rows that fit the query
                            # If we have data in our query, add it to our output
                        if len(body["data"]) == 0 and page != 0:
                            # If there should be data, but nothing is returned.
                            logging.info("Zero Rows returned. Expecting {x} pages total".format(x=max_page))
                        yield body["data"]
                        if page == 1:
                            # Important, reset max_page if we have more rows than was given
                            if agg or limit <= self._PAGE_SIZE:
                                # Different key name for aggregation endpoint and read endpoint
                                max_page = 0
                            else:
                                # Read endpoint key
                                if int(body["count"]) > limit:
                                    if limit % page_limit == 0:
                                        max_page = limit // page_limit
                                    else:
                                        max_page = (limit // page_limit) + 1
                                else:
                                    if int(body["count"]) % page_limit == 0:
                                        max_page = int(body["count"]) // page_limit
                                    else:
                                        max_page = (int(body["count"]) // page_limit) + 1
                                # Visibility
                                logging.info("There are {x} total number of pages to process.".format(x=max_page))
                        getting = False
                        break
                    elif response.status_code == 504:
                        # When datacore backend times out before completing the transaction
                        logging.warning("STATUS 504")
                        # Bad, but can happen during periods of high traffic. Wait a moment before trying again.
                        if i < 2:
                            logging.info("This can occur during periods of high traffic. Retrying in a few seconds...")
                            i += 1
                            time.sleep(30 + random.random())
                        else:
                            raise DatacoreException('504', "Timeout.")
                    elif response.status_code >= 500:
                        # Bad, and undefined error from datacore
                        logging.warning("STATUS {r}".format(r=response.status_code))
                        if i == 0:
                            # If the error is resolvable, we wait and try again.
                            i += 1
                            time.sleep(2 ** i + random.random())
                        else:
                            # If we have already tried, then raise.
                            message = response.text if response.text else "Unknown datacore error produced status 500."
                            raise DatacoreException(response.status_code, message)
                    else:
                        logging.warning("UNKNOWN ERROR: {e}".format(e=response.text))
                        # Somehow we didn't catch it
                        if i == 0:
                            # Retry
                            time.sleep(4 + random.random())
                            i += 1
                        else:
                            # Assuming this did it
                            raise DatacoreException(response.status_code, response.text)
                except json.decoder.JSONDecodeError as error:
                    # Bad upload possibly? Probably unlikely, but possible?
                    logging.warning(
                        "Bad string returned from datacore: {t}".format(
                            t=response.text
                        )
                    )
                    raise DatacoreException.from_error(
                        error,
                        "FormatError",
                        "Data was returned in a bad formatting.",
                    )
                except requests.exceptions.ConnectionError as error:
                    if i == 2:
                        # This only happens as a client-side connection issue. Only happened once.
                        raise DatacoreException.from_error(
                            error,
                            "ConnectionError",
                            "There was an issue connecting to datacore. (Are you connected to the internet?)"
                        )
                    else:
                        # We should retry. Very likely just due to load on datacore.
                        time.sleep(8 + random.random())
                        logging.warning("Connection error during datacore pull... Retrying...")
                        time.sleep(4)
                        i += 1
                except requests.exceptions.Timeout as error:
                    if i == 2:
                        # This occurs when no data is returned
                        raise DatacoreException.from_error(
                            error,
                            "TimeoutError",
                            "Read connection timed out while attempting to connect."
                        )
                    else:
                        time.sleep(8 + random.random())
                        logging.warning("Connection error during datacore pull... Retrying...")
                        time.sleep(4)
                        i += 1
            # Remind us what page we are on currently
            logging.info("Page: {p}".format(p=page))

    def post(self, url: AnyStr, data: Payload, sync: bool=False)\
            -> None:
        """Uploads to datacore staging env.

        data should be a list of dictionaries (rows), not yet 'chunked'
        to 1000-row size.

        Note that Google API python client natively handles incremental
        back-off and retries for 5XX response error codes.

        :param url: bulk Url endpoint for the post
        :type url: str
        :param data: data to upload
        :type data: list(dict)
        :param sync: (Optional) Set to True if access to synchronous endpoint is desired. False default.
        :type sync: bool
        :returns None:
        """
        logging.info("="*50)
        logging.info("Uploading to Datacore..")
        logging.info("Number of rows: {d}".format(d=len(data)))
        data_set = self.chunk(data)
        logging.info("Number of chunks: {d}".format(d=len(data_set)))
        logging.info("-"*50)
        i = 1
        dest_url = url
        if not data_set:
            # Just an extra defense in case something changes in clients.py
            return None
        for package in data_set:
            logging.info("Uploading {i} of {m} chunks to datacore ({r} rows)...".format(
                i=i,
                m=len(data_set),
                r=len(package))
            )
            for j in range(4):
                # Incremental backoff
                try:
                    if not sync:
                        response = requests.post(
                            url=dest_url.strip(),
                            data=json.dumps(package),
                            headers=self.headers,
                            timeout=TIMEOUT
                        )
                    else:
                        response = requests.post(
                            url=dest_url.strip(),
                            data=json.dumps(package),
                            headers=self.sync_headers,
                            timeout=TIMEOUT
                        )
                    logging.info("Datacore post status code: {s}".format(s=response.status_code))
                    if response.status_code in [200, 202]:
                        # There is at least some success -- it was recieved
                        logging.info("-" * 50)
                        # But we still must check that there were no issues with specific rows
                        body = json.loads(response.text)
                        if body["count"] != body["success"]:
                            # There is a discrepancy between the number of rows and number of successes
                            index = 0
                            errors = []
                            for row in body["results"]:
                                if "_id" in row.keys():
                                    # This row uploaded to processing correctly
                                    pass
                                elif not package:
                                    # If no rejection reason was given (rare)
                                    errors.append([row, data_set])
                                else:
                                    # We have an error message at the same index as its source row in the post payload
                                    try:
                                        errors.append([row, package[index]])
                                    except KeyError:
                                        # Really bad package content
                                        errors.append([row, package])
                                # Increment index
                                index += 1
                            raise DatacoreException(
                                "post_error",
                                str({"errors": errors})
                            )
                        logging.info("Packet upload successful")
                        break
                    elif response.status_code == 413:
                        logging.info("Packet too big; breaking it down and retrying.")
                        logging.info("-"*50)
                        self._sub_post(dest_url.strip(), package, sync=sync)
                        break
                    elif response.status_code == 502:
                        if j == 4:
                            logging.warning("Couldn't communicate with datacore.")
                            raise DatacoreException(
                                response.status_code,
                                "Couldn't establish a connection. Please check connection and try again." \
                                + response.text
                            )
                        logging.info("Bad Gateway... Possible internet connection issues... will try again shortly.")
                    elif response.status_code >= 500:
                        # Something really bad happened.
                        body = json.loads(response.text)
                        if "err" in body.keys():
                            if "field" in body["message"][0]:
                                # User error, easy
                                raise DatacoreException(
                                    response.status_code,
                                    body
                                )
                        else:
                            # In staging, very common -- server-side out of disk space errors
                            logging.warning("Couldn't communicate with datacore.")
                            raise DatacoreException(
                                response.status_code,
                                "Datacore API service is likely down.\n Please try again at another time.\n"
                                + "If this issue persists, please contact EveryMundo to resolve the issue. Ref: \n"
                                + response.text
                            )
                    else:
                        logging.info("Packet post error")
                        logging.info("Status: "+str(response.status_code))
                        logging.info(response.text)
                        raise(DatacoreException(response.status_code, response.text))
                except requests.exceptions.Timeout:
                    # Just try again lol
                    if j < 3:
                        logging.warning("Connection timed out. Retrying...")
                        time.sleep(8 + random.random())
                    else:
                        raise DatacoreException(
                            "TimeoutError",
                            "The connection timed out, and failed retries."
                        )
                except requests.exceptions.ConnectionError:
                    if j == 3:
                        raise DatacoreException(
                            "ConnectionError",
                            "There was an issue connecting with datacore. Are you connected to the internet?"
                        )
                # Allow a wait
                time.sleep(2**j + random.random())
            logging.info("Post chunk successful.")
            logging.info("-"*50)
            i += 1
        logging.info("Post batch successful.")
        logging.info("="*50)

    def head(self, url: AnyStr, query: Union[AggregationQuery, Query]=None) -> Header:
        """
        Performs an HTTP head request given the query onto the target endpoint url. This method is safer than _head(),
        which will never check or raise errors for unexpected response types.

        This method is decidedly lower-level than self.head(). Be sure to identify the correct query type (Query or
        AggregationQuery) depending on the endpoint that is being hit.

        :param url: endpoint url with the body already assembled
        :param query: Query for which to retrieve the response headers (Optional)
        :return headers: query headers
        """
        i = 0
        while i < 3:
            # Set up a retry loop
            query = query
            response = self._head(url, query=query)
            logging.info("Datacore HEAD request response status code {s}".format(s=response.status_code))
            if response.status_code in [200, 202]:
                # We're solid and dandy
                headers = response.headers
                return headers
            elif response.status_code == 403:
                raise DatacoreException(
                    403,
                    "Invalid credentials.",
                    response.request.url
                )
            elif response.status_code == 504:
                logging.warning("STATUS 504")
                # Bad
                if i == 0:
                    i += 1
                    time.sleep(4 + random.random())
                else:
                    raise DatacoreException(504, response.request.url)
            elif response.status_code >= 500:
                # Bad
                logging.warning("STATUS {r}".format(r=response.status_code))
                if i == 0:
                    i += 1
                    time.sleep(2 ** i + random.random())
                else:
                    raise DatacoreException(response.status_code, response.request.url)
            else:
                logging.warning("UNKNOWN ERROR: {e}".format(e=response.request.url))
                # Somehow we didn't catch it
                if i == 0:
                    # Retry
                    time.sleep(4 + random.random())
                    i += 1
                else:
                    # Assuming this did it
                    raise DatacoreException(response.status_code, response.request.url)

    def _sub_post(self, url: AnyStr, data_set: Payload, sync: bool=False) -> None:
        """If a payload (even with < 500 lines) exceeds the datacore upload
        size limit, this breaks it down and uploads the sub-chunks of the
        payload.

        :param url:
        :param data_set:
        :param sync:

        """
        logging.info("Uploading packet as subposts.")
        logging.info("-" * 75)
        data = self.chunk(data_set, chunk_size=len(data_set) // 2)
        for part in data:
            for j in range(5):
                try:
                    if not sync:
                        response = requests.post(
                            url=url.strip(),
                            data=json.dumps(part),
                            headers=self.headers,
                            timeout=TIMEOUT
                        )
                    else:
                        response = requests.post(
                            url=url.strip(),
                            data=json.dumps(part),
                            headers=self.sync_headers,
                            timeout=TIMEOUT
                        )
                    logging.info("Datacore post status code: {s}".format(s=response.status_code))
                    if response.status_code in [200, 202]:
                        # There is at least some success -- it was recieved
                        logging.info("-" * 50)
                        # But we still must check that there were no issues with specific rows
                        body = json.loads(response.text)
                        if body["count"] != body["success"]:
                            # There is a discrepancy between the number of rows and number of successes
                            index = 0
                            errors = []
                            for row in body["results"]:
                                if "_id" in row.keys():
                                    # This row uploaded to processing correctly
                                    pass
                                else:
                                    # We have an error message at the same index as its source row in the post payload
                                    errors.append([row, part[index]])
                                # Increment index
                                index += 1
                            raise DatacoreException(
                                "post_error",
                                {"errors": errors}
                            )
                        logging.info("Packet upload successful")
                        break
                    elif response.status_code == 500:
                        # Something really bad happened.
                        body = json.loads(response.text)
                        if "err" in body.keys():
                            if "field" in body["message"][0]:
                                # User error, easy
                                raise DatacoreException(
                                    response.status_code,
                                    body
                                )
                        else:
                            # In staging, very common -- server-side out of disk space errors
                            logging.warning("Couldn't communicate with datacore.")
                            raise DatacoreException(
                                response.status_code,
                                "Datacore API service is likely down.\n Please try again at another time.\n"
                                + "If this issue persists, please contact EveryMundo to resolve the issue. Ref: \n"
                                + response.text
                            )
                    elif response.status_code == 413:
                        logging.info("Sub-post still too big: attempting recursive subpost")
                        logging.info("Do not worry unless this message appears for several pages,")
                        logging.info("consecutively, without end.")
                        logging.info("-" * 75)
                        self._sub_post(url, part)
                        part = None
                        break
                    elif response.status_code == 502:
                        if j == 4:
                            logging.warning("Couldn't communicate with datacore.")
                            raise DatacoreException(
                                response.status_code,
                                "Couldn't establish a connection. Please check connection and try again." \
                                + response.text
                            )
                        logging.info("Bad Gateway... Possible internet connection issues... will try again shortly.")
                        j += 1
                    elif response.status_code >= 500:
                        if j == 4:
                            logging.warning("Couldn't communicate with datacore.")
                            raise DatacoreException(
                                response.status_code,
                                "Datacore API service is likely down. Please try again at another time." + response.text
                            )
                        else:
                            logging.info("Server issues... Retrying shortly...")
                            j += 1
                    else:
                        logging.info("Packet post error")
                        logging.info("Status: " + str(response.status_code))
                        logging.info(response.text)
                        raise (DatacoreException(response.status_code, response.text))
                except requests.exceptions.Timeout:
                    pass
                except requests.exceptions.ConnectionError:
                    # Just try again lolol
                    pass
                time.sleep(2 ** j + random.random())
        data_set = None

    def _head(self, url: str, query: Query=None):
        """
        Base header. Short wrapper for requests.head(). Does not raise any errors intentionally, nor does it catch
        raised exceptions.

        :param url: endpoint to hit
        :param query: query to use
        :return:
        """
        qurl = "{u}?q={q}".format(
            u=url,
            q=json.dumps(query)
        ) if query else url
        response = requests.head(
            qurl.strip(),
            headers=self.headers,
            timeout=TIMEOUT
        )
        return response

    def old_data(self, url: AnyStr, date_to_check: datetime.date, date_field_name: AnyStr, rules: Optional[Query]=None)\
            -> Payload:
        """

        :param url: datacore read endpoint to check
        :param date_to_check: date to pull data from
        :param date_field_name: name of date field for the table with endpoint url
        :param rules: other rules to put in place
        :type rules: dict
        :type url: str
        :type date_to_check: datetime.date
        :type date_field_name: str
        :return old_data: list whose rows are dict {col_name: value, }
        :rtype: list
        """
        query = rules if rules else {}
        query[date_field_name] = {
            "$date": date_to_check.isoformat()
        }
        old_data = self.get(
            url,
            query=query,
        )
        if old_data:
            return old_data
        else:
            return []

    @staticmethod
    def chunk(data: Payload, chunk_size=500) \
            -> Sequence[Payload]:
        """
        Breaks a collection of rows intended for bulk posting into 'chunks' of len chunk_size (or less). The upload
        size limitations of datacore lead to the necesity of using a method like this in posting batches of length
        greather than 1000, or of sufficiently large size (in bytes).

        Since this is a helper method, it does not check for invalid inputs.

        :param data: data to be uploaded
        :type data: list(dict)
        :param chunk_size: maximum length of each batch desired
        :type chunk_size: int
        :return chunks: the pieced-out partition of data
        :rtype: list(list(dict))
        """
        try:
            data = data
            # The number of chunks
            n = len(data) // chunk_size
            # Usual case: len(data) is not integer divisible by chunk_size
            if len(data) == 1:
                # Possible slicing issues.
                chunks = [data]
            elif len(data) % chunk_size > 0:
                # Produce an extra chunk, will have (len(data) % chunk_size) rows in it.
                chunks = [data[i * chunk_size:(i * chunk_size) + chunk_size] for i in range(n + 1)]
            else:
                # Produce exactly as many chunks of exactly chunk_size length
                chunks = [data[i * chunk_size:(i * chunk_size) + chunk_size] for i in range(n)]
            return chunks
        except Exception as error:
            raise DatacoreException(
                "PostPreparationFailure",
                "Failed to prepare data for posting.",
                data
            ) from error
