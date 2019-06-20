import os
from action_base import action_base
from config import Config
import path_helpers as Ph
import jinja2

class display_template(action_base):

    def run(self, command_item, buffer_name=''):
        template_paths = Ph.get_paths_for_plugin('templates')
        template_filename = command_item.get("filename", '')
        for templates_path in template_paths:
            template_filename_path = os.path.join(templates_path, template_filename)
            if os.path.isfile(template_filename_path):
                self.__process_template_file(buffer_name, templates_path, template_filename)
                break

    def __process_template_file(self, buffer_name, templates_path, template_filename):
            template_loader = jinja2.FileSystemLoader(searchpath=templates_path)
            template_env = jinja2.Environment(loader=template_loader)
            template = template_env.get_template(template_filename)
            config_variables = Config().get()["variables"]
            output_text = template.render(config_variables)
            if output_text:
                output_text_array = output_text.split('\n')
                Config().get()["internal"]["buffer_caches"][buffer_name] = output_text_array
