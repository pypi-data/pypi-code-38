import os
import sqlalchemy
import yaml
import importlib
import re
import ast


class BaseDriver(object):
    """
    BaseDriver represents an abstract base class for data source drivers.

    The constructor of BaseDriver takes any number of keyword arguments (kwargs) that it will store internally.
    """
    TYPE = 'Generic DB Driver'

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
        self.uri = kwargs["uri"] if "uri" in kwargs else ""
        self._internal_data = kwargs

    @classmethod
    def from_json(cls, raw_setts):
        """Instantiates an instance of the BaseDriver based on the raw_setts provided.

        :param raw_setts: a string containing the keyword arguments for the driver.

        :returns: An `object` of the target BaseDriver with specified settings.
        """
        setts = ast.literal_eval(raw_setts)
        return cls(**setts)

    @classmethod
    def get_name(cls):
        return cls.TYPE

    @staticmethod
    def resolve_params(input_str, params_dict):
        matches = re.findall('<([A-Za-z0-9_ ]+)>', input_str)
        for match in matches:
            input_str = input_str.replace("<{}>".format(match), str(params_dict[match]))
        return input_str

    @classmethod
    def get_module_path(cls):
        return cls.__module__ + "." + cls.__name__


class Connector(object):
    """
    The Connector object represents the metadata about a driver and
    its desired settings so that they may be serialized and deserialized as needed.
    """
    @staticmethod
    def fetch(name, connections_source):
        if isinstance(connections_source, str):
            source_dict = ast.literal_eval(connections_source)
        else:
            source_dict = yaml.load(connections_source, Loader=yaml.FullLoader)
            if name not in source_dict:
                raise ValueError("Invalid Connection name", name)
            source_dict = source_dict[name]

        if "driver" not in source_dict:
            raise ValueError("Source must contain a driver value", source_dict)

        source_dict = {key: os.path.expandvars(val) if isinstance(val, str) else val for key, val in source_dict.items()}
        driver_str = source_dict["driver"]
        # resolve driver
        clzz_file, clzz_name = driver_str.rsplit(".", 1)
        clzz_file = importlib.import_module(clzz_file)
        if not hasattr(clzz_file, clzz_name):
            raise ValueError("Class file", clzz_file, "does not contain a class called", clzz_name)
        driver_obj = getattr(clzz_file, clzz_name)
        if "connection_parameters" not in source_dict:
            driver_obj = driver_obj(**source_dict)
        else:
            driver_obj = driver_obj(**source_dict["connection_parameters"])
        return driver_obj


class DatabaseDriver(BaseDriver):
    """Generic database driver that is a passthrough to sqlalchemy's create_engine"""
    def __init__(self, **kwargs):
        super(DatabaseDriver, self).__init__(**kwargs)
        self.engine = sqlalchemy.create_engine(self.uri)

    def write_df(self, table_name, df, **kwargs):
        return df.to_sql(table_name,
                         self.engine,
                         **kwargs)
