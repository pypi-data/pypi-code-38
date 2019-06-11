import yaml
import json
import click
from index import spin_this_up


@click.command()
@click.option("--config", help="Path to the config file")
@click.option("--source", help="Path to the source folder")
def main(config, source):
    with open(config) as f:
        config_dict = yaml.safe_load(f)
    INDEX_NAME = config_dict["index"]
    DOC_NAME = config_dict["type"]
    mappings_dict = config_dict["mapping"]
    spin_this_up(INDEX_NAME, DOC_NAME, mappings_dict, source)