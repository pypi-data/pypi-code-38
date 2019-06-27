# -*- coding: utf-8 -*-

"""Console script for gaeconf."""
import sys
import click

from .gaeconf import AppEngineFlexibleConfig, AppEngineStandardConfig, load_yaml_classes


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '-m', '--config-module', 'config_module_path',
    envvar='GAECONF_CONFIG_MODULE', metavar='<config_module_path>',
    type=click.Path(exists=True), required=True,
    help='config module path: ie: staging.yaml'
)
@click.option(
    '-s', '--service', 'service', envvar='GAECONF_SERVICE', metavar='<service>',
    required=True, help='GAE service name'
)
def main(config_module_path, service):
    """
    Gaeconf is a CLI that parses a yaml file and outputs a Google App Engine
    configuration file.
    
    GAE standard reference: https://cloud.google.com/appengine/docs/standard/python3/config/appref
    GAE flexible reference: https://cloud.google.com/appengine/docs/flexible/python/reference/app-yaml
    """
    services = load_yaml_classes(config_module_path)
    try:
        service_config_class = services[service]
        if getattr(service_config_class, 'env', 'standard') == 'flex':
            base_class = AppEngineFlexibleConfig
        else:
            base_class = AppEngineStandardConfig

        service_class = type(service, (service_config_class, base_class), {})
        click.echo(service_class().to_yaml())
    except KeyError:
        click.echo(f"Service '{service}' not found")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
