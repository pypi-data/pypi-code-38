#!/usr/local/bin/python3
"""
The spectre module is used to make access to Lumeta's Spectre API
a little easier (Lumeta and Spectre are trademarks of the Lumeta Corporation).
"""
import requests
import urllib3
import spectreapi
import json
from typing import Optional, List, Iterable


class Server:
    """
    A Server is used to make API Calls to a Lumeta Spectre(r) server
    It's not meant to be instantiated directly, use one of its
    subclasses (e.g. UsernameServer or APIKeyServer) based on how we're
    authenticating to the Spectre Command Center in question.
    """

    def __init__(self, server, page_size=500, verify_cert=False):
        self.session = requests.Session()
        self.session.verify = False
        self.page_size = page_size
        self.url = "https://" + server + "/api/rest/"
        self._host = server
        self._version = None
        self.session.timeout = 1
        if verify_cert is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @property
    def host(self) -> str:
        '''Returns the server name (or IP) specified in the constructor'''
        return self._host

    @property
    def name(self) -> str:
        '''Returns the server name '''
        return self._name


    @property
    def version(self) -> str:
        '''Returns the version of the Spectre server we're talking with (as reported by that server)'''
        return self._version

    def close(self):
        '''
        It's not _required_ to close a Server, but if you don't, you might
        hold tcp sockets open (the underlying requests and urllib3 modules
        hold them for keepalive purposes)
        '''
        self.session.close()

    def post(self, api, **kargs) -> requests.Response:
        """
        This method POSTs to the Spectre API
        >>> import spectreapi
        >>> s = spectreapi.UsernameServer("6hour", "admin", "admin")
        >>> data = '''
        ...         [{
        ...             "@class":"zone",
        ...             "name":"Twilight",
        ...             "description": "Zone to Test Scanning",
        ...             "organization":{"id":1, "name":"Test Organization"}
        ...         }]
        ...         '''
        >>> r = s.post("zone", data=data)
        >>> r.json()['status']
        'SUCCESS'
        """
        if 'headers' not in kargs:
            kargs['headers'] = {'Accept': 'json:pretty', 'Content-Type': 'application/json'}

        result = self.session.post(self.url + api, **kargs)
        if not result.ok:
            raise APIException(result)
        return result

    def raw_post(self, api, **kargs) -> requests.Response:
        """
        This method POSTs to the Spectre API but _doesn't_ set any headers.
        This is so we can make things like file uploads work (because they seem to 
        require XML for reasons as yet mysterious.  For example, this is currently the only
        way to setup the SNMP server:
            data='''<set_snmpd_request>
                <SNMPDaemonConfig>
                    <readOnlyCommunity>
                        <community>public</community>
                    </readOnlyCommunity>
                </SNMPDaemonConfig>
            </set_snmpd_request>
            '''

        server.raw_post('management/snmpd',data=data,headers={'Content-Type':'application/xml'})
        """
        result = self.session.post(self.url + api, **kargs)
        if not result.ok:
            raise APIException(result)
        return result

    def put(self, api, **kargs):
        '''Method PUTs through to the server'''

        if 'headers' not in kargs:
            kargs['headers'] = {'Accept': 'json:pretty', 'Content-Type': 'application/json'}

        result = self.session.put(self.url + api, **kargs)
        if not result.ok:
            raise APIException(result)
        return result


    def delete(self, api, **kargs) -> requests.Response:
        '''Method sends DELETEs through to server'''

        if 'headers' not in kargs:
            kargs['headers'] = {'Accept': 'json:pretty', 'Content-Type': 'application/json'}

        result = self.session.delete(self.url + api, **kargs)
        if not result.ok:
            raise APIException(result)
        return result


    def getpage(self, api, params=None, page=0, headers=None) -> requests.Response:
        """
        This private method is in place to handle the actual
        fetching of GET API calls
        """
        if params is None:
            params = {"query.pagesize": self.page_size}

        if headers is None:
            headers = {'Accept': 'json:pretty', 'Content-Type': 'application/json'}

        params["query.pagesize"] = self.page_size
        params["query.page"] = page
        results = self.session.get(self.url+api, params=params, timeout=120, headers=headers)
        if not results.ok:
            print(results.text)
            raise APIException(results)
        return results

    def get(self, api, params=None) -> Iterable['spectreapi.Response']:
        """
        Use this method to GET results from an API call and produce
        an iterable response
        >>> import spectreapi
        >>> s=spectreapi.UsernameServer('6hour','admin','admin')
        >>> s.get('zone').results.json()
        {'@class': 'apiresponse', 'status': 'SUCCESS', 'method': 'ZoneManagement.getZones', 'total': 2, 'results': [{'@class': 'zone', 'id': 2, 'name': 'Twilight', 'description': 'Zone to Test Scanning'}, {'@class': 'zone', 'id': 1, 'name': 'Zone1', 'description': 'Default Zone'}]}
        >>> r = s.get('zone')
        >>> for z in r:
        ...     print(z)
        ...
        {'@class': 'zone', 'id': 2, 'name': 'Twilight', 'description': 'Zone to Test Scanning'}
        {'@class': 'zone', 'id': 1, 'name': 'Zone1', 'description': 'Default Zone'}
        >>>
        """
        return spectreapi.Response(self, api, params)

    def query(self, api="zonedata/devices"):
        """
        >>> import spectreapi
        >>> s=spectreapi.UsernameServer('6hour','admin','admin')
        >>> q=s.query().filter('zone.id',2).detail('Attributes')
        >>> for d in q.run():
        ...     print(d)
        """
        return Query(self, api)

    def get_zones(self) -> List['spectreapi.Zone']:
        '''Returns all the Zones configured on the server'''
        zones = []
        result = self.get('zone')
        for zone in result:
            zones.append(spectreapi.Zone(zone['id'], zone['name'], zone['description'], server=self))

        return zones

    def get_zone_by_name(self, name) -> Optional['spectreapi.Zone']:
        '''Returns the Zone configured on the server named <name> (if present)'''
        results = self.get('zone')
        for zone in results:
            if zone['name'] == name:
                return spectreapi.Zone(zone['id'], zone['name'], zone['description'], server=self)

        return None

    def get_or_create_zone(self, name, description="Test Zone", organization={"id": 1, "name": "Test Organization"}):
        zone = self.get_zone_by_name(name)
        if zone:
            return zone
        data = [{ "@class" : "zone",
            "name" : name,
            "description" : description,
            "organization": organization
            }]
        r = self.post("zone", data=json.dumps(data))
        zone = self.get_zone_by_name(name)
        return zone


    def get_collectors(self) -> List['spectreapi.Collector']:
        '''Returns the Collectors configured on the server'''
        collectors = []
        results = self.get('zone/collector')
        for collector in results:
            collectors.append(spectreapi.Collector(
                collector['id'],
                collector['uuid'],
                collector['name'],
                spectreapi.Zone(collector['zone']['id'], collector['zone']['name']),
                server=self,
            ))
        return collectors

    def get_collector_by_name(self, name) -> Optional['spectreapi.Collector']:
        '''Returns the Collector configured on the server named <name> (if present)'''
        results = self.get('zone/collector')
        for collector in results:
            if collector['name'] == name:
                return spectreapi.Collector(
                    collector['id'],
                    collector['uuid'],
                    collector['name'],
                    spectreapi.Zone(collector['zone']['id'], collector['zone']['name']),
                    server=self,
                )

        return None

