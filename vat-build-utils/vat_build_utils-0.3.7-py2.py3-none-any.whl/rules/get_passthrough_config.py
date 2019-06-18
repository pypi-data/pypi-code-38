import os

from vat_utils.config import create_config_client_v2

def get_passthrough_config(execution_context):
    old_working_directory = os.getcwd()
    try:
        os.chdir(execution_context.dir_path)

        config_source = execution_context.build_context.get_rule_config_value('passthrough_config_source')
        config_client = create_config_client_v2(config_source)
        return config_client.get_root_json_value()
    finally:
        os.chdir(old_working_directory)
