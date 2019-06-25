# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import datetime
import six

from .constants import (PROP_EQ_FORMAT_STR, PROP_EXISTS_FORMAT_STR,
                        TAG_EQ_FORMAT_STR, TAG_EXISTS_FORMAT_STR,
                        TYPE_EQ_FORMAT_STR, CREATED_AFTER_FORMAT_STR,
                        STATUS_EQ_FORMAT_STR, NO_CHILD_RUNS_QUERY,
                        TARGET_EQ_FORMAT_STR)
from .expressions import and_join
from .helpers import convert_dict_values


def get_filter_run_type(filter_val):
    if isinstance(filter_val, six.text_type):
        return TYPE_EQ_FORMAT_STR.format(filter_val)
    else:
        raise ValueError("Unknown filter type for run type: {0}".format(type(filter_val)))


def get_filter_run_status(filter_val):
    if isinstance(filter_val, six.text_type):
        return STATUS_EQ_FORMAT_STR.format(filter_val)
    else:
        raise ValueError("Unknown filter type for run status: {0}".format(type(filter_val)))


def get_filter_include_children(filter_val):
    if isinstance(filter_val, bool):
        return None if filter_val else NO_CHILD_RUNS_QUERY  # Include children = no filter
    else:
        raise ValueError("Unknown filter type for include_children: {0}".format(type(filter_val)))


def get_filter_run_created_after(filter_val):
    if isinstance(filter_val, datetime.datetime):
        return CREATED_AFTER_FORMAT_STR.format(filter_val)
    else:
        raise ValueError("Unknown filter type for run type: {0}".format(type(filter_val)))


def get_filter_run_tags(filter_val):
    if isinstance(filter_val, six.text_type):
        return get_filter_run_has_tag(filter_val)
    elif isinstance(filter_val, dict):
        return get_filter_run_tag_equals(filter_val)
    else:
        raise ValueError("Unknown filter type for run tags: {0}".format(type(filter_val)))


def get_filter_run_has_tag(tag):
    return TAG_EXISTS_FORMAT_STR.format(tag)


def get_filter_run_tag_equals(tag_value_dict):
    value_dict = convert_dict_values(tag_value_dict)
    exprs = [TAG_EQ_FORMAT_STR.format(tag, value)
             for tag, value in value_dict.items()]
    return and_join(exprs)


def get_filter_run_properties(filter_val):
    if isinstance(filter_val, six.text_type):
        return get_filter_run_has_property(filter_val)
    elif isinstance(filter_val, dict):
        return get_filter_run_property_equals(filter_val)
    else:
        raise ValueError("Unknown filter type for run properties: {0}".format(type(filter_val)))


def get_filter_run_has_property(property_key):
    return PROP_EXISTS_FORMAT_STR.format(property_key)


def get_filter_run_property_equals(prop_value_dict):
    value_dict = convert_dict_values(prop_value_dict)
    exprs = [PROP_EQ_FORMAT_STR.format(tag, value)
             for tag, value in value_dict.items()]
    return and_join(exprs)


def get_filter_run_target_name(target_name):
    return TARGET_EQ_FORMAT_STR.format(target_name)
