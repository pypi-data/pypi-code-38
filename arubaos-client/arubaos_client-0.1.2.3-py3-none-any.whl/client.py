from pytimeparse import parse
import requests
import urllib3
from pprint import pprint
import time
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

cpu_regex = re.compile(r'(?P<key>.*?) (?P<value>.*?)%(?:, | |$)')
memory_regex = re.compile(
    r'(?:Memory.*?: )?(?P<key>.*?): (?P<value>.*?)(?:,|$)')
user_regex = re.compile(r'^(?P<key>.*?): (?P<actual>\d+)/(?P<max>\d+)$')
flag_regex = re.compile(r'(?P<flag>.*?) = (?P<meaning>.*?)(?:; |;|$)')
flag_replace_regex = re.compile(r' followed by \&quot;.*')
essid_regex = re.compile(r'^\s*\d+(?P<radio>\w) \w+ (?P<ESSID>.*?) (?:Stats)$')
eirp_regex = re.compile(r'^.*?\/(?P<eirp>\d+.\d+)\/(?P<max_eirp>\d+.\d+)$')
eirp_regex_clients = re.compile(
    r'^.*?\/(?P<eirp>\d+.\d+)\/(?P<max_eirp>\d+.\d+)\/(?P<clients>\d+)$')
mac_regex = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')


