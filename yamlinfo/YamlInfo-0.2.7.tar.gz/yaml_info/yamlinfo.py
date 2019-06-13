"""YamlInfo Main Module"""
# coding=utf-8
import yaml
from logging import info


class YamlInfo:
    """Parse Yaml config file."""

    yaml_info_dict = {}

    def __init__(self, yaml_config_file, option, input_file) -> None:
        """Load yaml information and parse args info."""
        with open(yaml_config_file, 'rb') as input_config_file_object:
            yaml_info_strings = input_config_file_object.read()
        self.yaml_info_dict = yaml.safe_load(yaml_info_strings)
        if option == "projectinfo":
            if input_file == "LICENSE":
                with open("LICENSE") as license_file:
                    license_strings = license_file.read()
                self.yaml_info_dict["license"] = license_strings.strip('\n')
            project_info_data = self.yaml_info_dict["info"]
            project_version_data = self.yaml_info_dict["version"]
            __version__ = "%(major)s.%(minor)s.%(release)s" % project_version_data
            info("Starting " + self.yaml_info_dict["info"]["name"] + " v" + __version__)
            for items in project_info_data:
                info(str(items) + ":" + str(project_info_data[items]))

    def get(self) -> dict:
        """Return parsed project config file as a dict."""
        return self.yaml_info_dict
