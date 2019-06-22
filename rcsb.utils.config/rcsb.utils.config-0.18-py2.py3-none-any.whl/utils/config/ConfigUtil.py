##
# File:    ConfigUtil.py
# Author:  J. Westbrook
# Date:    14-Mar-2018
# Version: 0.001
#
# Updates:
#   31-Mar-2018  jdw standardize argument names
#   16-Jun-2018. jdw add more convenient support for multiple config sections
#   18-Jun-2018  jdw push the mocking down to a new getPath() method.
#   20-Aug-2018  jdw add getHelper() to return an instance of a module/class
#   13-Sep-2018  jdw add YAML support and read/write methods.
#   16-Sep-2018  jdw add support importing a CommentedMap
#    3-Oct-2018  jdw add support to import environment for ini/configparser format files.
#   10-Oct-2018  jdw added methods getConfigPath() adn getMockTopPath()
#   23-Oct-2018  jdw refine export method to manually extract content from configparser structure
#   24-Oct-2018  jdw if config format is not specified perceive the format from the config filename extension
#                    change default section name management.
#    4-Jan-2019  jdw add optional arguments to getPath(...,prefixName=None, prefixSectionName=None)
#                    add methods getDefaultSectionName(), replaceSectionName(), and getSectionNameReplacement()
#   10-Mar-2019  jdw add method getEnvValue() to dereference config option as an environmental variable
##
"""
 Manage simple configuration options.

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import copy
import logging
import os
import sys

import ruamel.yaml

try:
    from configparser import ConfigParser as cp
except ImportError:
    from ConfigParser import SafeConfigParser as cp


logger = logging.getLogger(__name__)


class ConfigUtil(object):
    def __init__(self, configPath=None, defaultSectionName="DEFAULT", fallbackEnvPath=None, mockTopPath=None, configFormat=None, **kwargs):
        """Manage simple configuration options stored in INI (Python configparser-style) or YAML configuration files.


        Args:
            configPath (str, optional): Configuration file path
            defaultSectionName (str, optional): Name of configuration section holding default option values (e.g. DEFAULT)
            fallbackEnvPath (str, optional): Environmental variable holding configuration file path
            mockTopPath (str, optional): Mockpath is prepended to path configuration options if it specified (default=None)
            configFormat (str, optional): Configuration file format (e.g. ini or yaml default=ini)
            **kwargs: importEnvironment(bool) imports environment as default values for ini/configparser format files


        """
        myFallbackPath = os.getenv(fallbackEnvPath, "setup.cfg") if fallbackEnvPath else None
        self.__myConfigPath = configPath if configPath is not None else myFallbackPath
        #
        self.__defaultSectionName = defaultSectionName
        #
        #  Mockpath is prepended to path configuration options if it specified
        self.__mockTopPath = mockTopPath
        #
        # This is the internal container for configuration data from all sources
        self.__cD = {}
        #
        #
        self.__sectionNameD = {"DEFAULT": defaultSectionName}
        #
        self.__configFormat = configFormat
        if not self.__configFormat:
            # Perceive the format from the file path or set default to 'ini'
            if self.__myConfigPath:
                _, ext = os.path.splitext(self.__myConfigPath)
                if ext[1:].lower() in ["yaml", "yml"]:
                    self.__configFormat = "yaml"
                else:
                    self.__configFormat = "ini"
            else:
                self.__configFormat = "ini"
        #
        logger.debug("Using config path %s format %s", self.__myConfigPath, self.__configFormat)
        if self.__myConfigPath:
            self.__configFormat, self.__cD = self.__updateConfig(self.__myConfigPath, self.__configFormat, **kwargs)
            if not self.__cD:
                logger.warning("No configuration information imported - configuration path is %s (%s)", self.__myConfigPath, configFormat)

    def getConfigPath(self):
        return self.__myConfigPath

    def getMockTopPath(self):
        return self.__mockTopPath

    def getDefaultSectionName(self):
        return self.__defaultSectionName

    def replaceSectionName(self, orgSectionName, replaceSectionName):
        """ Set an replacement section name that will override the section name for input requests.
        """
        try:
            self.__sectionNameD[orgSectionName] = replaceSectionName
            return True
        except Exception:
            return False

    def getSectionNameReplacement(self, orgSectionName):
        try:
            return self.__sectionNameD[orgSectionName] if orgSectionName in self.__sectionNameD else orgSectionName
        except Exception:
            return orgSectionName

    def importConfig(self, dObj):
        """Import configuration options from the input dictionary-like object.

        Args:
            dObj (object): Dictionary-like configuration object

        Returns:
            bool: True for sucess or False otherwise

        """
        try:
            if isinstance(dObj, dict):
                self.__cD.update(dObj)
            elif isinstance(dObj, ruamel.yaml.comments.CommentedMap):
                self.__cD = dObj
            elif isinstance(dObj, cp):
                self.__cD.update(self.__extractDict(dObj))
            else:
                logger.error("Cannot import object type %r", type(dObj))
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return False

    def exportConfig(self, sectionName=None):
        try:
            cD = self.__extractDict(self.__cD) if isinstance(self.__cD, cp) else self.__cD
            if sectionName:
                return copy.deepcopy(cD[sectionName])
            else:
                return copy.deepcopy(cD)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return None

    def __updateConfig(self, filePath, configFormat=None, **kwargs):
        """Update the current configuration options with data from the input configuration file.

        Args:
            filePath (str): Configuration file path
            configFormat (str, optional): Configuration file format (e.g. ini or yaml)
            **kwargs: key value arguments pass to import methods

            rountTrip (bool): parse yaml to preserve context for roundtrip processing
            importEnvironment (bool):  include the environment as defaults values for 'ini'/'configparser' format files


        Returns:
            tuple(str, object): 'ini' or 'yaml' and configuration object
        """
        #
        cD = None
        try:
            cf = configFormat if configFormat else self.__configFormat
            if cf.lower() in ["ini", "configparser"]:
                useEnv = kwargs.get("importEnvironment", False)
                cD = self.__readIniFile(filePath, useEnv=useEnv, **kwargs)
                configFormat = "ini"
            elif cf.lower() in ["yaml"]:
                rt = kwargs.get("roundTrip", True)
                cD = self.__readYamlFile(filePath, roundTrip=rt)
                configFormat = "yaml"
        except Exception as e:
            logger.exception("Failing with filePath %r format %r with %s", filePath, configFormat, str(e))
        #
        return configFormat, cD

    def writeConfig(self, filePath, configFormat=None, **kwargs):
        """Write the current configuration in the selected format.

        Args:
            filePath (str): Output configuration file path
            configFormat (str, optional): configuration format (e.g. 'ini' or 'yaml')
            **kwargs: key value arguments passed to export methods

        Returns:
            bool: True for success or False otherwise

        """
        cf = configFormat if configFormat else self.__configFormat
        #
        if cf == "ini":
            if not isinstance(self.__cD, cp):
                cD = self.__createConfigParseObj(self.__cD, delimiter=";")
                ok = self.__writeIniFile(filePath, cD, **kwargs)
            else:
                ok = self.__writeIniFile(filePath, self.__cD, **kwargs)
        elif cf == "yaml":
            cD = self.__extractDict(self.__cD) if isinstance(self.__cD, cp) else self.__cD
            ok = self.__writeYamlFile(filePath, cD, **kwargs)
        else:
            ok = False
        return ok

    def get(self, name, default=None, sectionName=None):
        """Return configuration value of input configuration option.

        Args:
            name (str): configuration option name
            default (str, optional): default value returned if no configuration option is provided
            sectionName (str, optional): configuration section name, a simple key (default = defaultSectionName from object)

        Returns:
            str: configuration option value

        """
        logMissing = False
        val = default
        try:
            mySection = sectionName if sectionName else self.__defaultSectionName
            mySection = self.getSectionNameReplacement(mySection)
            if "." in name:
                val = self.__getKeyValue(self.__cD[mySection], name)
            else:
                val = self.__cD[mySection][name]
            #
            val = str(val) if self.__configFormat == "ini" else val
        except Exception as e:
            if logMissing:
                logger.debug("Missing config option %r (%r) assigned default value %r (%s)", name, mySection, default, str(e))
        #
        return copy.deepcopy(val)

    def getPath(self, name, default=None, sectionName=None, prefixName=None, prefixSectionName=None):
        """ Return path associated with the input configuration option and an option prefix path.
            This method supports mocking where the MOCK_TOP_PATH will be prepended to the configuration path.

        Args:
            name (str): configuration option name
            default (str, optional): default value returned if no configuration option is provided
            sectionName (str, optional): configuration section name, a simple key
            prefixName(str, optional):  optional configuration option for a prefix path
            prefixSectionName(str, optional):  optional configuration section name for a prefix path option (default = defaultSectionName from object)

        Returns:
            str: configuration path

        """
        val = default
        try:
            val = self.get(name, default=default, sectionName=sectionName)
            myPrefixSectionName = prefixSectionName if prefixSectionName else self.__defaultSectionName
            prefixPath = self.get(prefixName, default=None, sectionName=myPrefixSectionName) if prefixName else None

            if prefixPath:
                val = os.path.join(self.__mockTopPath, prefixPath, val) if self.__mockTopPath else os.path.join(prefixPath, val)
            else:
                val = os.path.join(self.__mockTopPath, val) if self.__mockTopPath else val
        except Exception as e:
            logger.debug("Missing config option %r (%r) assigned default value %r (%s)", name, sectionName, default, str(e))
        #
        return val

    def getEnvValue(self, name, default=None, sectionName=None):
        """ Return the value of input configuration option (environmental variable name).

        Args:
            name (str): configuration option name (environmental variable)
            default (str, optional): default value returned if no configuration option is provided
            sectionName (str, optional): configuration section name, a simple key

        Returns:
            str: option(environmental variable) value

        """
        val = default
        try:
            varName = self.get(name, default=None, sectionName=sectionName)
            val = os.environ.get(varName, default)
        except Exception as e:
            logger.debug("Failed processing environmental variable config option %r (%r) assigned default value %r (%s)", name, sectionName, default, str(e))
        #
        return val

    def getList(self, name, default=None, sectionName=None, delimiter=","):
        vL = default if default is not None else []
        try:
            val = self.get(name, default=default, sectionName=sectionName)
            if isinstance(val, (list, set, tuple)):
                vL = list(val)
            else:
                vL = str(val).split(delimiter)
        except Exception as e:
            logger.debug("Missing config option list %r (%r) assigned default value %r (%s)", name, sectionName, default, str(e))
        #
        return vL

    def getHelper(self, name, default=None, sectionName=None, **kwargs):
        """Return an instance of module/class corresponding to the configuration module path.


        Args:
            name (str): configuration option name
            default (str, optional): default return value
            sectionName (str, optional): configuration section name, a simple key
            **kwargs: key-value arguments passed to the module/class instance

        Returns:
            object: instance of module/class


        """
        val = default
        try:
            val = self.get(name, default=default, sectionName=sectionName)
        except Exception as e:
            logger.error("Missing configuration option %r (%r) assigned default value %r (%s)", name, sectionName, default, str(e))
        #
        return self.__getHelper(val, **kwargs)

    def __getHelper(self, modulePath, **kwargs):
        aObj = None
        try:
            aMod = __import__(modulePath, globals(), locals(), [""])
            sys.modules[modulePath] = aMod
            #
            # Strip off any leading path to the module before we instaniate the object.
            mpL = str(modulePath).split(".")
            moduleName = mpL[-1]
            #
            aObj = getattr(aMod, moduleName)(**kwargs)
        except Exception as e:
            logger.error("Failing to instance helper %r with %s", modulePath, str(e))
        return aObj

    def __readIniFile(self, configPath, useEnv=False, **kwargs):
        """Internal method to read INI-style configuration file using standard ConfigParser/configparser library.

        Args:
            configPath (str): Configuration file path
            **kwargs: (dict) passed to ConfigParser/configparser

        Returns:
            object: On success a ConfigParser dictionary-like object

        """
        _ = kwargs
        if useEnv:
            # Note that environmetal variables are still lowercased.
            logger.debug("Using enviroment length %d", len(os.environ))
            configP = cp(os.environ, default_section=self.__defaultSectionName)
        else:
            configP = cp(default_section=self.__defaultSectionName)
        try:
            # This is to avoid case conversion of option names
            # configP.optionxform = str
            configP.optionxform = lambda option: option
            configP.sections()
            configP.read(configPath)
            return configP
        except Exception as e:
            logger.error("Failed reading INI configuration file %s with %s", configPath, str(e))
        return configP

    def __readYamlFile(self, configPath, **kwargs):
        """Internal method to read YAML-style configuration file using ruamel.yaml library.

        Args:
            configPath (str): Configuration file path
            **kwargs: (dict) passed to ConfigParser/configparser

        Returns:
            object: On success a ConfigParser dictionary-like object or an empty dictionary on Failure

        """
        _ = kwargs
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=4, sequence=6, offset=4)
        yaml.explicit_start = True
        rD = {}
        try:
            with open(configPath, "r") as stream:
                rD = yaml.load(stream)
        except Exception as e:
            logger.error("Failed reading YAML configuration file %s with %s", configPath, str(e))
        return rD

    def __writeIniFile(self, configPath, configObj, **kwargs):
        """Internal method to write INI-style configuration file using standard ConfigParser/configparser library.

        Args:
            configPath (str): Output file path
            configObj (object): ConfigParser/configparser object

        Returns:
            bool: True for success or False otherwise

        """
        _ = kwargs
        try:
            with open(configPath, "w") as ofh:
                configObj.write(ofh, space_around_delimiters=False)
            return True
        except Exception as e:
            logger.error("Failed writing INI configuration file %s with %s", configPath, str(e))
        return False

    def __writeYamlFile(self, configPath, mObj, **kwargs):
        """Internal method to write YAML-style configuration file using standard ruamel.yaml library.

        Args:
            configPath (str): Output file path
            dObj (mapping object): Mapping object or dictionary

        Returns:
            bool: True for success or False otherwise
        """
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        yaml.width = kwargs.get("width", 120)
        yaml.indent(mapping=4, sequence=6, offset=4)
        yaml.explicit_start = True
        try:
            #
            with open(configPath, "w") as ofh:
                yaml.dump(mObj, ofh)
            return True
        except Exception as e:
            logger.error("Failed writing YAML configuration file %s with %s", configPath, str(e))
        return False

    def __extractDict(self, configObj):
        """ Internal method to copy the contents of the input ConfigParser object to a dictionary structure.
        """
        sectDict = {}
        #
        defaults = configObj.defaults()
        tD = {}
        for key in defaults.keys():
            tD[key] = defaults[key]

        sectDict[self.__defaultSectionName] = tD

        sections = configObj.sections()
        logger.debug("Sections %r", sections)

        for section in sections:
            options = configObj.options(section)
            tD = {}
            for option in options:
                tD[option] = configObj.get(section, option)

            sectDict[section] = tD
        logger.debug("Returning dictionary %r", sectDict.items())
        return sectDict

    def __createConfigParseObj(self, dObj, delimiter=","):
        """ Internal method to create a configparser object from a dictionary representation
        of configuration sections and objects.

        The dictionary object must conform to the simple configparser data model. For instance:

            d{'sectionName1': {'option1': value2, 'option2': value2, ... }, ... }

        """
        cpObj = cp()
        try:
            for sK, sV in dObj.items():
                if sK != self.__defaultSectionName:
                    cpObj.add_section(sK)
                for oK, oV in sV.items():
                    if isinstance(oV, (list, tuple, set)):
                        cpObj.set(sK, oK, delimiter.join(oV))
                    elif isinstance(oV, (dict)):
                        continue
                    else:
                        cpObj.set(sK, oK, oV)
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return cpObj

    def __getKeyValue(self, dct, keyName):
        """  Return the value of the corresponding key expressed in dot notation in the input dictionary object (nested).
        """
        try:
            kys = keyName.split(".")
            for key in kys:
                try:
                    dct = dct[key]
                except KeyError:
                    return None
            return dct
        except Exception as e:
            logger.exception("Failing for key %r with %s", keyName, str(e))

        return None

    def dump(self):
        for section in self.__cD:
            logger.info("Configuration section: %s", section)
            for opt in self.__cD[section]:
                logger.info(" ++++  option %s  : %r ", opt, self.__cD[section][opt])