class Response():
    """
    This class is used to present the results of a "GET" API call
    It handles iterating through the results and fetching pages as
    needed from the server
    """

    def __init__(self, server, api, params):
        self.server = server
        self.api = api
        self.params = params
        self.page = 0
        self.page_line = 0
        self.results = self.server.getpage(api, params, page=self.page)

        if "total" in self.results.json():
            self.total = self.results.json()['total']
        else:
            self.total = 1

    def rewind(self):
        '''Used to reset state after iterating over results'''
        self.page = 0
        self.page_line = 0
        self.results = self.server.getpage(
            self.api, self.params, page=self.page)

    def __iter__(self):
        return self

    def __next__(self):
        '''This facilitates being able to iterate over the results of a GET'''
        if self.page * self.server.page_size + self.page_line == self.total:
            self.rewind()
            raise StopIteration

        if self.page_line < self.server.page_size:
            self.page_line += 1
            try:
                return self.results.json()['results'][self.page_line - 1]
            except IndexError:
                self.rewind()
                raise StopIteration  # This could happen if the underlying query shrinks under us

        else:
            self.page_line = 1
            self.page += 1
            self.results = self.server.getpage(
                self.api, self.params, page=self.page)
            try:
                return self.results.json()['results'][0]
            except IndexError:
                self.rewind()
                raise StopIteration  # This could happen if the underlying query shrinks under us

    @property
    def result(self):
        """Return result 0 (the only result for singletons"""
        return self.values()[0]

    def value(self):
        """Return value 0 (the only value for singletons (replaces result())"""
        return self.results.json()['results'][0]

    def values(self):
        """Return the values from the API call"""
        return self.results.json()['results']

