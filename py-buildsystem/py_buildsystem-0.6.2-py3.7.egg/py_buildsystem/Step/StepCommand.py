import os
import subprocess

from py_buildsystem.common import logger

from py_buildsystem.Step.Step import Step


class StepCommand(Step):

    def __init__(self, step_config, step_name):
        self.configuration = step_config
        self._check_config()

        self.step_name = step_name

    def _check_config(self):
        try:
            self.__command_execution_location = self.configuration["location"]
        except KeyError:
            logger.warning("location not set, executing from current directory.")
            self.__command_execution_location = "./"

        try:
            self.__commands = self.configuration["commands"]
        except KeyError:
            logger.error("no commands given.")
            exit(-1)

    def get_type(self):
        return "command"

    def perform(self):
        base_location = os.getcwd()
        logger.debug("Changing directory to " + self.__command_execution_location)
        os.chdir(self.__command_execution_location)

        for command in self.__commands:
            logger.debug("Calling " + command)
            if command.startswith("cd "):  # TODO: To be done better.
                os.chdir(command.replace("cd ", ""))
            else:
                self.return_code = subprocess.call(command, shell=True)

        logger.debug("Changing directory to " + base_location)
        os.chdir(base_location)