class MobilityControllerAPIClient(object):
    '''
    Attributes:
        :username (str): MobilityController Login username.
        :password (str): MobilityController Login password.
        :url (str): MobilityController URL.
        :
    '''

    def __init__(self, **kwargs):
        '''
            Args:
            :username (str): MobilityController Login username.
            :password (str): MobilityController Login password.
            :url (str): MobilityController url.
            :proxy (str) Proxy to use. (default=None)
            :api_version API Version to use (default=1)
            Usage: ::
            >>> from aruba_os import ArubaOSAPIClient
            >>> MobilityController = MobilityControllerAPIClient(username='admin',
            >>>                            password='xxxxx',
            >>>                            url='https://<ip_addr|hostname>:<port>/')
            >>>
        '''
        self.bands = {"2g": 'g', "5g": 'a'}
        self.config_path = kwargs.get('config_path', '/mm/mynode')
        self.api_version = kwargs.get('api_version', 1)
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.url = kwargs['url']
        self.verify = kwargs.get('verify', False)
        proxy = kwargs.get('proxy', None)
        self.proxies = None
        if proxy:
            self.proxies = {
                'http': proxy,
                'https': proxy
            }
        self.url = self.path(
            'v{version}/'.format(version=self.api_version))
        self.session = None

    def login(self):
        '''
            Login to aruba_os device
        '''
        self.session = requests.Session()
        self.session.proxies = self.proxies
        self.session.verify = self.verify
        url = self.path('api/login')
        params = {'username': self.username,
                  'password': self.password,
                  }
        login = self.session.get(url, params=params)
        if login.ok:
            self.uid = {'UIDARUBA': login.json()['_global_result']['UIDARUBA']}
            self.session.params = self.uid
        return login.ok

    def logout(self):
        '''
            Close the session to the device
        '''
        if not self.session:
            raise Exception("You need to login")
        url = self.path('api/logout')
        logout = self.session.get(url)
        return logout.ok

    def get(self, ressource):
        '''
            get an api ressource
        '''
        url = self.path(ressource)
        print(url)
        answer = self.session.get(url)
        if answer.ok:
            return answer.text
        return {}

    def by_command(self, command):
        '''
            Get information by show <> command
            Args:
                :command (str): command must be a show command

            Returns:
                :answer (dict): {}

        '''
        url = self.path('configuration/showcommand')
        params = {
            "json": 1,
            "command": command
        }
        answer = self.session.get(url, params=params)
        if answer.ok:
            return answer.json()
        return {}

    def sys_info(self):
        '''
            Return system information
            Returns:
                :answer (dict): {}
        '''
        url = self.path('configuration/container/sys_info')
        answer = self.session.get(url)
        if answer.ok:
            return answer.json()
        else:
            return {}

    def clients(self, band="2g"):
        '''
            Gets Amount of clients by Band.
            Args:
                :band (str): 2g or 5g band (self.bands)

            Returns:
                :answer (dict): {}
        '''
        if band not in list(self.bands.keys()):
            raise Exception("Unsupported Band Type: {} :: Only {} are supported.".format(
                band, "or ".join(self.bands.keys())))

        data = self.by_command(
            'show user-table phy-type {}'.format(self.bands[band]))
        return self._restructure_client_count(data)

    def clients_2g(self):
        '''
            Wrapper for self.clients(band='2g')
        '''
        return self.clients(band="2g")

    def clients_5g(self):
        '''
            Wrapper for self.clients(band='5g')
        '''
        return self.clients(band="5g")

    def aps(self, group=None, long=True):
        '''
            Gets a list of aps
            Args:
                :group (str): group Notation
                :long (bool): extensive information

            Returns:
                :url (list): List of APs
        '''
        answer = self.by_command('show ap database {}{}'.format(
            "long " if long else "",
            "group {}".format(group) if group else "local")
        )
        answer = self._restructure_database_output(answer)
        return self._restructure_flags_data(answer)

    def ap_by_mac(self, ap_mac):
        '''
            Args:
                :ap_mac (str): MAC address in xx:xx:xx:xx:xx:xx  notation

            Returns:
                :url (str): '<self.url/path>'
        '''
        if not mac_regex.match(ap_mac):
            raise Exception("Invalid MAC Address: {}".format(ap_mac))
        answer = self.by_command(
            'show ap provisioning wired-mac {}'.format(ap_mac))
        return {ap_mac: self._restructure_provisioning_output(answer)}

    def ap(self, ap_name):
        '''
            Get information about a ap_name
            Args:
                :ap_name (str): Name of the AP

            Returns:
                :ap (dict): {ap_name: statistics}
        '''
        answer = self.by_command('show ap active ap-name {}'.format(ap_name))
        answer = self._right_typing(answer)
        return {ap_name: self._restructure_flags_data(answer)}

    def ap_re_group_mac(self, ap_mac, ap_group):
        value = {}
        url = self.path('configuration/object/wdb_cpsec_modify_mac')
        data = {
            "name": ap_mac,
            "ap_group": ap_group
        }

        answer = self.session.post(
            url, params={"config_path": self.config_path}, json=data)

        if answer.ok:
            value["wdb_cpsec_modify_mac"] = answer.json()
        else:
            value["wdb_cpsec_modify_mac"] = {}
        data = {
            "wired-mac": ap_mac,
            "new-group": ap_group
        }
        url = self.path('configuration/object/ap_regroup')
        answer = self.session.post(
            url, params={"config_path": self.config_path}, json=data)
        if answer.ok:
            value["ap_regroup"] = answer.json()
        else:
            value["ap_regroup"] = {}
        return value

    def cpu_load(self):
        '''

            Returns:
                :cpu (dict): {}
        '''
        data = self.by_command('show cpuload')
        data = data.get('_data', [""])[0]
        data = cpu_regex.findall(data)
        cpu = {"cpu": {}}
        for key, value in data:
            cpu["cpu"][key] = float(value)
        return cpu

    def memory_usage(self):
        '''

            Returns:
                :memory_usage (dict): {}
        '''
        data = self.by_command('show memory')
        data = data.get('_data', [""])[0]
        data = memory_regex.findall(data)
        ram = {"ram": {}}
        for key, value in data:
            ram["ram"][key.strip()] = int(value)
        return ram

    def path(self, path):
        '''
            builds up the complete URL

            Args:
                :path (str): Ressource extension
                :path (list): list of separated Ressource extensions

            Returns:
                :url (str): '<self.url/path>'
        '''
        return urljoin(self.url, path)
