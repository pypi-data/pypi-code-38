import ntpath
from abc import ABCMeta, abstractmethod
from pathlib import Path
import logging


class AbstractValidator(metaclass=ABCMeta):

    def __init__(self):
        logging.basicConfig(filename="cef.log", level=logging.DEBUG)

    def get_file(self):
        """
        gets the file path
        :return: returns the file path
        """
        return self.file_path

    def set_file(self, file_path):
        """
        sets the file path
        :param file_path: the path of the file we want to set
        :return: returns the setted file path.
        """
        self.file_path = file_path

    @staticmethod
    def file_exist(file_path):
        """

        :param file_path: the path of the file that is checked
        :return: returns whether the file exists or not
        """
        file = Path(file_path)
        try:
            file.resolve(strict=True)
        except FileNotFoundError:
            logging.warning("File not found")
            return False
        else:
            logging.info("File found")
            return True

    @staticmethod
    def get_filename_from_path(file_path):
        """
        Returns the name of the file from a given path
        :param file_path: the path that the method retrieves the filename from
        :return: returns the file name from the given path
        """
        try:
            file_name = ntpath.basename(file_path)
            logging.info("Returned name of the file")
        except FileNotFoundError:
            logging.warning("Could not create the file name")
            return ""
        else:
            return file_name

    @abstractmethod
    def validate(self, config):
        return


