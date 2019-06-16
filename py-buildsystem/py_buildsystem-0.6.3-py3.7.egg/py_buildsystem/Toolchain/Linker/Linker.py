import os
import time
import subprocess

from py_buildsystem.common import logger


class Linker:

    def __init__(self, linker_path, output_flag, command_line_file):
        self.__linker_path = linker_path
        self.__output_flag = output_flag
        self.__command_line_file = command_line_file
        self.__flags = []

    def set_flags(self, list_of_flags):
        self.__flags = list_of_flags

    def link(self, list_of_files, output_file, list_of_additional_flags=[]):
        filename = str(int(time.time())) + "linker_file"

        with open(filename, "w") as comand_line_file:

            logger.debug("Created " + filename)

            for file in list_of_files:
                comand_line_file.write(" " + file)
                logger.debug("Added " + file)

        logger.debug("Linking {}".format(list_of_files))
        command = [self.__linker_path] + self.__flags + [self.__command_line_file + filename] + [self.__output_flag + output_file] + list_of_additional_flags
        exit_code = subprocess.call(command)

        os.remove(filename)
        logger.debug("Removed " + filename)

        return exit_code
