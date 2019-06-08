"""ISOTEL Data-acqusition & Metering (IDM) Smart Gateway API
"""

from __future__ import absolute_import
import json
from uncertainties import ufloat, ufloat_fromstr

try:
    from . import _urllib3 as gateway_urllib
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
    from . import _urllib2 as gateway_urllib


def get_compatible_revision():
    return 845

def get_compatible_major_revision():
    return "1.1"

def check_compatible_version(gateVer, compVer, majorVer):
    """
    Check version compatibility
    
    :param sver: 
    :param lver: 
    :return: 
    """
    #print(str(sver) + " vs: " + str(compVer))
    if not str(gateVer).startswith(majorVer):
        raise RuntimeError('Major API versions not compatible, gateway: {} library: {}'.format(gateVer[:3], majorVer))

    rev = int(str(gateVer).split('.')[-1:][0])
    if rev != compVer  :
        raise RuntimeError('API versions not compatible, gateway: {} library: {}, {} upgrade required.'
                           .format(str(rev), str(compVer), "gateway" if rev < compVer else "library"))


def is_compatible_legacy_version(sver):
    return int(sver) <= 882


class GatewayError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Group:
    """Attach to a Group instance of an IDM Gateway,
    which group can spread in a cluster over several IDM Gateways.

    :param str gateway: gateway url, such as 'http://localhost:33000'
    :param str group: a group of devices that belong to one entity,
                      as 'me' to access local devices or 'friend1'
    :param int timeout: request timeout in seconds
    :param bool ssl_untrusted: request lets true untrusted ssl certificate
    :param str ssl_cert_file: client ssl certificate file
    :param str ssl_cert_pass: client ssl certificate password
    """

    def __init__(self, gateway='http://localhost:33000', group='me', timeout=60, ssl_untrusted=True, ssl_cert_file=None,
                 ssl_cert_pass=None, username=None, password=None, keep_alive=True, keep_alive_timeout=10):

        version = 'v1'
        self.params = {
            "gateway": gateway,
            "group": group,
            "timeout": timeout,
            "version": version,
            "ssl_untrusted": ssl_untrusted,
            "ssl_cert_file": ssl_cert_file,
            "ssl_cert_pass": ssl_cert_pass,
            "username": username,
            "password": password,
            "keep_alive": keep_alive,
            "keep_alive_timeout": keep_alive_timeout

        }
        self.gateway = gateway + '/api/' + version
        self.group = group
        self.gateway_url = self.gateway + '/' + group
        self.timeout = timeout
        self.context = None
        self.auth_header = None

        if username and password:
            self.auth_header = gateway_urllib.encode_auth_header(username, password)

        if (self.gateway_url.startswith('https://')):
            self.context = gateway_urllib.get_context(untrusted=ssl_untrusted, cert_file=ssl_cert_file,
                                                      cert_pass=ssl_cert_pass)

        self.request = gateway_urllib.RequestHandler(self.context, self.auth_header,
                                                     keep_alive=keep_alive, keep_alive_timeout=keep_alive_timeout)

        sver = self.request.get(self.gateway_url + '/version.json', self.timeout)
        check_compatible_version(sver['api'], get_compatible_revision(), get_compatible_major_revision())

    def clone(self):
        """
        Clone this Group
        :return: 
        """
        me = Group(self.params['gateway'],
                   self.params['group'],
                   timeout=self.params['timeout'],
                   ssl_untrusted=self.params['ssl_untrusted'],
                   ssl_cert_file=self.params['ssl_cert_file'],
                   ssl_cert_pass=self.params['ssl_cert_pass'],
                   username=self.params['username'],
                   password=self.params['password'],
                   keep_alive=self.params['keep_alive'],
                   keep_alive_timeout=self.params['keep_alive_timeout'])
        return me

    def get_gatewayname(self):
        """
        :returns: gateway name
        """
        return urlparse(self.gateway).netloc.split(':')[0]

    def get(self, uri, params=None):
        """
        Sends generic GET request
        
        :param str uri: resource uri
        :param dict params: HTTP request parameters
        :returns: Resource response
        :rtype: depending on resource
        :raises: HTTPError, socket.timeout
        """
        if not uri.startswith("/"):
            uri = "/" + uri
        uri = self.gateway + uri
        uri = self.add_params_to_uri(uri, params=params)

        return self.request.get(uri, self.timeout)

    def post(self, uri, data, dump_json=True):
        """
        Sends generic POST request
        
        :param str uri: resource uri
        :param dict data: Request body
        :param dump_json: convert json data to string if True
        :returns: Resource response
        :rtype: depending on resource
        :raises: HTTPError, socket.timeout
        """
        if not uri.startswith("/"):
            uri = "/" + uri
        uri = self.gateway + uri
        if dump_json:
            data = json.dumps(data)
        return self.request.post(uri, data, self.timeout)

    def delete(self, uri, params=None):
        """
        Sends generic DELETE request
        
        :param str uri: resource uri
        :param dict params: HTTP request parameters
        :returns: Resource response
        :rtype: depending on resource
        :raises: HTTPError, socket.timeout
        """
        if not uri.startswith("/"):
            uri = "/" + uri
        uri = self.gateway + uri
        uri = self.add_params_to_uri(uri, params=params)

        return self.request.delete(uri, self.timeout)

    def get_device_list(self, brand_filter=None, inactive=False):
        """Gets list of devices from gateway.

        :returns: list of devices
        :rtype: list of dicts
        :raises: HTTPError, socket.timeout
        """
        uri = self.gateway_url + ".json"
        if inactive==False:
            uri += "?active=true"
        
        devlist = self.request.get(uri, self.timeout)
        if brand_filter:
            devlist = [i for i in devlist if brand_filter in i['name'] ]

        return devlist

    def get_service_list(self):
        """Gets list of running services from gateway.

        :returns: list of devices
        :rtype: list of dicts
        :raises: HTTPError, socket.timeout
        """
        uri = self.gateway_url + "/services.json"

        return self.request.get(uri, self.timeout)

    def get_service_pin(self, name):
        """Request service PIN number required for connection
        :returns: pin number
        """
        uri = self.gateway_url + "/services/pin/" + str(name)

        return self.request.get(uri, self.timeout)

    def get_bluetooth_list(self, after=None):
        """Fetches list of devices connected through bluetooth.

        :returns: list of bluetooth devices
        :rtype: list of dicts
        :raises: HTTPError, socket.timeout
        """
        return self._get_list(self.gateway_url + "/bluetooth.json", after=after, timeout=90)

    def get_serial_list(self, after=None):
        """Fetches list of devices connected through serial ports.

        :returns: list of serial devices
        :rtype: list of dicts
        :raises: HTTPError, socket.timeout
        """
        return self._get_list(self.gateway_url + "/serial.json", after=after, timeout=30)

    def _get_list(self, uri, after=None, timeout=None):
        if after:
            uri += '?after=' + str(after)
        return self.request.get(uri, timeout if timeout else self.timeout)

    def get_connections(self):
        """
        Get connections
        
        :returns: adapter status in json form
        """
        uri = self.gateway_url + "/connections"

        return self.request.get(uri, self.timeout)

    def get_protocols(self, port):
        """
        Get protocol stack dump for given adapter/port

        :returns: adapter status in json form
        """
        uri = self.gateway_url + "/connections/" + port

        return self.request.get(uri, self.timeout)

    def get_adapter_status(self, adapter, level=None, connection='serial'):
        """
        Get connected adapter status
        
        :param str adapter: adapter preset or communication port
        :param str level: limit status results by protocol level (phy, frame, ec, trans, msg)
        :param str connection: can be (serial)
        :returns: adapter status in json form
        """
        uri = self.gateway_url + "/" + connection + "/" + adapter
        if level:
            uri += "/" + level
        return self.request.get(uri, self.timeout)

    def set_adapter_setting(self, adapter, level, data):
        """
        Set protocol parameter
        
        :param str adapter: adapter preset or communication port
        :param str level: limit status results by protocol level (phy, frame, ec, trans, msg)
        :param data: data format {"setting_name":"value"}
        :returns: operation result
        """
        uri = self.gateway_url + "/serial/" + adapter + "/" + level
        return self.request.post(uri, json.dumps(data), self.timeout)

    def get_activity(self, params=None):
        """
        Get latest gateway activity logs
        
        :param int limit: max number of returned logs
        :returns: activity logs
        :rtype: list of dicts
        :raises: HTTPError, socket.timeout
        """
        uri = self.gateway_url + '/activity.json'
        uri = self.add_params_to_uri(uri, params=params)

        return self.request.get(uri, self.timeout)

    def push_notification(self, data):
        """
        Sends generic POST request
        
        :param str uri: resource uri
        :param dict data: Request body
        :param dump_json: convert json data to string if True
        :returns: Resource response
        :rtype: depending on resource
        :raises: HTTPError, socket.timeout
        """
        uri = self.gateway_url + '/activity.json'
        return self.request.post(uri, json.dumps(data), self.timeout)

    def time(self):
        """Returns current gateway time.

        :returns: current gateway time
        :rtype: float
        """
        ts = self.request.get(self.gateway_url + '/servertime.json', self.timeout)
        try:
            return float(ts['time'])
        except:
            return None

    def version(self):
        """Returns current gateway time.

        :returns: current gateway time
        :rtype: float
        """
        return self.request.get(self.gateway_url + '/version.json', self.timeout)

    def run_script(self, script_name, phy_name):
        """Runs a script on a gateway.

        :returns: state of the script.
        """
        data = {'alias': script_name, 'phy': phy_name}
        return self.request.post(self.gateway + "/terminal/aliases",
                                 json.dumps(data), self.timeout)

    def kill_script(self):
        """Kills currently running script on a gateway.

        :returns: state of the last script
        """
        self.do('$kill')

    def do(self, command, params=''):
        """Sends a command to a gateway.
        Refer to gateway help for a list of available commands, obtainable with the $help command.

        :param str command: name of the command to be executed
        :param str params: optional parameters for the command
        """
        data = {
            'command': command,
            'parameters': params
        }
        return self.request.post(self.gateway + "/terminal/commands",
                                 json.dumps(data), self.timeout)

    def load_virtual_device(self, data, owner=None):
        """
        Create virtual device
        """
        uri = self.gateway_url + "/virtual"
        return self.request.post(uri, json.dumps(data), self.timeout)

    def remove_device(self, device):
        """
        Remove given active device from protocol stack
        """
        uri = self.gateway_url + "/" + str(device)
        return self.request.delete(uri, self.timeout)

    def get_property_list(self, identifier):
        """Retrieves a list of properties related to the device.
        :returns: list of property names
        :rtype: list
        """
        uri = self.gateway_url + "/"
        uri += identifier + "/properties" + '.json'
        return self.request.get(uri, self.timeout)

    def add_params_to_uri(self, uri, params=None):
        if params:
            uri += '?' + '&'.join({"%s=%s" % (k, v) for (k, v) in params.items()})
        return uri

    def get_property(self, identifier, prop, params=None):
        """Fetches value of *prop* property.
        The object returned has a definite structure:
        ``{ prop: {data: <value>}, time: <tstmp> }``

        :param str identifier: property group identifier
        :param str prop: name of the property
        :returns: value of the property
        :rtype: dict
        """
        prop = prop.replace(".", "/")
        uri = self.gateway_url + "/"
        uri += identifier + "/properties/" + prop + '.json'

        uri = self.add_params_to_uri(uri, params=params)

        return self.request.get(uri, self.timeout)

    def set_property(self, identifier, prop, value, append=False):
        """Sets or overwrites the value of the *prop* property with *val* value.
        The *val* passed is stored and enclosed in:
        ``{prop: {data: <val>}}``

        :param str identifier: property group identifier
        :param str prop: name
        :param str|dict|number value: value
        :returns: result with structure ``{result: Error|OK}``
        :rtype: dict
        """
        prop = prop.replace(".", "/")
        uri = self.gateway_url + "/"
        uri += identifier + "/properties/" + prop + '.json'

        if append:
            uri += '?append=true'

        return self.request.post(uri, json.dumps(value), self.timeout)

    def delete_property(self, identifier, prop, params=None):
        """Deletes the `prop` property.
        The entire property, not only its value, is removed.
        
        :param str identifier: property group identifier
        :param str prop: name
        :return: response with structure: ``{result: Error|OK}``
        :rtype: dict
        """
        prop = prop.replace(".", "/")
        uri = self.gateway_url + "/"
        uri += identifier + "/properties/" + prop + '.json'
        uri = self.add_params_to_uri(uri, params=params)

        return self.request.delete(uri, self.timeout)

    def get_arptable(self, params=None):
        """
        Get arptable
        :param params: 
        :return: 
        """

        uri = self.gateway + "/arptable"
        uri = self.add_params_to_uri(uri, params=params)

        return self.request.get(uri, self.timeout)

    def credentials(self):
        """
        Get current user credentials
        """
        uri = self.gateway + "/credentials"

        return self.request.get(uri, self.timeout)

    def get_users(self, principal_filter=None, username=None, key=None, pending=False, user_type=None):
        """
        Get user credentials according to given filters
        
        :param str filter: user principal info filter
        :param str key: user public key
        :param bool pending: pending users
        :param cred_type: credentials type, either password or certificate
        """
        uri = self.gateway + "/credentials/users"
        if pending:
            uri = uri + "/pin"
        if key:
            uri += "?key=" + str(key)
        elif principal_filter:
            uri += "?filter=" + str(principal_filter)
        elif username:
            uri += "?username=" + str(username)

        if user_type:
            uri = uri + ("&" if (key or principal_filter or username) else "?") + "type=" + str(user_type)

        return self.request.get(uri, self.timeout)

    def set_user(self, value, pending=False):
        """
        Set user credentials 
        
        :param str value: credentials json data
        
        """
        uri = self.gateway + "/credentials/users"
        if pending:
            uri = uri + "/pin"
        return self.request.post(uri, json.dumps(value), self.timeout)

    def delete_user(self, principal_filter=None, username=None, key=None, pending=False, user_type=None):
        """
        Delete user credentials
        
        :param str filter: user principal info filter
        :param str key: user public key     
        :param bool pending: pending pin users         
        :param cred_type: credentials type, either password or certificate
        """
        uri = self.gateway + "/credentials/users"
        if pending:
            uri = uri + "/pin"

        if key:
            uri += "?key=" + str(key)
        elif principal_filter:
            uri += "?filter=" + str(principal_filter)
        elif username:
            uri += "?username=" + str(username)

        if user_type:
            uri = uri + ("&" if (key or principal_filter or username) else "?") + "type=" + str(user_type)

        return self.request.delete(uri, self.timeout)

    def register_user(self, pin, name=None):
        """
        Register user credentials with PIN number 
        
        :param int pin: PIN number
        
        """
        uri = self.gateway + "/credentials/users/register"
        uri += "?pin=" + str(pin)
        if name:
            uri += "&name=" + str(name)
        return self.request.get(uri, self.timeout)

    def reset_user(self, pin):
        """
        Register user credentials with PIN number 
        
        :param int pin: PIN number
        
        """
        uri = self.gateway + "/credentials/users/reset"
        uri += "?pin=" + str(pin)

        return self.request.get(uri, self.timeout)

    def get_groups(self, name_filter=None, key=None):
        """
        Get group credentials
        
        :param str filter: group name filter
        :param str key: group key  
        """
        uri = self.gateway + "/credentials/groups"
        if key:
            uri += "?key=" + str(key)
        elif name_filter:
            uri += "?filter=" + str(name_filter)

        return self.request.get(uri, self.timeout)

    def get_group_members(self, name_filter=None, key=None):
        """
        Get group credentials
        
        :param str filter: group name filter
        :param str key: group key  
        """
        uri = self.gateway + "/credentials/groups/members"
        if key:
            uri += "?key=" + str(key)
        elif name_filter:
            uri += "?filter=" + str(name_filter)

        return self.request.get(uri, self.timeout)

    def set_group(self, value):
        """
        Set group credentials 
        
        :param str value: group json data
        """
        uri = self.gateway + "/credentials/groups"

        return self.request.post(uri, json.dumps(value), self.timeout)

    def delete_group(self, name_filter, key=None):
        """
        Delete group credentials
        
        :param str filter: group name filter
        :param str key: group key       
        """
        uri = self.gateway + "/credentials/groups"
        if key:
            uri += "?key=" + str(key)
        elif name_filter:
            uri += "?filter=" + str(name_filter)

        return self.request.delete(uri, self.timeout)


