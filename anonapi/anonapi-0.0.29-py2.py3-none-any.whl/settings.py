"""Settings used by anon console app

"""

import yaml

from anonapi.objects import RemoteAnonServer


class AnonClientSettings:
    """Settings used by anonymization web API client """

    def __init__(self, servers, user_name, user_token):
        """
        Parameters
        ----------
        servers: List(RemoteAnonServer)
            all servers
        user_name: str
            user name
        user_token: str
            API token

        """
        self.servers = servers
        self.user_name = user_name
        self.user_token = user_token
        if servers:
            self.active_server = servers[0]
        else:
            self.active_server = None

    def to_datamap(self):
        """Convert these settings to a dict that can be used by YAML

        """
        datamap = {
            "servers": {x.name: x.url for x in self.servers},
            "user_name": self.user_name,
            "user_token": self.user_token,
        }
        if self.active_server:
            datamap["active_server_name"] = self.active_server.name
        else:
            datamap["active_server_name"] = None
        return datamap

    def save_to_file(self, filename):
        """ Putting save to file method here in base class so I can write settings files generated from code

        """
        datamap = self.to_datamap()
        with open(filename, "w") as f:
            yaml.dump(datamap, f, default_flow_style=False)

    def save(self):
        """ Implementing save() here to fulfil settings object signature
        """
        pass  # can't really save anything


class DefaultAnonClientSettings(AnonClientSettings):
    """A settings object with some default values. For testing and for writing settings when none are available

    """

    def __init__(self):
        """Create default settings object:

        >>> servers = [RemoteAnonServer("test", "https://hostname_of_api")]
        >>> user_name='username'
        >>> user_token='12345abc'

        """
        super().__init__(
            servers=[RemoteAnonServer("test", "https://hostname_of_api")],
            user_name="username",
            user_token="token",
        )


class DataMap:
    """Structure to hold output from a yaml load(). Raises error when you cannot get() an expected key
    Poor man's substitute for schema validation.

    """

    def __init__(self, datamap):
        self._datamap = datamap

    def get(self, key):
        if key not in self._datamap.keys():
            msg = f"expected to find key '{key}'"
            raise AnonClientSettingsFromFileException(msg)
        return self._datamap[key]


class AnonClientSettingsFromFile(AnonClientSettings):
    """ Settings which are bound to a file. Can load and save from there.

    """

    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            datamap = yaml.safe_load(f)

        self.parse_datamap(DataMap(datamap))

    def __str__(self):
        return f"Settings at {self.filename}"

    def parse_datamap(self, datamap: DataMap):
        try:
            servers = datamap.get("servers")
            user_name = datamap.get("user_name")
            user_token = datamap.get("user_token")
            active_server_name = datamap.get("active_server_name")
        except AnonClientSettingsFromFileException as e:
            msg = f"Could not read all settings from {self.filename}: {e}"
            raise AnonClientSettingsException(msg)

        servers_parsed = {}
        for name, url in servers.items():
            servers_parsed[name] = RemoteAnonServer(name=name, url=url)
        super().__init__(
            servers=list(servers_parsed.values()),
            user_name=user_name,
            user_token=user_token,
        )
        # set active server
        if active_server_name is None:
            self.active_server = None
        else:
            try:
                self.active_server = servers_parsed[active_server_name]
            except KeyError:
                msg = (
                    f"Active server name '{active_server_name}' was not found in list of servers_parsed "
                    f"'{list(servers_parsed.keys())}'. I don't know what the active server is supposed to be"
                )
                raise AnonClientSettingsException(msg)

    def save(self):
        super().save_to_file(self.filename)


class AnonClientSettingsException(Exception):
    pass


class AnonClientSettingsFromFileException(AnonClientSettingsException):
    pass
