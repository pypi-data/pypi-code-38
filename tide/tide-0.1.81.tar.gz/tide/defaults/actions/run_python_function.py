import sys
import importlib
from config import Config
from action_base import action_base
import interpolate as Interpolate

class run_python_function(action_base):

    _command_item = {}
    _buffer_name = {}
    _command_args = {}
    _function_file = ''
    _function_name = ''
    _input_args = {}
    _set_on_return = ''
    _function_module_name = ''
    _function_module = None
    _function = None
    _interpolated_input_args = {}

    def run(self, command_item, buffer_name='', command_args={}):
        self.__set_locals(command_item, buffer_name, command_args)
        self.__set_function_module_locals()
        self.__update_command_args()
        self.__run_function_update_variable()

    def __run_function_update_variable(self):
        function_result = self._function(**self._interpolated_input_args)
        if self._set_on_return:
            Config().get()["variables"][self._set_on_return] = function_result

    def __update_command_args(self):
        if self._command_args:
            self._interpolated_input_args["command_args"] = self._command_args

    def __set_function_module_locals(self):
        self._function_module = importlib.import_module(self._function_module_name)
        self._function = getattr(sys.modules[self._function_module_name], self._function_name)
        self._interpolated_input_args = self.__get_interpolated_args(self._command_item)

    def __set_locals(self, command_item, buffer_name, command_args):
        self._command_item = command_item
        self._buffer_name = buffer_name
        self._command_args = command_args
        self._function_file = self._command_item["function_file"]
        self._function_name = self._command_item["function_name"]
        self._input_args = self._command_item.get("input_args", {})
        self._set_on_return = self._command_item.get("set_on_return", None)
        self._function_module_name = self._function_file.replace(".py", "")

    def __get_interpolated_args(self, command_item):
        input_args = command_item.get("input_args", {})
        interpolated_input_args = {}
        for key, value in input_args.items():
            interpolated_input_args[key] = Interpolate.interpolate_variables(value)
        return interpolated_input_args
