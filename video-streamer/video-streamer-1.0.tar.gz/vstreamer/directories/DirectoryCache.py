import copy


class DirectoryCache:
    def __init__(self):
        self._directories = {}
        self._additional_properties = {}

    def store_directory(self, directory_info):
        self._directories[directory_info.path] = directory_info

    def store_additional_properties(self, path, additional_properties):
        self._additional_properties[path] = additional_properties

    def get_directory(self, path):
        if path in self._directories:
            return copy.deepcopy(self._directories[path])
        return None

    def get_additional_properties(self, filepath):
        if filepath in self._additional_properties:
            return copy.deepcopy(self._additional_properties[filepath])
        return None