class Device:
    """Represents one Device from a Group

    :param group: an gateway.Group reference or string containing url to a gateway
    :param str name: name of the device returned by the get_device_list(),
                       such as 'device0' root designation or a full name
    :param bool unit: indicates if unit for params is to be fetched.
    :param bool advanced: fetches advanced params of the device if True
    :param bool hidden: fetches hidden params of the device if True
    :param bool development: fetches dev params of the device if True    
    """

    def __init__(self, group = None, name = None, exclude=None, unit=True, accuracy=True, advanced=False, development=False, hidden=False, brand_filter=None):

        if isinstance(group, str):
            group = Group(group)
        if not group:
            group = Group()

        if not name:
            if exclude != None:
                for dev in group.get_device_list(brand_filter):
                    onlist = False
                    for e in exclude:
                        if isinstance(e, Device):
                            if e.name == dev['name'].replace(" ", "_"):
                                onlist = True
                        elif isinstance(e, str):
                            if e.replace(" ", "_") == dev['name'].replace(" ", "_"):
                                onlist = True

                    if not onlist:
                        name = dev['name']
                        break

            else: # take first
                name = group.get_device_list(brand_filter)[0]['name']

        if name == None:
            raise GatewayError('Cannot find an active device.')

        self.group = group
        self.name = name.replace(" ", "_")
        self.unit = unit
        self.accuracy = accuracy
        self.advanced = advanced
        self.hidden = hidden
        self.development = development
        self.active = True
        self.request = group.request
        self.timestamp = 0
        try:            
            status = self.get_device_status()
            if 'name' not in status or status['name'] is None:
                raise ValueError("device " + self.name + " not yet loaded")
            self.name = str(status['name']).replace(" ", "_")
        except Exception as __:
            for i in group.get_device_list(inactive=True):
                if i['name'].replace(" ", "_") == self.name:
                    self.active = False
                    print('Warning: Device is currently inactive but have records.')
                    return
            raise ValueError("device " + self.name + " not available")

    def get_url(self):
        """
        Get device url
        """
        return self.group.gateway_url + "/" + self.name

    def time(self):
        """
        Get last updated time

        :returns: device status in json form
        """
        return self.timestamp

    def get(self, parameter='', after=None, until=None, options=False, attributes=None, args=None):
        """Retrieves one or more parameters of the device.
        If parameter is specified, then only that param info is fetched.
        Otherwise, all the params are fetched.
        A parameter can have a finite range of values, which can be fetched with ``options=True`` flag.

        :param str parameter: name of the parameter
        :param float after: wait until the given UTC time or 'now', and then issue query request
        :param float until: wait for a new sample until given UTC time, and if still not given issue query
        :param bool options: flag to determine if param options are to be fetched
        :param str attributes: fetches attributes of the passed value
        :returns: list of values
        :rtype: list
        :raises: HTTPError, socket.timeout
        """
        uri = self.group.gateway_url + "/"
        uri += self.name + "/"
        uri += parameter.replace('.', '/') + ".json"

        qp = []
        if self.unit:
            qp.append('unit=true')
        if self.accuracy:
            qp.append('accuracy=true')
        if after:
            qp.append('after=' + str(after))
        if until:
            qp.append('until=' + str(until))
        if self.advanced:
            qp.append('advanced=true')
        if self.hidden:
            qp.append('hidden=true')
        if self.development:
            qp.append('development=true')
        if options:
            qp.append('options=true')
        if attributes:
            qp.append('attributes=' + str(attributes))
        if args:
            qp.append('args=true')

        qs = '?' + '&'.join(qp) or ''
        uri += qs
        return self._parse_status(self.request.get(uri, self.group.timeout))

    def get_value(self, parameter, after=None, until=None):
        """Fetches value of the parameter from Device.

        :param str parameter: name of the parameter whose value is to be fetched
        :returns: value of the parameter
        :raises: HTTPError, socket.timeout
        """
        param = parameter.replace('.', '/')
        result = self._parse_time(self.get(param, after, until))[param.split('/')[-1]]
        try:
            return ufloat(float(result['value']), float(result['accuracy']))
        except:
            return result['value']

    def collect(self, parameter, Ts, t_start=None, N=0):
        """Collect N-values of the parameter at given time interval Ts

        :param str parameter: name of the parameter to be fetched
        :param float Ts: time interval between samples in second, or as tupple to define time interval in which sample is expected to arrive
        :param float t_start: start time of first sample to be taken in UTC or None
        :param int N: number of samples to be fetched or 0 for infinite
        :returns: yields (generates) an output to be used with isotel.idm.signal 
        """
        t0 = ts = self.group.time() if t_start == None else t_start
        unit = ''
        try:
            unit = ' [' + self.get(parameter)[parameter]['unit'] + ']'
        except:
            pass
            
        yield (('t [s]', (parameter + unit,)),)
        while True:
            if type(Ts)==tuple:
                value = self.get_value(parameter, after=ts+Ts[0], until=ts+Ts[1])
            else:
                value = self.get_value(parameter, after=ts)
            try:
                valf = value.n
            except:
                valf = float(value)

            if type(Ts)==tuple:
                ts = self.timestamp
                yield ((ts-t0, (valf,)),)
            else:
                yield ((ts-t0, (valf,)),)
                ts += Ts

            if N > 0:
                N -= 1
                if N == 0:
                    break
    
    def __getitem__(self, parameter):
        return self.get_value(parameter)

    def get_records(self, parameter, time_from=None, time_to='last',
                    limit=None, scale=None, average=None, calc=None, show=None):
        """Retrieves values from record storage.

        time_from provides filter value either as a UTC timestamp
        or as 'first' or 'start' strings to indicate that
        retrieval is to be made from first available record.

        time_to provides filter value either as a UTC timestamp
        or one of 'last' or 'end' strings to indicate that
        retrieval is to be made till last n=limit available records.

        Both scale and limit args limit the number of records being returned.
        However, limit returns records each containing ``N`` property.
        scale arg returns records, each containing ``M`` property.
        They are *mutually exclusive*; providing them both raises ``ValueError``
        with appropriate message.
        If none are provided, then gateway restricts the number of records by 100
        with each record containing ``N`` property by default.

        average arg can be used only with scale;
        providing average without scale raises ValueError.
        average specifies the number of records to be averaged on
        to determine a single scale value.
        average usage is hinted by ``SD`` property present in the response.

        :param str parameter: parameter name or stringified number
        :param int or str time_from: time from which records are to be fetched
        :param int or str time_to: time till which records are to be fetched
        :param int limit: max number of records to return with ``N`` property in each sample
        :param int scale: max number of records to return with ``M`` property in each sample
        :param int average: number of records to average on in case of scale

        :returns: list of JSON objects
        :rtype: list
        :raises: HTTPError, socket.timeout, ValueError
        """
        if limit and scale:
            raise ValueError('Provide either limit or scale arg. They are mutually exclusive.')
        if average and not scale:
            raise ValueError('average arg can only be used with scale arg.')

        uri = self.group.gateway_url + "/"
        uri += self.name + "/"
        uri += parameter.replace('.', '/') + ".json"

        qp = []
        if limit:
            qp.append('limit=' + str(limit))
        if scale:
            qp.append('scale=' + str(scale))
        if average:
            qp.append('average=' + str(average))
        if time_from:
            qp.append('from=' + str(time_from))
        if time_to:
            qp.append('to=' + str(time_to))
        if calc:
            qp.append('calc=' + str(calc))
        if show:
            qp.append('show=' + str(show))
        if self.advanced:
            qp.append('advanced=true')
        if self.development:
            qp.append('development=true')
        if self.unit:
            qp.append('unit=true')
        qs = '?' + '&'.join(qp) or ''
        uri += qs
        return self.request.get(uri, self.group.timeout)

    def get_args(self, msg):
        """
        Get arguments for given message
        """
        uri = self.group.gateway_url + "/" + self.name + "/" + str(msg)
        return self._parse_time(self.request.get(uri, self.group.timeout))

    def set_args(self, msg, data):
        """
        Set arguments for given message
        """
        uri = self.group.gateway_url + "/" + self.name + "/" + str(msg)
        return self._parse_time(self.request.post(uri, json.dumps(data), self.group.timeout))

    def set(self, parameter, data, after=None):
        """Set device variables

        :param str parameter: parameter name or stringified number
        :param str data: variable data in json format

        :returns: result of the set values in json format
        :raises: HTTPError, socket.timeout
        """
        uri = self.group.gateway_url + "/"
        uri += self.name + "/"
        uri += parameter.replace('.', '/')

        struct = data.copy()
        if after:
            struct["$after"] = after
        if self.advanced:
            struct['$advanced'] = True
        if self.development:
            struct['$development'] = True

        resp = self.request.post(uri, json.dumps(struct), self.group.timeout)
        return self._parse_status(resp)

    def set_value(self, parameter, data, after=None):
        param = parameter.replace('.', '/')
        result = self.get(param)
        token = param.split('/')[-1]
        result[token]['value'] = data
        result = self._parse_time(self.set(param, result, after))
        try:
            return result[token]['value']
        except:
            return result['status']

    def __setitem__(self, parameter, value):
        return self.set_value(parameter, value)

    def query(self, parameter):
        """
        query given parameter
        :param parameter: 
        :return: 
        """
        return self.set(parameter, {})

    def get_device_status(self):
        """
        Get connected device status
       
        :returns: device status in json form
        """
        uri = self.group.gateway_url + "/" + self.name + "/device_status"

        return self.request.get(uri, self.group.timeout)

    def get_protocols(self):
        """
        Get devices protocol tree

        :returns: protocol tree in json form
        """
        port = self.get_device_status()['port']
        return self.group.get_protocols(port)[port]

    def set_device_setting(self, data):
        """
        Set device parameter
                
        :param data: data format {"setting_name":"value"}
        :returns: operation result
        """
        uri = self.group.gateway_url + "/" + self.name + "/device_status"
        return self.request.post(uri, json.dumps(data), self.group.timeout)

    def _parse_status(self, result):

        if isinstance(result, list):
            return result

        status = 'OK'
        try:
            status = result['status']
        except:
            pass

        self._parse_time(result)
        if status.upper() not in ['OK', 'ACK']:
            report = str(status)
            if 'message' in result and result['message'] is not None:
                report = " - ".join([report, str(result['message'])])
            raise IOError(report)
        return result

    def _parse_time(self, result):
        if 'time' in result:
            self.timestamp = float(result['time'])

        return result


