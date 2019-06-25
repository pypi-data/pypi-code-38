from stacklift.read_config import ConfigReader
import os


class GlobalConfig:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config_reader = ConfigReader(config_path)

    def get_module_dir(self):
        return os.path.join(os.path.dirname(self.config_path), self.config_reader.get_global_value("ModuleDir"))

    def get_templates_path(self, override_module_dir=None):
        module_dir = override_module_dir if override_module_dir else self.get_module_dir()
        return os.path.join(module_dir, self.config_reader.get_global_value("Templates"))

    def get_archive_location(self):
        return self.config_reader.get_global_value("ArchiveLocation")
