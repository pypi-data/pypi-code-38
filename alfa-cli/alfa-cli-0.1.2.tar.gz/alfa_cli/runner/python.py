import os
import json
import importlib
import sys

from alfa_sdk.common.exceptions import AlfaConfigError


class PythonRunner:
    def __init__(self, invoke_config):
        self.invoke_config = invoke_config
        self.handler = self.import_handler()

    #

    def get_handler_definition(self, invoke_config):
        ERROR_MESSAGE = "invoke function handler not defined"

        invoke_config_function = invoke_config.get("function")
        if not invoke_config_function:
            raise AlfaConfigError(message='Invalid configuration', error=ERROR_MESSAGE)

        invoke_config_handler = invoke_config_function.get("handler")
        if not invoke_config_handler:
            raise AlfaConfigError(message='Invalid configuration', error=ERROR_MESSAGE)

        return invoke_config_handler

    def get_handler_parameters(self, invoke_config):
        ERROR_MESSAGE = "invoke function parameters not defined"

        invoke_config_function = invoke_config.get("function")
        if not invoke_config_function:
            raise AlfaConfigError(message='Invalid configuration', error=ERROR_MESSAGE)

        invoke_config_parameters = invoke_config_function.get("parameters")
        if not invoke_config_parameters:
            raise AlfaConfigError(message='Invalid configuration', error=ERROR_MESSAGE)

        return invoke_config_parameters

    #

    def import_handler(self):
        sys.path.insert(0, os.path.join(os.getcwd(), 'invoke'))

        handler_definition = self.get_handler_definition(self.invoke_config)
        module_name = '.'.join(handler_definition.split('.')[:-1])
        function_name = handler_definition.split(".")[-1]

        module = importlib.import_module(module_name)
        invoke = getattr(module, function_name)

        return invoke

    #

    def run(self, problem):
        arguments = self.map_problem_to_arguments(problem)
        return self.handler(*arguments)

    def map_problem_to_arguments(self, problem):
        parameters = self.get_handler_parameters(self.invoke_config)

        try:
            problem = open(problem, "r").read()
        except:
            problem = json.loads(problem)

        return self.get_parameter_values(parameters, problem)

    def get_parameter_values(self, parameters, problem):
        arguments = []
        for parameter in parameters:
            if isinstance(parameter, dict):
                for name, default_value in parameter.items():
                    arguments.append(problem.get(name, default_value))
            else:
                arguments.append(problem.get(parameter))

        return tuple(arguments)
