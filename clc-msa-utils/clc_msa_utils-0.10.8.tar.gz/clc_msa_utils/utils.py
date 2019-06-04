import logging
from copy import deepcopy
from decimal import Decimal

from boto3.dynamodb import types

logger = logging.getLogger('utils')


def dict_replace_empty_values(in_dictionary,
                              process_none_values=False,
                              clone_dict=False,
                              remove_values=False,
                              replace_with=None,
                              replace_float_with_decimal=False):
    if type(in_dictionary) is not dict:
        raise Exception("Value provided must be a dictionary.")

    if clone_dict:
        logger.debug("Cloning dictionary")
        in_dictionary = deepcopy(in_dictionary)

    keys_to_process = []

    for key in in_dictionary.keys():
        value = in_dictionary.get(key)
        logger.debug("Processing key '{0}' of type '{1}'".format(key, type(value).__name__))
        if process_none_values and value is None:
            logger.debug("Adding key '{0}' to keys to process.".format(key))
            keys_to_process.append(key)

        if type(value) is dict:
            logger.debug("Calling dict_replace_empty_values for keys '{0}'.".format(key))
            dict_replace_empty_values(value,
                                      process_none_values=process_none_values,
                                      clone_dict=False,
                                      remove_values=remove_values,
                                      replace_with=replace_with,
                                      replace_float_with_decimal=replace_float_with_decimal)
        elif type(value) in [list, set]:
            index = 0
            if type(value) is set:
                value = list(value)
                in_dictionary[key] = value
            for item in value:
                if type(item) is dict:
                    dict_replace_empty_values(item,
                                              process_none_values=process_none_values,
                                              clone_dict=False,
                                              remove_values=remove_values,
                                              replace_with=replace_with,
                                              replace_float_with_decimal=replace_float_with_decimal)
                elif replace_float_with_decimal:
                    if type(item) is float:
                        logger.debug("Converting '{0}' to Decimal".format(key))
                        value[index] = Decimal(str(item))
                    elif type(item) is str:
                        if len(item.strip()) == 0:
                            value[index] = replace_with
                    elif type(item) in [int, Decimal, types.Binary, types.Decimal, type(None)]:
                        logger.debug("Type {0} is a valid boto3 type, not modifying value.".format(str(type(item))))
                    else:
                        logger.debug("Converting {0} to a str".format(str(type(item))))
                        value[index] = str(item)

                index = index + 1
        else:
            logger.debug("Convert non boto types? {0}".format(str(replace_float_with_decimal)))
            _process_primitives(in_dictionary, key, value, keys_to_process, replace_float_with_decimal)
            logger.debug("No special handing required for key '{0}' for its type.".format(key))

    for key_to_process in keys_to_process:
        if remove_values:
            logger.debug("Removing key '{0}'.".format(key_to_process))
            in_dictionary.pop(key_to_process)
        else:
            logger.debug("Replacing key '{0}' with '{1}'.".format(key_to_process, replace_with))
            in_dictionary[key_to_process] = replace_with

    return in_dictionary


def _process_primitives(in_dictionary, key, value, keys_to_process, replace_float_with_decimal):
    if type(value) is str:
        if len(value.strip()) == 0:
            logger.debug("Adding key '{0}' to keys to process.".format(key))
            keys_to_process.append(key)
    else:
        logger.debug("Value {0}, of type {1}, should I convert? {2}".
                     format(str(value), str(type(value)), str(replace_float_with_decimal)))
        if replace_float_with_decimal:
            logger.debug("Converting '{0}' to boto3 types".format(key))
            in_dictionary[key] = _to_boto3_type(value)
        logger.debug("Value for key '{0}' is not blank.".format(key))


def _to_boto3_type(value):
    if type(value) in [float]:
        boto3_value = Decimal(str(value))
    elif type(value) in [int, bool, types.Decimal, types.Binary, Decimal, type(None)]:
        boto3_value = value
    elif type(value) in [set, list]:
        logger.debug("Processing a {0}".format(str(type(value))))
        a_set = set()
        for i in value:
            if type[i] is str:
                if len(i.strip()) == 0:
                    logger.debug("Converting emtpy srt to None")
                    a_set.add(None)
                else:
                    logger.debug("Adding {0} to set".format(str(type(i))))
                    a_set.add(i)
            elif type(i) in [float]:
                logger.debug("Converting {0} to Decimal".format(str(type(i))))
                a_set.add(Decimal(str(i)))
            elif type(i) in [int, Decimal, types.Binary, types.Decimal]:
                logger.debug("Adding {0} to set".format(str(type(i))))
                a_set.add(i)
            else:
                logger.debug("Converting {0} to a str".format(str(type(i))))
                a_set.add(str(i))
    else:
        boto3_value = str(value)
    return boto3_value


def log_dict_types(a_dict, prefix="", types=None, use_logger=logger, print_no_type_message=False):
    was_logged = False
    for key in a_dict.keys():
        if prefix:
            fq_key = "{0}.{1}".format(prefix, key)
        else:
            fq_key = "{0}".format(key)
        value = a_dict.get(key)
        value_type = type(value).__name__
        if not types or value_type in types:
            use_logger.info("'self.{0}' is a '{1}'".format(fq_key, value_type))
            was_logged = True
        if type(value) is dict:
            log_dict_types(value, prefix=fq_key, types=types, use_logger=use_logger)
    if not was_logged:
        if prefix:
            self_prefix = "self."
        else:
            self_prefix = "self"
        if print_no_type_message:
            use_logger.info("'{0}' has no type in {1}".format("{0}{1}".format(self_prefix, prefix), str(types)))
