import os
import configparser


DOTFILE_NAME = "{}/tronald.ini".format(os.path.expanduser("~"))


class TronaldConfig:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(DOTFILE_NAME)

        if not "tronald" in config.sections():
            config["tronald"] = {
                "KeyPath": "",
                "DefaultDatabase": "",
                "Prefix": "",
                "Suffix": "",
            }

            with open(DOTFILE_NAME, "w") as configfile:
                config.write(configfile)
            config.read(DOTFILE_NAME)

        self.configuration = config["tronald"]

    def get_value(self, key):
        config = configparser.ConfigParser()
        config.read(DOTFILE_NAME)
        if not key in config["tronald"]:
            return None
        return config["tronald"][key]

    def set_value(self, key, value):
        config = configparser.ConfigParser()
        config.read(DOTFILE_NAME)
        config["tronald"][key] = value
        with open(DOTFILE_NAME, "w") as configfile:
            config.write(configfile)
            return config


class MetaData:
    def __init__(
        self,
        host=None,
        container=None,
        ssh_user=None,
        postgres_user=None,
        postgres_db="app",
        dump_name=None,
        target=None,
    ):
        config = TronaldConfig()
        self.host = host
        self._container = container
        self.postgres_user = postgres_user
        self.postgres_db = postgres_db
        self.ssh_user = ssh_user
        self.target = target

        if self.postgres_db:
            self.db_name = self.postgres_db
        else:
            self.db_name = config.get_value("defaultdatabase")

        self.prefix = config.get_value("prefix")
        self.suffix = config.get_value("suffix")
        self.key_path = config.get_value("keypath")

    @property
    def postgres_user(self):
        return self._postgres_user or "postgres"

    @postgres_user.setter
    def postgres_user(self, user):
        self._postgres_user = user

    @property
    def ssh_user(self):
        return self._ssh_user or "root"

    @ssh_user.setter
    def ssh_user(self, user):
        self._ssh_user = user

    @property
    def container(self):
        if self._container:
            return self._container

        if not self.host:
            raise Exception(
                "No container name derivation possible because of missing host."
            )

        if self.host:
            return "{}{}{}".format(self.prefix, self.host, self.suffix)

    @container.setter
    def container(self, container_name):
        self._container = container_name

    @property
    def database(self):
        return self.db_name or "app"

    @property
    def rsa_key(self):
        return self.key_path or "~/.ssh/id_rsa"

    @property
    def target(self):
        return self._target or "recent-dump.db"

    @target.setter
    def target(self, target_path):
        self._target = target_path

    @property
    def dump_name(self):
        return "dump-{}.db".format(self._container)
