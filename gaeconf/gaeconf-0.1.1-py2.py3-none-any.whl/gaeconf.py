# -*- coding: utf-8 -*-
import inspect
import ruamel.yaml as yaml
from os import environ


class AppEngineBaseConfig:
    """
    This base class is implements a `to_yaml()` method which dumps a YAML
    file compatible with GAE.

    Instructions
    ------------

    - Constructor receives an optional `exposed_env_vars` parameter
      to define the host environment variables which will be passed to
      the resulting GAE app.yaml file.
    - The attributes of the class will be exported to the final yaml.
    - An attribute starting with __ENV__ will be considered an environment
      variable and it will be included to env_variables in the yaml.
    - Some of the class attributes can be ignored by overriding
      `get_ignore_attrs` method.
    """

    service = None
    runtime = None

    def __init__(self, exposed_env_vars=None):
        self._exposed_env_vars = exposed_env_vars or []

    def clean_config(self, config: dict) -> dict:
        """
        Config post-processing

        :param config: App engine configuration vars
        :type config: dict
        :return: dict
        """
        return config

    def get_ignore_attrs(self, data: list) -> list:
        """
        Exclude class attrbutes from the yaml export

        :param data: List of class attributes
        :type data: list
        :return: list
        """
        data.append('ignore_attrs')
        return data

    def to_yaml(self) -> str:
        """
        Dumps the current configuration as yaml

        :return: str
        """
        methods = [e[0] for e in inspect.getmembers(self, predicate=inspect.ismethod)]

        # Class attrs ending with __ENC are attributes whose values were previously encrypted
        # and then decrypted, but it is necessary to get the real attribute name without the
        # __ENC
        config = {
            e.rsplit('__ENC', 1)[0]: getattr(self, e)
            for e in dir(self)
            if not e.startswith('_') and e not in methods and e not in self.get_ignore_attrs([])
        }

        # Filter class attrs starting with __ENV__ and adds them to env_vars
        env_vars = {e.split('__ENV__')[1].rsplit('__ENC', 1)[0]: getattr(self, e) for e in dir(self) if '__ENV__' in e}

        # Include exposed environment variables in env_variables
        for e in self._exposed_env_vars:
            env_var_value = environ.get(e, '')
            if env_var_value:
                env_vars[e] = env_var_value

        config["env_variables"] = env_vars
        return yaml.safe_dump(self.clean_config(config), default_flow_style=False)


class AppEngineStandardConfig(AppEngineBaseConfig):
    """
    Defines a suitable configuration for Google App Engine standard
    runtime.

    By default the runtime is *python37* and the instance class is
    *F4_HIGHMEM* but these defaults can be overriden with the following
    environment variables:


    - `GAECONF_STANDARD_RUNTIME`
    - `GAECONF_STANDARD_INSTANCE_CLASS`
    """

    runtime = environ.get("GAECONF_STANDARD_RUNTIME", "python37")
    instance_class = environ.get("GAECONF_STANDARD_INSTANCE_CLASS", "F4_HIGHMEM")


class AppEngineFlexibleConfig(AppEngineBaseConfig):
    """
    Defines a suitable configuration for Google App Engine flexible
    runtime.

    Default configuration can be overriden with environment variables:


    - `GAECONF_FLEXIBLE_RUNTIME`: *python*
    - `GAECONF_FLEXIBLE_RUNTIME_PYTHON_VERSION`: *3.7*
    - `GAECONF_AUTOSCALING_MAX_INSTANCES`: *2*
    - `GAECONF_AUTOSCALING_MIN_INSTANCES`: *1*
    - `GAECONF_FLEXIBLE_NUM_CPU`: *2*
    - `GAECONF_FLEXIBLE_MEMORY_GB`: *3*
    - `GAECONF_FLEXIBLE_DISK_SIZE_GB`: *20*
    """

    service = None
    instance_tag = None
    subnetwork_name = None
    runtime = environ.get("GAECONF_FLEXIBLE_RUNTIME", "python")
    automatic_scaling = {
        "max_num_instances": int(environ.get("GAECONF_AUTOSCALING_MAX_INSTANCES", 2)),
        "min_num_instances": int(environ.get("GAECONF_AUTOSCALING_MIN_INSTANCES", 1)),
    }
    resources = {
        "cpu": int(environ.get("GAECONF_FLEXIBLE_NUM_CPU", 2)),
        "memory_gb": int(environ.get("GAECONF_FLEXIBLE_MEMORY_GB", 3)),
        "disk_size_gb": int(environ.get("GAECONF_FLEXIBLE_DISK_SIZE_GB", 20))
    }
    runtime_config = {
        "python_version": environ.get("GAECONF_FLEXIBLE_RUNTIME_PYTHON_VERSION", "3.7")
    }
    env = 'flex'

    def get_ignore_attrs(self, data: list) -> list:
        data = super().get_ignore_attrs(data)
        data.extend(['instance_tag', 'subnetwork_name'])
        return data

    def clean_config(self, config: dict) -> dict:
        config['network'] = {
            "instance_tag": self.instance_tag or self.service,
            "name": "default",
            "subnetwork_name": self.subnetwork_name
        }
        return super().clean_config(config)


def load_yaml_classes(filename: str) -> dict:
    """
    Parses a YAML file and builds Python classes defining the
    GAE services.

    :param filename: path to a yaml configuration file
    :type filename: str
    :returns: {<service-name>: <service-class>}
    """

    with open(filename) as stream:
        obj = yaml.load(stream, Loader=yaml.Loader)
        services = {}
        for class_name, config in obj['services'].items():
            parent_classes = {k.__name__: k for k in services.values()}
            parents = tuple([parent_classes[e] for e in tuple(config.pop('inherits_from', []))])
            attrs = config.copy()
            env_vars = attrs.pop('env_variables', {})
            for k, v in env_vars.items():
                attrs[f'__ENV__{k}'] = v
            if 'service' in config:
                services[config["service"]] = type(class_name, parents, attrs)
            else:
                services[class_name] = type(class_name, parents, attrs)
        return services
