import subprocess

from py_buildsystem.common import logger


class Compiler():

    def __init__(self, compiler_path, define_flag, output_flag,
                 compile_flag, include_flag):

        self.__compiler_path = compiler_path
        self.__define_flag = define_flag
        self.__output_flag = output_flag
        self.__compile_flag = compile_flag
        self.__include_flag = include_flag

        self.__flags = []
        self.__defines = []
        self.__includes = []

    def set_flags(self, list_of_flags):
        self.__flags = list_of_flags

    def set_defines(self, list_of_defines):
        self.__defines = list_of_defines

    def set_includes(self, list_of_includes):
        self.__includes = list_of_includes

    def compile(self, list_of_files, output_directory, list_of_additional_flags=[],
                list_of_additional_defines=[], list_of_additionals_includes=[]):

        flags = self.__flags + list_of_additional_flags + [self.__compile_flag]
        defines = self._compose_defines(self.__defines + list_of_additional_defines)
        includes = self._compose_includes(self.__includes + list_of_additionals_includes)

        for file in list_of_files:
            output_file_name = file.split("/")[-1]  # take the file name
            output_file_name = output_file_name.split(".")[0] + ".o"  # change expention to ".o"

            output_flag = self.__output_flag + "/".join([output_directory, output_file_name])

            logger.debug("Compiling: " + file)
            command = [self.__compiler_path] + flags + defines + includes + [output_flag] + [file]
            return subprocess.call(command)

    def _compose_defines(self, list_of_defines):
        composed_defines = []

        for define in list_of_defines:
            composed_defines.append(self.__define_flag + define)

        return composed_defines

    def _compose_includes(self, list_of_includes):
        composed_includes = []

        for include in list_of_includes:
            composed_includes.append(self.__include_flag + include)

        return composed_includes
