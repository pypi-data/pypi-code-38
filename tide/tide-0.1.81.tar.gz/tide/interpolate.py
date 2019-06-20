from config import Config
from jinja2 import Template
from logging_decorator import logging

@logging
def interpolate_variables(message):
    template = Template(message)
    config_variables = Config().get()["variables"]
    if config_variables:
        return template.render(config_variables)
