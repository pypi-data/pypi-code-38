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


class Evidencer:
    def __init__(self):
        self.extractors_plugins_directories = [DefaultDirectory.extractors_plugins()]
        self.extractors_configurations_directory = [DefaultDirectory.extractors_pre_configurations()]

        self._extractors = {}
        self._plugin_manager = PluginManager()
        self._import_extractors()

        self._extractors_pre_configurations = {}
        self._import_extractor_pre_configurations()

    def extract_by_file(self, user_extractors_configurations_file):
        # TODO: key strings to class

        working_directory = os.path.abspath(os.path.dirname(user_extractors_configurations_file))
        user_extractors_configurations = self._read_json_file(user_extractors_configurations_file)

        return self.extract_all(user_extractors_configurations, working_directory)

    def extract_all(self, user_extractors_configurations, working_directory):
        results = []
        for user_extractor_configuration in user_extractors_configurations[ConfigurationKeys.configurations]:
            print(".")
            result = self._extract_one(user_extractor_configuration, working_directory)
            results.append(result)
        print("--")
        return results

    def _import_extractor_pre_configurations(self):
        for directory in self.extractors_configurations_directory:
            for file_configuration in Path(directory).glob(os.path.join(os.path.join("**", "*.json"))):
                self._import_extractor_configuration(file_configuration)

    def _import_extractor_configuration(self, file_configuration):
        configuration = self._read_json_file(file_configuration)
        # TODO: check json schema
        self._extractors_pre_configurations[configuration[ConfigurationKeys.pre_configuration_name]] = configuration

    def _read_json_file(self, file_path):
        with open(file_path) as json_file:
            return json.load(json_file)

    def _import_extractors(self):
        self._plugin_manager.setPluginPlaces(self.extractors_plugins_directories)
        self._plugin_manager.collectPlugins()

    def _extract_one(self, user_extractor_configuration, working_directory):
        extractor_configuration = self._prepare_extractor_configuration(user_extractor_configuration, working_directory)
        extractor = self._plugin_manager.getPluginByName(extractor_configuration[ConfigurationKeys.extractor])
        return extractor.plugin_object.extract(extractor_configuration)

    def _prepare_extractor_configuration(self, user_extractor_configuration, working_directory):
        # TODO: key strings to class
        pre_configuration_name = user_extractor_configuration[ConfigurationKeys.pre_configuration]
        pre_configuration_parameters = self._extractors_pre_configurations[pre_configuration_name][ConfigurationKeys.parameters]

        parameters_merge = jsonmerge.merge(pre_configuration_parameters,
                                           user_extractor_configuration[ConfigurationKeys.parameters])
        return {
            ConfigurationKeys.extractor: user_extractor_configuration[ConfigurationKeys.extractor],
            ConfigurationKeys.parameters: parameters_merge,
            ConfigurationKeys.working_directory: working_directory
        }


if __name__ == "__main__":
    evidencer = Evidencer()
    r = evidencer.extract_by_file("../evidencer.json")
    print(r)
    print(r)
    print(r)




