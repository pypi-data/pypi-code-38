import yaml
from typing import Dict, Union, List
from swimlane_platform.lib.debug_decorators import debug_function_args, debug_function_return
from swimlane_platform.lib.logger import SplitStreamLogger


class DockerComposeFileManager:

    def __init__(self, logger, docker_compose_file):
        # type: (SplitStreamLogger, str) -> None
        self.logger = logger
        self.docker_compose_file = docker_compose_file
        with open(docker_compose_file) as f:
            self._dict = yaml.safe_load(f)
            f.close()

    @debug_function_return
    @debug_function_args
    def get(self, *attrs):
        # type: (str) -> Union[Dict[str,Union[str, List[str]]], str, None]
        pointer = self._dict
        for attr in attrs:
            if attr not in pointer:
                return None
            pointer = pointer[attr]
        return pointer

    @debug_function_return
    @debug_function_args
    def get_or_create_dict(self, *attrs):
        # type: (str) -> Dict[str, Union[str, List[str]]]
        pointer = self._dict
        for attr in attrs:
            if attr not in pointer or type(pointer[attr]) is not dict:
                pointer[attr] = dict()
            pointer = pointer[attr]
        return pointer

    @debug_function_args
    def append_or_create_list(self, value, *attr):
        # type: (str, str) -> None
        """
        Appends to the list at the end of property values or creates a new list at indicated location.
        :param value: Value to add.
        :param attr: Properties to add it to.
        """
        pointer = self.get_or_create_dict(*attr[:-1])
        last_attr = attr[-1]
        if last_attr not in pointer:
            pointer[last_attr] = [value]
        elif isinstance(pointer[last_attr], list):
            if value not in pointer[last_attr]:
                pointer[last_attr].append(value)
        else:
            raise LookupError('Wrong type found.')

    @debug_function_args
    def subtract_from_list(self, value, *attr):
        # type: (str, str) -> None
        """
        Removes from the list at the end of property chain or ignores if property chain doesn't exists.
        :param value: Value to add.
        :param attr: Properties to add it to.
        """
        pointer = self.get(*attr[:-1])
        if not pointer:
            return
        last_attr = attr[-1]
        if last_attr not in pointer:
            return
        elif isinstance(pointer[last_attr], list):
            if value in pointer[last_attr]:
                pointer[last_attr].remove(value)
        else:
            raise LookupError('Wrong type found.')

    def save(self):
        self.save_as(self.docker_compose_file)

    @debug_function_args
    def save_as(self, file_path):
        with open(file_path, 'w') as fs:
            yaml.safe_dump(self._dict, fs, default_flow_style=False)

    @debug_function_args
    def set(self, value, *attr):
        pointer = self.get_or_create_dict(*attr[:-1])
        last_attr = attr[-1]
        pointer[last_attr] = value

    @debug_function_return
    def get_image_tags(self):
        return [service.get('image') for name, service in self._dict.get('services').items()]