# Private Parsing Functions

    def _try_cast(self, value):
        '''
            Args:
                :value (dict): {..}

            Returns:
                :value (dict): casted
        '''
        try:
            return float(value)
        except:
            if value in ['N/A', '-'] or 'bps' in value:
                return float(0)
            return value

    def _parse_eirp(self, value, other_regex=False):
        if not other_regex:
            try:
                eirp, max_eirp = eirp_regex.findall(value)[0]
                return self._try_cast(eirp), self._try_cast(max_eirp)
            except TypeError:
                return 0.0, 0.0
        else:
            try:
                eirp, max_eirp, clients = eirp_regex_clients.findall(value)[0]
                return self._try_cast(clients), self._try_cast(eirp), self._try_cast(max_eirp)
            except TypeError:
                return 0.0, 0.0, 0.0

    def _restructure_client_count(self, values):
        data = values['_data'][0]
        data = user_regex.findall(data)
        key, actual, maxi = data[0]
        users = {
            str(key): {
                "actual": self._try_cast(actual),
                "max": self._try_cast(maxi)
            }
        }
        values['_data'] = users
        return values

    def _restructure_flags_data(self, values):
        data = values.get('_data')
        if not data:
            for key in ['_meta', '_data']:
                if key in values.keys():
                    del(values[key])
            return values
        data = "".join(data)
        data = data.replace("Flags: ", "")
        data = flag_replace_regex.sub("", data)
        data = flag_regex.findall(data)

        flags = {
            "flags": {}
        }
        for flag, meaning in data:
            flags["flags"][flag.strip()] = meaning
        del(values['_data'])
        del(values['_meta'])
        values["_data"] = flags
        return values

    def _restructure_provisioning_output(self, values):
        del(values['_meta'])
        data = {}
        for provisioning in values.values():
            for item in provisioning:
                data[item["Item"].lower().replace(' ', '_').replace('(%)', '').replace('(kbps)', '_kbps')
                     ] = self._try_cast(item["Value"])
        del(values)
        return data

    def _restructure_database_output(self, values):
        for ap in values.get("AP Database", []):
            status = ap.get("Status")
            status = status.split(" ")
            try:
                status, uptime = status[0].lower(), parse(
                    status[1].replace(":", ""))
            except IndexError:
                status = "down"
                uptime = 0
            status = True if "up" == status else False
            ap["Status"] = {
                "status": status,
                "uptime": uptime
            }
        return values

    def _right_typing(self, values):

        data = {}
        for key, items in values.items():
            if essid_regex.match(key):
                found = essid_regex.findall(key)
                radio, essid = found[0]
                if radio == 'a':
                    radio = '5g'
                elif radio == 'g':
                    radio = '2g'
                if not data.get('stats'):
                    data['stats'] = {}
                if not data['stats'].get(essid):
                    data['stats'] = {essid: {}}
                data['stats'][essid][radio] = {}

                for item in items:
                    data['stats'][essid][radio][item["Parameter"].lower().replace(' ', '_').replace('(%)', '').replace('(kbps)', '_kbps')
                                                ] = self._try_cast(item["Value"])
            elif 'Active AP Table' in key:
                for item in items:
                    item['Uptime'] = parse(
                        item['Uptime'].replace(":", ""))
                    if '11a Clients' not in item.keys():
                        item['11a_info'] = {}
                        item['11a Clients'.lower().replace(
                            ' ', '_')], item['11a_info']['eirp'], item['11a_info']['max_eirp'] = self._parse_eirp(
                            item["Radio 0 Band Ch/EIRP/MaxEIRP/Clients"], other_regex=True)
                        item['11g_info'] = {}
                        item['11g Clients'.lower().replace(
                            ' ', '_')], item['11g_info']['eirp'], item['11g_info']['max_eirp'] = self._parse_eirp(
                            item["Radio 1 Band Ch/EIRP/MaxEIRP/Clients"],
                            other_regex=True)
                        del(item["Radio 0 Band Ch/EIRP/MaxEIRP/Clients"])
                        del(item["Radio 1 Band Ch/EIRP/MaxEIRP/Clients"])
                    else:
                        item['11a Clients'.lower().replace(
                            ' ', '_')] = self._try_cast(item['11a Clients'])
                        item['11g Clients'.lower().replace(
                            ' ', '_')] = self._try_cast(item['11g Clients'])
                        item['11a_info'] = item['11g_info'] = {}
                        item['11a_info']['eirp'], item['11a_info']['max_eirp'] = self._parse_eirp(
                            item["11a Ch/EIRP/MaxEIRP"])
                        item['11g_info']['eirp'], item['11g_info']['max_eirp'] = self._parse_eirp(
                            item["11g Ch/EIRP/MaxEIRP"])
                        del(item["11a Ch/EIRP/MaxEIRP"])
                        del(item["11g Ch/EIRP/MaxEIRP"])
        values = {**data, **values}
        keys = list(values.keys())
        for key in keys:
            if essid_regex.match(key):
                del(values[key])
        if 'stats' not in values.keys():
            values['stats'] = {}
        return values
