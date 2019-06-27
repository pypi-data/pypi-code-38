import json
import os
import sys

import click

import storyscript

import xerox

from .utils import find_story_yml, get_app_name_from_yml, get_asyncy_yaml
from .version import compiler_version, version


def echo_support():

    data = {}
    data['cli'] = {}
    data['compiler'] = {}
    data['python'] = {}
    data['app'] = {}
    data['context'] = {}

    data['cli']['version'] = version
    data['cli']['path'] = os.path.dirname(__file__)
    data['compiler']['version'] = compiler_version
    data['compiler']['path'] = os.path.dirname(storyscript.__file__)
    data['python']['path'] = sys.executable
    data['python']['version'] = sys.version.split()[0]
    data['app']['name'] = get_app_name_from_yml()
    data['app']['story.yml'] = get_asyncy_yaml(must_exist=False)
    data['app']['story.yml_path'] = find_story_yml()
    data['context']['cwd'] = os.getcwd()
    data['context']['environ_keys'] = [k for k in os.environ.keys()]
    data['context']['argv'] = sys.argv

    report = json.dumps(data, indent=4)
    click.echo(report)

    # Copy the report to the clipboard!
    try:
        xerox.copy(report)
        click.echo(click.style('Copied to clipboard!', fg='red', bold=True))
    except Exception:
        pass

    # TODO: this.
