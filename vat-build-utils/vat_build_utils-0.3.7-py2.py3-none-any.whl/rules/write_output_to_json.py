import json
import os

from build_utils import utils

def write_output_to_json(execution_context, path):
    json_output = json.dumps(execution_context.output)
    output_file_path = os.path.join(execution_context.dir_path, path)
    utils.write_text_file(output_file_path, json_output)
