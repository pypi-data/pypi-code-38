# -*- coding: utf-8 -*-
import os
from jinja2 import Environment, FileSystemLoader

from cpbox.tool import file
from cpbox.tool import utils

def render_to_str(template_file, data):
    if not os.path.isfile(template_file):
        raise Exception('template file not found: ' +  template_file)
    template_dir = os.path.dirname(template_file)
    template_name = os.path.basename(template_file)
    file_loader = FileSystemLoader(template_dir)
    env = Environment(loader=file_loader)
    template = env.get_template(template_name)
    result = template.render(data)
    return result

def render_to_file(template_file, data, target_file):
    if not os.path.isfile(template_file):
        raise Exception('template file not found: ' +  template_file)
    ret = render_to_str(template_file, data)
    file.file_put_contents(target_file, ret)
    return ret

def render(template_file, config_file=None, config_section=None, extra_kvs=None, output_file=None, output_dir=None, **kwargs):
    data = utils.load_yaml_config(config_file, config_section, extra_kvs)
    if not output_file and not output_dir:
        raise Exception('should specify output_file or output_dir')

    if output_file is not None:
        output_file = output_file
    else:
        output_file = output_dir.rstrip('/') + '/' + os.path.basename(template_file)
    return render_to_file(template_file, data, output_file)

def render_str(patten, data):
    env = Environment(keep_trailing_newline=True)
    patten = file.ensure_decode(patten)
    s = env.from_string(patten)
    ret = s.render(data)
    return ret