class Parameter:
    """Represents a Parameter of a Device

    :param Device device: a device object
    :param str parameter: parameter name or stringified number
    """

    def __init__(self, device, parameter):
        self.device = device
        self.parameter = parameter.replace('.', '/')
        self.timestamp = 0
        self.lunit = None
        self.lvalue = None
        self.struct = self.get()
        param = self.parameter.split('/')[-1]  # Only the last parameter is of interest.

        for v in self.struct.keys():
            if param in v:
                self.key = v

    def time(self):
        return self.timestamp

    def value(self):
        return self.lvalue

    def unit(self):
        return self.lunit

    def get_value(self, after=None):
        value = self._parse_time(self.get(after))
        return value[self.key]['value']

    def get_options(self):
        """Retrieves the list of possible values that the Parameter instance can possess.
        If such a range is defined, then it is returned else None is returned.

        :returns: list of option values else None
        """
        resp = self._parse_time(self.get(options=True))
        return resp[self.key].get('options', None)

    def get(self, after=None, options=False, attributes=None):
        resp = self.device.get(self.parameter, after=after,
                               options=options, attributes=attributes)
        return self._parse_status(resp)

    def get_records(self, time_from=None, time_to='last',
                    limit=None, scale=None, average=None):
        resp = self.device.get_records(self.parameter,
                                       time_from=time_from, time_to=time_to,
                                       limit=limit, scale=scale, average=average)
        return self._parse_status(resp)

    def set_value(self, new_value, after=None):

        self.struct[self.key]['value'] = new_value
        self._parse_time(self.set(self.struct, after))
        return self.value()

    def set(self, data, after=None):
        """Set values of a given parameter(s)

        :param str data: variable data in json format

        :returns: list of values
        :raises: HTTPError, socket.timeout
        """
        resp = self.device.set(self.parameter, data, after)
        return self._parse_status(resp)

    def query(self):
        """
        Send message query for given parameter
        :param data: 
        :return: 
        """
        resp = self.device.query(self.parameter)
        return self._parse_status(resp)

    def _parse_status(self, result):

        if isinstance(result, list):
            return result

        status = 'OK'
        try:
            status = result['status']
        except:
            pass
            # print("Return struct is missing status")
        self._parse_time(result)
        if status.upper() not in ['OK', 'ACK']:
            report = str(status)
            if 'message' in result and result['message'] is not None:
                report = " - ".join([report, str(result['message'])])
            raise IOError(report)

        try:
            self.lvalue = result[self.key]['value']
        except:
            self.lvalue = 'OK'

        try:
            self.lunit = result[self.key]['unit']
        except:
            self.lunit = None

        return result

    def _parse_time(self, result):

        if 'time' in result:
            self.timestamp = float(result['time'])

        return result


