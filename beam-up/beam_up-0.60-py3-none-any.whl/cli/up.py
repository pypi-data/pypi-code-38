from beam import Site
from beam.config import load_config

import logging
import click
import os

logger = logging.getLogger(__name__)

@click.command("up")
@click.option("--site", default=None)
def up(site):
    if site is None:
        for site in ['site.yml', 'src/site.yml']:
            if os.path.exists(site):
                break
    if not os.path.exists(site):
        logger.error("Site configuration not found.")
        return -1
    config = load_config(site)
    site = Site(config)
    site.build()

