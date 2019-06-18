import os
from yapsy.PluginManager import PluginManager
from pathlib import Path
import json
import jsonmerge


class DefaultDirectory:

    package_directory = os.path.abspath(os.path.dirname(__file__))

    @classmethod
    def extractors_plugins(cls):
        return os.path.join(cls.package_directory, "extractors")

    @classmethod
    def extractors_pre_configurations(cls):
        return os.path.join(cls.package_directory, "extractors_pre_configurations")


class ConfigurationKeys:
    configurations = "configurations"
    extractor = "extractor"
    pre_configuration = "pre_configuration"
    working_directory = "working_directory"
    parameters = "parameters"
    pre_configuration_name = "pre_configuration_name"
    extraction_name = "extraction_name"


class Extraction:
    def __init__(self, configuration, result):
        self.configuration = configuration
        self.result = result


class EvidencerException(Exception):
    pass


class Evidencer:
    def __init__(self):
        self.extractors_plugins_directories = [DefaultDirectory.extractors_plugins()]
        self.extractors_pre_configurations_directories = [DefaultDirectory.extractors_pre_configurations()]

        self._plugin_manager = PluginManager()
        self._extractors_pre_configurations = {}

    def extract_by_file(self, user_extractors_configurations_file):
        working_directory = os.path.abspath(os.path.dirname(user_extractors_configurations_file))
        user_extractors_configurations = self._read_json_file(user_extractors_configurations_file)
        return self.extract_all(user_extractors_configurations, working_directory)

    def extract_all(self, user_extractors_configurations, working_directory):
        self._import()
        results = {}
        for user_extractor_configuration in user_extractors_configurations[ConfigurationKeys.configurations]:
            result = self._extract_one(user_extractor_configuration, working_directory)
            extraction_name = user_extractor_configuration[ConfigurationKeys.extraction_name]
            results[extraction_name] = result
        return results

    def append_extractors_plugin_directory(self, path):
        self.extractors_plugins_directories.append(path)

    def append_extractors_pre_configurations_directory(self, path):
        self.extractors_pre_configurations_directories.append(path)

    def _import(self):
        self._import_extractors()

        self._extractors_pre_configurations = {}
        self._import_extractor_pre_configurations()

    def _import_extractor_pre_configurations(self):
        for directory in self.extractors_pre_configurations_directories:
            for file_configuration in Path(directory).glob(os.path.join(os.path.join("**", "*.json"))):
                self._import_extractor_pre_configuration_file(file_configuration)

    def _import_extractor_pre_configuration_file(self, file_configuration):
        configuration = self._read_json_file(file_configuration)
        # TODO: check json schema
        self._extractors_pre_configurations[configuration[ConfigurationKeys.pre_configuration_name]] = configuration

    def _read_json_file(self, file_path):
        try:
            with open(file_path) as json_file:
                return json.load(json_file)
        except Exception as e:
            raise EvidencerException("Error during parsing json file '%s'.\n%s" % (file_path, str(e)))

    def _import_extractors(self):
        self._plugin_manager.setPluginPlaces(self.extractors_plugins_directories)
        self._plugin_manager.collectPlugins()

    def _extract_one(self, user_extractor_configuration, working_directory):
        extractor_configuration = self._prepare_extractor_configuration(user_extractor_configuration, working_directory)
        result = self._protected_extraction(extractor_configuration)
        return Extraction(extractor_configuration, result)

    def _protected_extraction(self, extractor_configuration):
        try:
            extractor_name = extractor_configuration[ConfigurationKeys.extractor]
            extractor = self._plugin_manager.getPluginByName(extractor_name)
            return extractor.plugin_object.extract(extractor_configuration)
        except Exception as e:
            raise EvidencerException("Error during extraction. Possible reasons are non-existent extractor or error in extractor.\n%s" % (str(e)))

    def _prepare_extractor_configuration(self, user_extractor_configuration, working_directory):
        pre_configuration_parameters = self._pre_configuration_parameters(user_extractor_configuration)
        parameters_merge = jsonmerge.merge(pre_configuration_parameters,
                                           user_extractor_configuration[ConfigurationKeys.parameters])
        return {
            ConfigurationKeys.extractor: user_extractor_configuration[ConfigurationKeys.extractor],
            ConfigurationKeys.extraction_name: user_extractor_configuration[ConfigurationKeys.extraction_name],
            ConfigurationKeys.parameters: parameters_merge,
            ConfigurationKeys.working_directory: working_directory
        }

    def _pre_configuration_parameters(self, user_extractor_configuration):
        if ConfigurationKeys.pre_configuration in user_extractor_configuration:
            pre_configuration_name = user_extractor_configuration[ConfigurationKeys.pre_configuration]
            try:
                return self._extractors_pre_configurations[pre_configuration_name][ConfigurationKeys.parameters]
            except Exception as e:
                raise EvidencerException("Non-existent pre configuration '%s'.\n%s" % (pre_configuration_name, str(e)))
        else:
            return {}





