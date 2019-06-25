#!/usr/bin/env python3

import re
from stacklift.templates_config import TemplatesConfig, StackDesiredState
from stacklift.read_config import yaml_ordered_load
from stacklift.global_config import GlobalConfig

ALL_KEYS = ["StackName",
            "Region",
            "CloudFormationRoleExport",
            "ChangesetDesiredState",
            "Capabilities",
            "DeployFunction",
            "DeployBucketName",
            "Parameters"]
REQUIRED_KEYS = ["StackName",
                 "Region"]


class TemplateParameter:
    def __init__(self, all, required):
        self.all = all
        self.required = required


def parse_template(path):
    with open(path) as f:
        body = f.read()
        before_resources = re.sub('^(Resources|Conditions):.*', '', body, flags=(re.MULTILINE | re.DOTALL))
        template = yaml_ordered_load(before_resources)

    if "Parameters" not in template:
        return TemplateParameter([], [])

    parameters = template["Parameters"]

    all = []
    requires = []
    for key in parameters:
        all.append(key)

        if "Default" not in parameters[key]:
            requires.append(key)

    return TemplateParameter(all, requires)


def parse_templates(config_path, override_module_dir):
    global_config = GlobalConfig(config_path)
    templates_config_path = global_config.get_templates_path(override_module_dir)
    templates_config = TemplatesConfig(templates_config_path)

    template_parameters = {}
    for group_name in templates_config.get_group_names():
        for name in templates_config.get_group_template_names(group_name):
            template_config = templates_config.get_template_config(group_name, name)
            if template_config.get_stack_desired_state() == StackDesiredState.DELETED:
                template_parameters[name] = TemplateParameter([], [])
            else:
                template_parameters[name] = parse_template(template_config.get_template_path())
    return template_parameters


def is_list_ordered(all_list, actual_list):
    key_order_map = {k: i + 1 for i, k in enumerate(all_list)}
    actual_orders = [key_order_map.get(k) or 0 for k in actual_list]
    return actual_orders == sorted(actual_orders)


class Validator:
    def __init__(self):
        self.error_count = 0

    def add_error(self, config_path, section_name, message):
        print("%s:%s: %s" % (config_path, section_name, message))
        self.error_count += 1

    def validate_config(self, config_path, template_parameters):
        with open(config_path) as f:
            config = yaml_ordered_load(f)
        common = config.get("Common") or {}

        # TODO: create test
        for k in set(common.keys()) - set(ALL_KEYS):
            self.add_error(config_path, "Common", "Key '{}' is not supported".format(k))

        for k in [k for k in common if not isinstance(common[k], str)]:
            self.add_error(config_path, "Common", "Key '{}' is not a string: {}".format(k, common[k]))

        if not is_list_ordered(ALL_KEYS, common.keys()):
            self.add_error(config_path, "Common", "Key must be ordered: {}".format(", ".join(ALL_KEYS)))

        sections = config["Stacks"]
        for section_name in sections:
            if section_name not in template_parameters:
                self.add_error(config_path, section_name, "Invalid section name")
                continue

            section = sections[section_name]
            for k in (set(section.keys()) - set(ALL_KEYS)):
                self.add_error(config_path, section_name, "Key '{}' is not supported".format(k))

            for k in [k for k in section if k != "Parameters" and not isinstance(section[k], str)]:
                self.add_error(config_path, section_name, "Key '{}' is not a string: {}".format(k, section[k]))

            if not is_list_ordered(ALL_KEYS, section.keys()):
                self.add_error(config_path, section_name, "Keys must be ordered: {}".format(", ".join(ALL_KEYS)))

            merged = common.copy()
            merged.update(section)
            section_params = merged.get("Parameters") or {}

            for k in (set(REQUIRED_KEYS) - merged.keys()):
                self.add_error(config_path, section_name, "Key '{}' is required".format(k))

            template_parameter = template_parameters[section_name]
            for k in set(template_parameter.required) - set(section_params.keys()):
                self.add_error(config_path, section_name, "Parameter '{}' is required".format(k))

            for k in set(section_params.keys()) - set(template_parameter.all):
                self.add_error(config_path, section_name, "Parameter '{}' is not supported".format(k))

            if not is_list_ordered(template_parameter.all, section_params.keys()):
                self.add_error(config_path, section_name, "Parameters must be ordered: {}".format(", ".join(template_parameter.all)))


def validate_configs(override_module_dir, config_files):
    validator = Validator()
    for config_path in config_files:
        template_parameters = parse_templates(config_path, override_module_dir)
        validator.validate_config(config_path, template_parameters)

    print("%d error(s)." % (validator.error_count))
    if validator.error_count > 0:
        exit(1)