class Service:
    """
    An IDM Service instance
    """

    def __init__(self, gateway, service):
        self.gateway = gateway
        self.service = service
        self.service_uri = self.gateway.gateway_url + "/services/" + service
        self.timeout = self.gateway.timeout
        self.request = gateway.request

    def stop(self):
        """
        Send stop signal to service
        """
        data = {"action": "stop"}

        return self.request.post(self.service_uri, json.dumps(data), self.timeout)

    def get_service_data(self, uri):
        """
        Get service data
        
        :param str uri: service uri
        """
        uri = self.service_uri + "/" + uri
        return self.request.get(uri, self.timeout)

    def post_service_data(self, uri, data):
        """
        Post service data
    
        :param str uri: service uri
        :param str data:
        """
        uri = self.service_uri + "/" + uri
        return self.request.post(uri, json.dumps(data), self.timeout)

    def get_service_property_list(self):
        """Retrieves a list of properties related to the service.
        :returns: list of property names
        :rtype: list
        """

        uri = self.service_uri + "/properties" + '.json'
        return self.request.get(uri, self.timeout)

    def get_service_property(self, prop, params=None):
        """Fetches value of *prop* property.
        The object returned has a definite structure:
        ``{ prop: {data: <value>}, time: <tstmp> }``

        :param str identifier: property group identifier
        :param str prop: name of the property
        :returns: value of the property
        :rtype: dict
        """
        prop = prop.replace(".", "/")

        uri = self.service_uri + "/properties/" + prop + '.json'

        uri = self.gateway.add_params_to_uri(uri, params=params)
        return self.request.get(uri, self.timeout)

    def set_service_property(self, prop, value, append=False):
        """Sets or overwrites the value of the *prop* property with *val* value.
        The *val* passed is stored and enclosed in:
        ``{prop: {data: <val>}}``

        :param str identifier: property group identifier
        :param str prop: name
        :param str|dict|number value: value
        :returns: result with structure ``{result: Error|OK}``
        :rtype: dict
        """
        prop = prop.replace(".", "/")
        uri = self.service_uri + "/properties/" + prop + '.json'
        if append:
            uri += '?append=true'

        return self.request.post(uri, json.dumps(value), self.timeout)

    def delete_service_property(self, prop, params=None):
        """Deletes the `prop` property.
        The entire property, not only its value, is removed.
        
        :param str identifier: property group identifier
        :param str prop: name
        :return: response with structure: ``{result: Error|OK}``
        :rtype: dict
        """
        prop = prop.replace(".", "/")

        uri = self.service_uri + "/properties/" + prop + '.json'

        uri = self.gateway.add_params_to_uri(uri, params=params)
        return self.request.delete(uri, self.timeout)
