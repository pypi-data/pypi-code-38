import yaml
import os
from enum import Enum, unique


@unique
class StackDesiredState(Enum):
    PRESENT = "present"
    DELETED = "deleted"


class TemplateConfig:
    def __init__(self, templates_file_dir, template_config_dict):
        self.templates_file_dir = templates_file_dir
        self.template_config_dict = template_config_dict

    def get_name(self):
        return self.template_config_dict["Name"]

    def get_template_path(self):
        filename = self.template_config_dict.get("Filename")
        return os.path.join(self.templates_file_dir, filename) if filename else None

    def get_function_root(self):
        function_root = self.template_config_dict.get("FunctionRoot")
        return os.path.join(self.templates_file_dir, function_root) if function_root else None

    def get_depends(self):
        return self.template_config_dict.get("Depends") or []

    def get_stack_desired_state(self):
        return StackDesiredState(self.template_config_dict.get("StackDesiredState",
                                                               StackDesiredState.PRESENT.value))


class TemplatesConfig:
    def __init__(self, templates_config_path):
        with open(templates_config_path) as f:
            self.templates_config = yaml.load(f)
        self.templates_file_dir = os.path.dirname(templates_config_path)

    def get_group_names(self):
        return self.templates_config["Groups"].keys()

    def get_group(self, group_name):
        group = self.templates_config["Groups"].get(group_name)
        if group is None:
            raise RuntimeError("Group {} is not defined.".format(group_name))
        return group

    def get_templates_dict(self, group_name):
        group = self.get_group(group_name)
        return {template["Name"]: template for template in group["Templates"]}

    def get_template_config(self, group_name, template_name):
        template_dict = self.get_templates_dict(group_name)

        template = template_dict.get(template_name)
        if not template:
            raise RuntimeError("Template {} is not found.".format(template_name))

        return TemplateConfig(self.templates_file_dir, template)

    def get_group_template_names(self, group_name):
        template_dict = self.get_templates_dict(group_name)
        return template_dict.keys()
