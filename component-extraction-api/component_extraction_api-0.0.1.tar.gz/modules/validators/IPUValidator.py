import collections
import logging
import json
import ast

from inspect import isclass

from runnable_pkg.modules.validators.AbstractValidator import AbstractValidator
from runnable_pkg.modules.validators.JsonKeys import JsonKeys


class IPUValidator(AbstractValidator):

    def __init__(self):
        AbstractValidator.__init__(self)

    @staticmethod
    def parse(file_path):
        """
        TODO: To be removed(We don't pass a file)
        :param file_path:
        :return:
        """
        logging.info("")
        if IPUValidator.file_exist(file_path):
            with open(file_path) as f:
                try:
                    data = json.loads(f.read())
                except ValueError as e:
                    logging.warning(e)
                else:
                    return data
        return {}

    @staticmethod
    def read_file(file_path):
        """
        Function that reads the file from the file path
        :param file_path: path of the file to read
        :return: content of the file if found
                empty array if not
        """
        with open(file_path) as f:
            logging.info("Opening the file")
            try:
                logging.info("Reading the file")
                data = f.read()
            except FileNotFoundError as e:
                logging.warning(e)
            else:
                logging.info("Returning file content")
                return data
        return []

    @staticmethod
    def return_class_names(file_path):
        """
        Function that returns the class names in a list
        :param file_path: path of the file to read
        :return: List of class names (str)
        """
        logging.info("Reading the content of the file")
        data = IPUValidator.read_file(file_path)
        logging.info("Parsing the content")
        p = ast.parse(data)
        logging.info("Checking for classes name within the file")
        classes = [node.name for node in ast.walk(p) if isinstance(node, ast.ClassDef)]
        return classes

    @staticmethod
    def compare_class_names_with_keys(config):
        """
        Function that validates the IPU
        :param config: the config that is parsed
        :return: True if the Pipeline units keys are the same as the corresponding values
                 False if not
        """
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        pipeline_unit_keys = []
        pipeline_unit_paths = []
        logging.info("Starting IPUValidation")
        parsed_data = IPUValidator.parse(config)
        pipeline_units = parsed_data[JsonKeys.UNITS.value]
        for k, v in pipeline_units.items():
            pipeline_unit_keys.append(k)
            pipeline_unit_paths.append(v)
        for path in pipeline_unit_paths:
            class_name = IPUValidator.return_class_names(path)
            found = compare(class_name, pipeline_unit_keys)
            if not found:
                return found
        return found

    def validate(self, config):
        """
        Function that validates the IPU
        :param config:
        :return: True if valid
                 False if not
        """
        valid = IPUValidator.compare_class_names_with_keys(config)
        if valid :
            logging.info("IPU valid")
        else:
            logging.warning("IPU invalid")
        return valid

