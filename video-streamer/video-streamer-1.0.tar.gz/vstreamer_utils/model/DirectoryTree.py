import pathlib
import pickle

import vstreamer_utils
from vstreamer_utils import model


class DirectoryTree:
    def __init__(self, directory_root):
        self.directory_root = pathlib.Path(directory_root).absolute()
        self.directories = {}
        if not self.directory_root.is_dir():
            raise ValueError("'%s' is not a directory" % str(self.directory_root))

        self.directories["/"] = model.DirectoryInfo(self.directory_root, self.directory_root)
        for file in self.directory_root.glob("**/*"):
            if file.is_dir():
                relative = "/" + str(file.relative_to(self.directory_root))
                self.directories[relative] = model.DirectoryInfo(file, self.directory_root)

        self.additional_properties = {}
        self.read_info()
        vstreamer_utils.log_info("Created directory tree for '%s'" % directory_root)

    def add_additional_properties(self, file, properties):
        directory = str(pathlib.Path(file).parent)
        if directory not in self.directories:
            raise RuntimeError("'%s' not found in directory tree" % file)
        self.directories[directory].add_additional_properties(file, properties)
        self.additional_properties[file] = properties
        vstreamer_utils.log_info("Added AdditionalEntryProperties for '%s'" % file)
        self.store_info()

    def read_info(self):
        properties_file = self.directory_root / "AdditionalProperties.data"
        if not properties_file.exists():
            return
        with properties_file.open("rb") as file_stream:
            self.additional_properties = pickle.load(file_stream)
            additional_properties = self.additional_properties.copy()
            for file, properties in additional_properties.items():
                directory = str(pathlib.Path(file).parent)
                if directory in self.directories:
                    try:
                        self.directories[directory].add_additional_properties(file, properties)
                    except RuntimeError:
                        del self.additional_properties[file]
            vstreamer_utils.log_info(
                "Read AdditionalEntryProperties from '%s'" % str(properties_file))

    def store_info(self):
        properties_file = self.directory_root / "AdditionalProperties.data"
        with properties_file.open("wb") as file:
            pickle.dump(self.additional_properties, file)
            vstreamer_utils.log_info(
                "Stored AdditionalEntryProperties to '%s'" % str(properties_file))
