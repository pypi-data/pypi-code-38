import os

from jinja2 import Environment, FileSystemLoader
from missinglink.crypto import Asymmetric
from missinglink.resource_manager.docker.utils import is_windows_containers

cur_path = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(cur_path))


def render(name, **kwargs):
    template = env.get_template(name)
    result = template.render(**kwargs)
    return result


def build_user_command(**kwargs):
    template = 'machine_bootstrap.{}.jinja2'.format(_get_template_type())
    return Asymmetric.bytes_to_b64str(render(template, **kwargs))


def build_root_command(**kwargs):
    template = 'root_bootstrap.{}.jinja2'.format(_get_template_type())
    return Asymmetric.bytes_to_b64str(render(template, **kwargs))


def _get_template_type():
    return 'cmd' if is_windows_containers() else 'sh'
