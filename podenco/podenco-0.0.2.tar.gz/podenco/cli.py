"""Console script for podenco."""

import click

from podenco.use_cases.podcast_generate import PodcastGenerate
from podenco.repositories.yaml_repository import YamlRepository


@click.command()
@click.argument("filename")
@click.argument("output_path")
def generate(filename, output_path):
    """Generate static site file structure."""
    with open(filename) as yaml_file:
        yaml_str = yaml_file.read()
    repository = YamlRepository(yaml_str)
    podcast_generate_uc = PodcastGenerate(repository, output_path)
    podcast_generate_uc.execute()
    click.echo("Done!")


@click.group()
def main(args=None):
    """Console script for podenco."""


main.add_command(generate)
