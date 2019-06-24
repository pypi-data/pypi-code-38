from beam import Site
from beam.config import load_config

import logging
import yaml
import click
import os

logger = logging.getLogger(__name__)

@click.command("config")
@click.option("--site", default=None)
def config(site):
    if site is None:
        for site in ['site.yml', 'src/site.yml']:
            if os.path.exists(site):
                break
    if not os.path.exists(site):
        logger.error("Site configuration not found.")
        return -1
    config = load_config(site)
    click.echo(yaml.dump(config))

