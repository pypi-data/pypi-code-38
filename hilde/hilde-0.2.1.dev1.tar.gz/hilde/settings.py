""" Settings class for holding settings, based on configparser.ConfigParser """
import time
import configparser
import json
from os import path

from ase.io import read
from ase.atoms import Atoms


from hilde._defaults import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_FIREWORKS_FILE,
    DEFAULT_SETTINGS_FILE,
    DEFAULT_TEMP_SETTINGS_FILE,
    DEFAULT_GEOMETRY_FILE,
)
from hilde import __version__ as version
from hilde.helpers.attribute_dict import AttributeDict
from hilde.helpers.warnings import warn


class Config(configparser.ConfigParser):
    """ConfigParser that has a slightly more clever get function."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, **kwargs, interpolation=configparser.ExtendedInterpolation()
        )

    def getval(self, *args, **kwargs):
        """ Redifine getval() to allow for json formated values (not only string) """
        try:
            return json.loads(self.get(*args, **kwargs))
        except json.JSONDecodeError:
            try:
                return self.getboolean(*args, **kwargs)
            except ValueError:
                return self.get(*args, **kwargs)


class ConfigDict(AttributeDict):
    """Dictionary that holds the configuration settings"""

    def __init__(self, *args, config_files=["hilde.cfg"], **kwargs):

        super().__init__(*args, **kwargs)

        config = Config()
        config.read(config_files)

        # Recursion depth: 1
        for sec in config.sections():
            self[sec] = AttributeDict()
            for key in config[sec]:
                val = config.getval(sec, key)
                self[sec][key] = val

    def __str__(self):
        """ for printing the object """

        return self.get_string()

    def print(self):
        """ literally print(self) """
        print(self.get_string())

    def write(self, filename=DEFAULT_SETTINGS_FILE, pickle=False):
        """write a settings object human readable and pickled"""
        with open(filename, "w") as f:
            timestr = time.strftime("%Y/%m/%d %H:%M:%S")
            f.write(f"# configfile written at {timestr}\n")
            f.write(self.get_string())
        #
        if pickle:
            import pickle

            # write pickled
            with open(filename + ".pick", "wb") as f:
                pickle.dump(self, f)

    def get_string(self, width=30):
        """ return string representation for writing etc. """
        string = ""
        for sec in self:
            # Filter out the private attributes
            if sec.startswith("_"):
                continue
            string += f"\n[{sec}]\n"
            for key in self[sec]:
                elem = self[sec][key]
                if "numpy.ndarray" in str(type(elem)):
                    elem = elem.flatten()
                #
                if elem is None:
                    elem = "null"
                #
                if key == "verbose":
                    continue
                string += "{:{}s} {}\n".format(f"{key}:", width, elem)
        return string


class Configuration(ConfigDict):
    """ class to hold the configuration from hilde.cfg """

    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        super().__init__(config_files=[config_file])

        # include the hilde version tag
        self.update({"hilde": {"version": version}})


class Settings(ConfigDict):
    """ Class to hold the settings parsed from settings.in (+ the configuration) """

    def __init__(
        self,
        settings_file=DEFAULT_SETTINGS_FILE,
        config_file=DEFAULT_CONFIG_FILE,
        fireworks_file=DEFAULT_FIREWORKS_FILE,
        write=False,
    ):
        self._settings_file = settings_file
        self._config_file = config_file
        self._fireworks_file = fireworks_file
        self._atoms = None

        config_files = [config_file, settings_file, fireworks_file]

        super().__init__(config_files=[file for file in config_files if file])

        if write:
            self.write(DEFAULT_TEMP_SETTINGS_FILE)

    @property
    def atoms(self, format="aims"):
        """ Return the settings.atoms object """
        if self._atoms:
            return self._atoms

        # use the file specified in geometry.file or the default (geometry.in)
        if "geometry" in self and "file" in self.geometry and self.geometry.file:
            file = self.geometry.file
        else:
            file = DEFAULT_GEOMETRY_FILE

        if path.exists(file):
            self._atoms = read(file, format=format)
            return self._atoms

        warn(f"Geometry file {file} not found.", level=1)

        return None

    @atoms.setter
    def atoms(self, object):
        """ Set the settings.atoms object """
        assert isinstance(object, Atoms), type(object)
        self._atoms = object

    def get_atoms(self, format="aims"):
        """ parse the geometry described in settings.in and return as atoms """
        return self.atoms
