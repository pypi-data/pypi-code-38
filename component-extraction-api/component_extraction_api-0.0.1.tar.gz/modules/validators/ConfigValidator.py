import logging
import json

from runnable_pkg.modules.validators.AbstractValidator import AbstractValidator
from runnable_pkg.modules.validators.JsonKeys import JsonKeys
import collections

class ConfigValidator(AbstractValidator):

    def __init__(self):
        AbstractValidator.__init__(self)

    @staticmethod
    def is_file_configured_correctly(parsed_data):
        """

        :param parsed_data: the data that is compared to the desired JsonKeys.
        :return: returns whether json_keys is configured correctly by checking if it has the desired keys and values
        """
        json_keys = (JsonKeys.UNITS.value in parsed_data and JsonKeys.ORDER.value in parsed_data)
        if json_keys:
            logging.info("File is configured correctly")
        else:
            logging.warning("Could not find the right keys in the json file")
        return json_keys

    @staticmethod
    def is_pipeline_order_valid(config):
        """
        :param config: the config parsed to check whether pipeline order matches the given specifications
        :return: returns whether the pipeline order is valid or not
        """
        if ConfigValidator.is_file_configured_correctly(config):
            pipeline_order = config[JsonKeys.ORDER.value]
            pipeline_units = config[JsonKeys.UNITS.value]
            pipeline_unit_keys = set(k for k, _ in pipeline_units.items())
            return set(pipeline_order).issubset(pipeline_unit_keys)

    @staticmethod
    def is_pipeline_unit_valid(config):
        """

        :param config: the config parsed to check whether pipeline units match the given specifications
        :return: returns whether or not the IPU specified in the config.json exists
        """
        if ConfigValidator.is_pipeline_order_valid(config):
            logging.info("Parsing the data from the Json config")
            pipeline_units = config[JsonKeys.UNITS.value]
            logging.info("Checking if the IPU specified in the config.json exists")
            return all(ConfigValidator.file_exist(v) for _, v in pipeline_units.items())

    def validate(self, config):
        """

        :param config: the config parsed to the methods called in validate to verify its configuration
        :return: returns the result of the other methods to provide if the config is configured correctly
        """
        configured_correctly = ConfigValidator.is_pipeline_unit_valid(config)
        if configured_correctly:
            logging.info("File validated correctly")
        else:
            logging.error("Could not validate the file")
        return configured_correctly