class APIKeyServer(Server):
    """
    An APIKeyServer is a Server that uses authentication via API key.
    You get an API key from the CLI via the "user key new <username>" command
    """

    def __init__(self, server, api_key, page_size=500, verify_cert=False):
        """
        APIKeyServer(server,api_key) where
        server is the Spectre server you're connecting to and
        api_key is the API key you've generated

        >>> import spectreapi
        >>> s = APIKeyServer("i3", api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"+ \
                ".eyJkYXRlIjoxNTI0NDI5ODU2NTA2LCJ1c2VyIjoiYWRtaW4ifQ.KEaRBjPVMns"+ \
                "dPAG6l3oinHOjPFAfsfUkgOs0YKyhwds")
        >>> r = s.getpage("system/information")
        >>> r.json()['status']
        'SUCCESS'
        >>> r.json()['results'][0]['name']
        'i3'
        """
        super().__init__(server, page_size=page_size, verify_cert=verify_cert)
        self.session.headers['Authorization'] = "Bearer " + api_key
        results = self.get("system/information")
        self._version = results.result['version']
        self._name = results.json()['results'][0]['name']

class UsernameServer(Server):
    """
    This Server uses username and password authentication for the initial
    request, and then uses a session cookie from there out
    """
    def __init__(self, server, username, password, page_size=500, verify_cert=False):
        super().__init__(server, page_size=page_size, verify_cert=verify_cert)
        auth = requests.auth.HTTPBasicAuth(username, password)
        headers = {'Accept': 'json:pretty', 'Content-Type': 'application/json'}
        results = requests.get(self.url + "system/information", headers=headers, verify=False, auth=auth)
        self._version = results.json()['results'][0]['version']
        self._name = results.json()['results'][0]['name']
        self.session.cookies = results.cookies

class Query:
    """
    Class to store the state around a GET request from a server
    >>> import spectreapi
    >>> s=spectreapi.UsernameServer('6hour','admin','admin')
    >>> q=s.query().filter('zone.id',2).detail('Attributes')
    >>> for d in q.run():
    ...     print(d)
    """
    def __init__(self, server, api) -> 'spectreapi.Query':
        """
        Setup a query for a server with api call <api>
        """
        self.server = server
        self.api = api
        self.params = {}

    def run(self) -> Iterable['spectreapi.Response']:
        """
        Go ahead and execute the query, return the results
        """
        return self.server.get(self.api, self.params)

    def filter(self, name, value=True) -> 'spectreapi.Query':
        """
        Add a filter to the query
        """
        self.params['filter.' + name] = value
        return self

    def detail(self, name) -> 'spectreapi.Query':
        """
        Add a detail to the query
        """
        self.params['detail.' + name] = True
        return self


class SpectreException(Exception):
    '''General Base Spectre exception'''
    pass

class NoServerException(SpectreException):
    '''Specter exception for when we call a
    method that needs a server but we don't have one'''
    pass

class InvalidArgument(SpectreException):
    '''Invalid argument'''
    pass

class APIException(SpectreException):
    '''We got an exception back from the Spectre API call'''
    def __init__(self, request):
        super().__init__()
        self.request = request

    def __str__(self):
        return self.request.text
