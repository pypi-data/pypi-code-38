# -*- coding: utf-8 -*-
import click

from spell.cli.commands.cluster_aws import create_aws, eks_init, add_bucket, update
from spell.cli.commands.cluster_gcp import create_gcp, gke_init


@click.group(name="cluster", short_help="Manage external clusters",
             help="Manage external clusters on Spell",
             hidden=True)
@click.pass_context
def cluster(ctx):
    pass


# register aws subcommands
cluster.add_command(create_aws)
cluster.add_command(eks_init)
cluster.add_command(add_bucket)
cluster.add_command(update)

# register gcp subcommands
cluster.add_command(create_gcp)
cluster.add_command(gke_init)
