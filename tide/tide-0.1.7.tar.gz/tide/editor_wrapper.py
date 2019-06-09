import importlib
import sys
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
from logging_decorator import logging
import path_helpers as Ph

@logging
class EditorWrapper(object):

    _editor_name = None
    _editor_object = None
    _editors_list = []

    def __init__(self, editor_name):
        self._editor_name = editor_name
        self.__set_editor_object()

    def __set_editor_object(self):
        self.__get_editors_list()
        self.__validate_and_create_editor_object()

    def __validate_and_create_editor_object(self):
        if self._editor_name.lower() in self._editors_list:
            return self.__create_editor_object()
        else:
            raise TypeError("error: python file for editor: " + self._editor_name + " is not a valid editor")

    def __create_editor_object(self):
        editor_module = self._editor_name
        importlib.import_module(editor_module)
        self._editor_object = getattr(sys.modules[editor_module], self._editor_name)

    def __get_editors_list(self):
        if not self._editors_list:
            editor_wrapper_paths = Ph.get_paths_for_plugin("editor_wrappers")
            for editors_path in editor_wrapper_paths:
                if editors_path not in sys.path:
                    sys.path.insert(0, editors_path)
                    editor_files = [f for f in listdir(editors_path) if isfile(join(editors_path, f))]
                    for editor_file in editor_files:
                        if Path(editor_file).suffix.lower() == ".py" and editor_file.lower() != "__init__.py":
                            self._editors_list.append(Path(editor_file).stem.lower())

    def get_set_dictionary_value_callback(self):
        return self._editor_object.set_dictionary_value

    def set_editor_dictionary(self, config_dictionary):
        self._editor_object.set_editor_dictionary(self._editor_object, config_dictionary)

    def get_current_buffer_name(self):
        return self._editor_object.get_current_buffer_name(self._editor_object)

    def get_current_buffer_line(self):
        return self._editor_object.get_current_buffer_line(self._editor_object)
