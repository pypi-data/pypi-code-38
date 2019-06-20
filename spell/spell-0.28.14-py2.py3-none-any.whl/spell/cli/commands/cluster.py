# -*- coding: utf-8 -*-
import click

from spell.cli.commands.cluster_aws import create_aws, eks_init, add_s3_bucket, update
from spell.cli.commands.cluster_gcp import create_gcp, gke_init, add_gs_bucket
from spell.cli.utils import cluster_utils


@click.group(name="cluster", short_help="Manage external clusters",
             help="Manage external clusters on Spell",
             hidden=True)
@click.pass_context
def cluster(ctx):
    pass


@click.command(name="add-bucket",
               short_help="Adds a cloud storage bucket to SpellFS", hidden=True)
@click.pass_context
@click.option("--bucket", "bucket_name", help="Name of bucket")
@click.option("--cluster-name", help="Name of cluster to add bucket permissions to")
@click.option("-p", "--profile", "profile", default=u"default",
              help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
                   "You will be prompted to confirm the Key and Region are correct before continuing. "
                   "This key will be used to adjust IAM permissions of the role associated with the cluster "
                   "that the bucket is being added to.")
def add_bucket(ctx, bucket_name, cluster_name, profile):
    """
    This command adds a cloud storage bucket (S3 or GS) to SpellFS, which enables interaction with the bucket objects
    via ls, cp, and mounts. It will also updates the permissions of that bucket to allow Spell read access to it
    """
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    clusters = spell_client.list_clusters()
    if len(clusters) == 0:
        click.echo("No clusters defined, please run `spell cluster init`")
        return
    while len(clusters) != 1:
        if cluster_name is not None:
            clusters = [c for c in clusters if c['name'] == cluster_name]
        if len(clusters) == 0:
            click.echo("No clusters with the name {}, please try again.")
            return
        elif len(clusters) > 1:  # two or more clusters
            cluster_names = [c['name'] for c in clusters]
            cluster_name = click.prompt("You have multiple clusters defined. Please select one.",
                                        type=click.Choice(cluster_names)).strip()
    cluster = clusters[0]

    cluster_type = cluster['cloud_provider']
    if cluster_type == 'AWS':
        ctx.invoke(add_s3_bucket, spell_client=spell_client, bucket_name=bucket_name, cluster=cluster, profile=profile)
    elif cluster_type == 'GCP':
        if profile != 'default':
            click.echo("--profile is not a valid option for adding a gs bucket")
            return
        ctx.invoke(add_gs_bucket, spell_client=spell_client, bucket_name=bucket_name, cluster=cluster)
    else:
        raise Exception("Unknown cluster with provider {}, exiting.".format(cluster_type))


# register generic subcommands
cluster.add_command(add_bucket)

# register aws subcommands
cluster.add_command(create_aws)
cluster.add_command(eks_init)
cluster.add_command(update)

# register gcp subcommands
cluster.add_command(create_gcp)
cluster.add_command(gke_init)
