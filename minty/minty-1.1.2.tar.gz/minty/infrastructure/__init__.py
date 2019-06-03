import threading
from collections import namedtuple

import statsd
from redis import StrictRedis

from .. import Base
from ..config.parser import ApacheConfigParser, ConfigParserBase
from ..config.store import FileStore, RedisStore
from ..exceptions import ConfigurationConflict

CONFIG_STORE_MAP = {"file": FileStore, "redis": RedisStore}
CONFIG_ARGUMENT_MAP = {"redis": StrictRedis}


def _parse_global_config(filename, config_parser: ConfigParserBase):
    """Parse config file with given config_parser.

    :param filename: filename
    :type filename: str
    :param config_parser: config parser to use
    :type config_parser: ConfigParserBase
    :return: config
    :rtype: dict
    """
    with open(filename, "r", encoding="utf-8") as config_file:
        content = config_file.read()

    return config_parser.parse(content)


class InfrastructureFactory(Base):
    """Infrastructure factory class.

    The infrastructure factory will create instances of registered
    "infrastructure" classes, with configuration for a specific context.
    """

    slots = [
        "global_config",
        "instance_config_store",
        "registered_infrastructure",
        "config_parser",
        "local_storage",
    ]

    def __init__(
        self, config_file: str, config_parser: ConfigParserBase = None
    ):
        """Initialize an application service factory.

        After reading the configuration, it also configures the defaults
        in the statsd module.

        :param config_file: Global configuration file to read
        :type config_file: str
        :param config_parser: config parser used to parse global configuration
        :type config_parser: ConfigParserBase
        """
        self.local_storage = LocalInfrastructureStorage()
        if config_parser is None:
            config_parser = ApacheConfigParser

        self.config_parser = config_parser()

        self.logger.info(f"Using configuration file '{config_file}'")
        self.global_config = _parse_global_config(
            filename=config_file, config_parser=self.config_parser
        )

        config_store_type = self.global_config["InstanceConfig"]["type"]

        if config_store_type == "none":
            self.instance_config_store = None
        else:
            config_store_args = self.global_config["InstanceConfig"][
                "arguments"
            ]

            try:
                config_store_args = CONFIG_ARGUMENT_MAP[config_store_type](
                    **config_store_args
                )
            except KeyError:
                # There doesn't have to be an argument mapper
                pass

            config_store = CONFIG_STORE_MAP[config_store_type](
                parser=ApacheConfigParser(), arguments=config_store_args
            )

            self.instance_config_store = config_store

        if "statsd" in self.global_config:
            if "disabled" in self.global_config["statsd"]:
                self.global_config["statsd"]["disabled"] = bool(
                    int(self.global_config["statsd"]["disabled"])
                )
            statsd.Connection.set_defaults(**self.global_config["statsd"])
        else:
            # No statsd configuration available; forcefully disable it
            statsd.Connection.set_defaults(disabled=True)

        self.registered_infrastructure = {}

    def get_config(self, context: str) -> dict:
        """Get config from infrafactory for given context.

        :param context: context
        :type context: str
        :return: config
        :rtype: dict
        """
        if self.instance_config_store is None or context is None:
            config = {**self.global_config}
        else:
            instance_config = self.instance_config_store.retrieve(context)
            config = {**self.global_config, **instance_config}
        return config

    def register_infrastructure(self, name: str, infrastructure: object):
        """Register an infrastructure class with the factory.

        :param cls: Class to register in the infrastructure factory
        :type cls: class
        """
        self.registered_infrastructure[name] = infrastructure

    def get_infrastructure(self, context: str, infrastructure_name: str):
        """Retrieve an infrastructure instance for the selected instance.

        If local_storage does not already have the infrastructure instance,
        it will be instantiated from infrastructure factory.

        :param infrastructure_name: Name of the infrastructure class to
            instantiate
        :type infrastructure_name: str
        :return: infrastructure
        :rtype: object
        """
        InfraKey = namedtuple("InfraKey", ["context", "infrastructure_name"])
        infra_key = InfraKey(
            context=context, infrastructure_name=infrastructure_name
        )
        try:
            return self.local_storage.infra[infra_key]
        except KeyError:
            pass

        try:
            infra = self.get_infra_from_infrastructure_factory(
                context=context, infrastructure_name=infrastructure_name
            )
        except KeyError as error:
            raise ConfigurationConflict(
                f"KeyError in infrastructure_factory.get_infrastructure: {error}"
            ) from error

        self.local_storage.infra[infra_key] = infra
        return infra

    def get_infra_from_infrastructure_factory(
        self, context: str, infrastructure_name: str
    ):
        """Retrieve an infrastructure instance for the selected instance.

        :param infrastructure_name: Name of the infrastructure class to
            instantiate
        :type infrastructure_name: str
        :return: infrastructure
        :rtype: object
        """
        config = self.get_config(context=context)
        with self.statsd.get_timer("get_infrastructure").time(
            infrastructure_name
        ):
            infra = self.registered_infrastructure[infrastructure_name](
                config=config
            )
        return infra

    def flush_local_storage(self):
        """Clean up all infrastructure in the local store.

        Usually called at the end of a request cycle. Some infrastructure
        instances might not have the `.clean_up(infrastructure)` method.
        """
        for infra_key, infra in self.local_storage.infra.items():
            try:
                with self.statsd.get_timer(
                    f"{infra_key.infrastructure_name}"
                ).time("clean_up"):
                    self.registered_infrastructure[
                        infra_key.infrastructure_name
                    ].clean_up(infra)
            except AttributeError:
                # Infrastructure does not have clean_up method implemented.
                pass
        self.local_storage.infra = {}
        return


class LocalInfrastructureStorage(threading.local):
    """Thread local storage for infrastructure."""

    def __init__(self):
        """Initilize the local storage for infrastructure with infra dict."""
        self.infra = {}
