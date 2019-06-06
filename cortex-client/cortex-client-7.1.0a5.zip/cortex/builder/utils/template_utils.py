"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import jinja2
import pkg_resources
from pathlib import Path


class TemplateUtils:
    """Python Template utils."""
    @staticmethod
    def render_and_save(to_dir, file_name, template_name, **kwargs):
        """Render Python template and save to file.

        :param to_dir: The directory to write to.
        :param file_name: The name of the file to write to.
        :param template_name: The name of the template to populate.
        :param **kwargs: The key / value pairs to populate the template with.

        :return: None
        """
        file_contents = TemplateUtils.render_template(template_name, **kwargs)
        TemplateUtils.dump_file(to_dir, file_name, file_contents)

    @staticmethod
    def dump_file(to_dir, file_name, file_contents):
        """Writes content to a file.

        :param to_dir: The directory to write to.
        :param file_name: The name of the file to write to.
        :param file_contents: The content to write to the file.

        :return: None
        """
        with Path(to_dir, file_name).open("w") as f:
            f.write(file_contents)

    ## private ##

    @staticmethod
    def render_template(template_name, **kwargs):
        """Render a Python Template.
        
        :param template_name: The name of the template.
        :param **kwargs: The key / value pairs to populate the template with.

        :return: A rendered template.
        """
        contents = TemplateUtils._read_resource(template_name)
        t = jinja2.Template(contents)
        return t.render(**kwargs)

    @staticmethod
    def _read_resource(name):
        """Read a cortex builder resource file.
        
        :param name: The name of the file to read.

        :return: The content of the file.
        """
        file_path = pkg_resources.resource_filename("cortex.builder.resources", name)
        with open(file_path) as f:
            contents = f.read()
        return contents