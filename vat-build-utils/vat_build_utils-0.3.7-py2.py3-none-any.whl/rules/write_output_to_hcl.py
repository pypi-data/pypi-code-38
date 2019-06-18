import os

from build_utils import utils

def write_output_to_hcl(execution_context, path):
    hcl_output = utils.dump_config_to_hcl(execution_context.output)
    output_file_path = os.path.join(execution_context.dir_path, path)
    utils.write_text_file(output_file_path, hcl_output)
