from py_buildsystem.common import logger

from py_buildsystem.Step.StepFactory import StepFactory
from py_buildsystem.ConfigReader.ConfigReader import ConfigReader


class Project(ConfigReader):

    def __init__(self, project_config_file, toolchain):
        logger.debug("Reading project configuration file.")
        ConfigReader.__init__(self, project_config_file)

        self.__project_name = ((project_config_file.replace("\\", "/")).split("/")[-1]).split(".")[0]  # take the file name as a projecct name

        self.__toolchain = toolchain

        self.__toolchain.get_compiler().set_defines(self.__defines)
        self.__toolchain.get_compiler().set_includes(self.__includes)

        self._parse_steps_list()

        self.run()

    def _check_config(self):
        try:
            self.__defines = self.configuration["defines"]
        except KeyError:
            logger.debug("defines not set")
            self.__defines = []

        try:
            self.__includes = self.configuration["includes"]
        except KeyError:
            logger.debug("defines not set")
            self.__includes = []

        try:
            self.__steps_list = self.configuration["steps"]
        except KeyError:
            logger.debug("steps not set")
            self.__steps_list = []

        self.__steps = []

    def get_project_name(self):
        return self.__project_name

    def get_defines(self):
        return self.__defines

    def get_includes(self):
        return self.__includes

    def _parse_steps_list(self):
        for step in self.__steps_list:
            self.__steps.append(StepFactory.create(step, object_to_inject=self.__toolchain))

    def run(self):
        logger.info("Starting " + self.__project_name + " project")

        for step in self.__steps:
            logger.info("Performing " + step.get_type() + " " + step.get_name())
            step.perform()
            logger.info("Finished " + step.get_type() + " " + step.get_name())

    def get_exit_codes(self):
        return [step.get_exit_code() for step in self.__steps]
