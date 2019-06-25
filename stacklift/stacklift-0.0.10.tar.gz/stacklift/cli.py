#!/usr/bin/env python3

import click
from stacklift.read_config import ReadConfigOptions, read_config
from stacklift.global_config import GlobalConfig
from stacklift.validate_configs import validate_configs
from stacklift.deploy_group import deploy_group
from stacklift.upload_archive import upload_archive
from stacklift.extract_archive import extract_archive


@click.group()
def cli():
    pass


@cli.command(name="read-config")
@click.option("--file", "-f", required=True)
@click.option("--section", "-s", required=True)
@click.option("--default", "-d")
@click.option("--parameter", "-p", is_flag=True, default=False)
@click.argument("key", nargs=1)
def read_config_cli(file, section, default, parameter, key):
    opts = ReadConfigOptions()
    opts.file = file
    opts.section = section
    opts.default = default
    opts.parameter = parameter
    opts.key = key
    read_config(opts)

@cli.command(name="validate-configs")
@click.option("--override-module-dir", "-m")
@click.argument("config-files", nargs=-1)
def validate_config_cli(override_module_dir, config_files):
    validate_configs(override_module_dir=override_module_dir, config_files=config_files)

@cli.command(name="deploy-group")
@click.option("--config-file", "-f", required=True)
@click.option("--group-name", "-g", required=True)
def deploy_group_cli(config_file, group_name):
    deploy_group(config_file=config_file, group_name=group_name)

@cli.command(name="upload-archive")
@click.option("--archive-url", required=True)
@click.argument("archive-path", nargs=1)
def upload_archive_cli(archive_url, archive_path):
    upload_archive(archive_url=archive_url, archive_path=archive_path)

@cli.command(name="extract-archive")
@click.option("--config-file", "-f", required=True)
def extract_archive_cli(config_file):
    extract_archive(config_file=config_file)

@cli.command(name="module-dir")
@click.option("--config-file", "-f", required=True)
def module_dir(config_file):
    print(GlobalConfig(config_file).get_module_dir())


def run():
    cli()

if __name__ == '__main__':
    run()
