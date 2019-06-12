import hashlib
import locale
import logging
import os
import platform
import re
import socket
import time

import netifaces
import requests
from requests.auth import HTTPBasicAuth

import nerdvision
from nerdvision import settings
from nerdvision.Utils import Utils

our_logger = logging.getLogger("nerdvision")


class ClientRegistration(object):
    def __init__(self):
        self.start = int(round(time.time() * 1000))
        self.api_key = settings.get_setting("api_key")
        self.name = settings.get_setting("name")
        self.tags = settings.get_setting("tags")

        self.uid = self.generate_uid()
        self.env_str_max = settings.get_setting("env_max_str_length")
        self.env_regex = re.compile(settings.get_setting("env_regex"))
        self.license_url = settings.get_license_url()
        self.network_exclude_regex = re.compile(settings.get_setting("network_interface_regex"))

    def run_and_get_session_id(self):
        reg_doc = {
            'uid': self.uid,
            'api_key': self.api_key,
            'product': self.product_extra(),
            'instance': self.instance_extra(),
            'os': self.os_extra(),
            'language': self.language_extra(),
            'env': self.env_extra(),
            'network': self.network_extra(),
            'tags': self.tags
        }
        our_logger.debug("Sending activation to %s => %s", self.license_url, reg_doc)
        response = requests.post(self.license_url, json=reg_doc, auth=HTTPBasicAuth(self.uid, self.api_key))

        our_logger.debug("Response from activation attempt: %s => %s", response.status_code, response.text)
        if response.status_code == 200:
            json = response.json()
            response.close()
            return json['session']
        response.close()
        return None

    def generate_uid(self):
        if self.tags is not None:
            flat_tags_ = [k + self.tags[k] for k in sorted(self.tags.keys())]
        else:
            flat_tags_ = ""
        return hashlib.md5(
            str((self.name if self.name is not None else "") + socket.gethostname() + "".join(flat_tags_)).encode()).hexdigest()

    def network_extra(self):
        return {
            'hostname': socket.gethostname(),
            'address': '',
            'interfaces': self.load_interfaces()
        }

    def load_interfaces(self):
        ifaces = []
        filtered = list(filter(lambda x: self.network_exclude_regex.match(x) is None, netifaces.interfaces()))

        for _next in filtered:
            try:
                ifaddresses = netifaces.ifaddresses(_next)
                addresses = []
                if netifaces.AF_INET in ifaddresses:
                    inet_v4 = ifaddresses[netifaces.AF_INET]
                    addresses += [{
                        'hostname': socket.gethostbyaddr(net['addr'])[0],
                        'address': net['addr']
                    } for net in inet_v4]
                elif netifaces.AF_INET6 in ifaddresses:
                    inet_v6 = ifaddresses[netifaces.AF_INET6]
                    addresses += [{
                        'hostname': socket.gethostbyaddr(net['addr'])[0],
                        'address': net['addr']
                    } for net in inet_v6]
                else:
                    continue

                mac = ifaddresses[netifaces.AF_LINK]
                ifaces.append({
                    'name': _next,
                    'mac': mac[0]['addr'],
                    'addresses': addresses
                })
            except Exception as e:
                if settings.is_client_reg_debug():
                    our_logger.exception("Error processing iface {}", _next, e)

        return ifaces

    def env_extra(self):
        env_dict = {}
        env_keys = os.environ.keys()
        for env_key in env_keys:
            if self.env_regex.match(env_key) is not None:
                continue
            val = os.environ[env_key]
            if len(val) > self.env_str_max:
                env_dict[env_key] = val[:self.env_str_max] + '...'
            else:
                env_dict[env_key] = val
        return env_dict

    @staticmethod
    def language_extra():
        return {
            'name': platform.python_implementation(),
            'type': 'python',
            'version': platform.python_version(),
            'python_branch': platform.python_branch(),
            'python_build': platform.python_build()[1],
            'python_compiler': platform.python_compiler(),
            'python_revision': platform.python_revision(),
        }

    def instance_extra(self):
        return {
            'start_ts': self.start,
            'name': self.name
        }

    @staticmethod
    def product_extra():
        return {
            "major_version": nerdvision.__version_major__,
            "minor_version": nerdvision.__version_minor__,
            "micro_version": nerdvision.__version_micro__,
            "path": nerdvision.__file__,
            "build": nerdvision.__props__['__Git_Commit_Id__'],
            "name": nerdvision.agent_name,
            "version": nerdvision.__version__,
            "properties": nerdvision.__props__
        }

    @staticmethod
    def os_extra():
        def get_btime(file):
            readlines = file.readlines()
            line = list(filter(lambda _line: _line.startswith("btime"), readlines))
            btime = None

            if len(line) != 0:
                btime = line[0]

            if btime is None:
                return btime
            return int(int(btime[6:-1]) * 1000)

        os_data = {
            "timezone": ClientRegistration.read_file("/etc/timezone"),
            "name": platform.system(),
            "arch": platform.machine(),
            "time": int(round(time.time() * 1000)),
            # this will need testing on lots of locals
            "lang": locale.getdefaultlocale()[0][:2],
            "locale": locale.getdefaultlocale()[0][-2:],
            "version": ClientRegistration.load_os_version()
        }

        ts = ClientRegistration.read_file("/proc/stat", get_btime)

        if ts != -1:
            os_data["start_ts"] = ts

        return os_data

    @staticmethod
    def load_os_version():
        if Utils.is_python_3():
            # noinspection PyUnresolvedReferences
            return os.uname().release
        return os.uname()[2]

    @classmethod
    def read_file(cls, file_name, call_back=lambda _f: _f.read().strip()):
        isfile = os.path.isfile(file_name)

        if not isfile:
            return -1

        with open(file_name, "r") as file:
            return call_back(file)
