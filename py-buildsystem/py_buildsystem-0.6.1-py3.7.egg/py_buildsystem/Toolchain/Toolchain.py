import os
import yaml
import subprocess

from py_buildsystem.common import logger

from py_buildsystem.Toolchain.Linker.Linker import Linker
from py_buildsystem.Toolchain.Compiler.Compiler import Compiler
from py_buildsystem.ConfigReader.ConfigReader import ConfigReader

path_to_configs = os.path.dirname(__file__).replace("\\", "/") + "/ToolchainsConfigs"


class Toolchain(ConfigReader):

    def __init__(self, config_yaml_file, path_to_toolchain=""):

        logger.debug("Reading toolchain configuration file.")
        ConfigReader.__init__(self, config_yaml_file)

        self._check_compiler_config_file()

        self.__linker_path = os.path.join(path_to_toolchain, self.__linker_name).replace("\\", "/")
        self.__compiler_path = os.path.join(path_to_toolchain, self.__compiler_name).replace("\\", "/")

        self._check_toolchain_path()

        self.__compiler = Compiler(self.__compiler_path, self.__define_flag, self.__output_flag,
                                   self.__compile_flag, self.__include_flag)

        self.__compiler.set_flags(self.__compiler_flags)

        self.__linker = Linker(self.__linker_path, self.__output_flag, self.__command_line_file)
        self.__linker.set_flags(self.__linker_flags)

    def get_compiler(self):
        return self.__compiler

    def get_linker(self):
        return self.__linker

    def _check_config(self):
        try:
            self.__choosen_compiler = self.configuration["compiler"]
        except KeyError:
            logger.error("You must provide compiler name in a compiler configuration file")
            exit(-1)

        try:
            self.__compiler_flags = self.configuration["compiler_flags"]
        except KeyError:
            logger.warning("no compiler_flags_set")
            self.__compiler_flags = []

        try:
            self.__linker_flags = self.configuration["linker_flags"]
        except KeyError:
            logger.warning("no linker_flags")
            self.__linker_flags = []

    def _check_compiler_config_file(self):
        try:
            with open(os.path.join(path_to_configs, self.__choosen_compiler + ".yaml").replace("\\", "/"), "r") as compiler_config_file:
                compiler_config = yaml.load(compiler_config_file)

        except FileNotFoundError:
            logger.error("Configuration file for the compiler was not found.")
            exit(-1)

        self.__compiler_name = compiler_config["compiler"]
        self.__linker_name = compiler_config["linker"]

        self.__define_flag = compiler_config["define_flag"]
        self.__output_flag = compiler_config["output_flag"]
        self.__compile_flag = compiler_config["compile_flag"]
        self.__include_flag = compiler_config["include_flag"]
        self.__version_flag = compiler_config["version_flag"]
        self.__command_line_file = compiler_config["comand_line_file"]

    def _check_toolchain_path(self):
        try:
            subprocess.check_output([self.__linker_path, self.__version_flag])
            subprocess.check_output([self.__compiler_path, self.__version_flag])
        except FileNotFoundError:
            logger.error("Can not find the compilers executable, check if the compilers path is correct or if the compiler is in a PATH.")
            exit(-1)
