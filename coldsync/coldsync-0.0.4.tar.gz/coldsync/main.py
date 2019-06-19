import os

import click

from coldsync.storage.google_storage_coldline import GoogleColdlineStorage
from coldsync.utils import make_bucket_name, get_from_environment

# The following environment variables are required for each setup

CS_DATA_CENTER = "CS_DATA_CENTER"
CS_PROJECT_NAME = "CS_PROJECT_NAME"
CS_ENV_NAME = "CS_ENV_NAME"
CS_GOOGLE_SERVICE_ACCOUNT_PATH = "CS_GOOGLE_SERVICE_ACCOUNT_PATH"

gcs = None

HERE = os.path.dirname(os.path.realpath(__file__))


@click.group()  # pragma: no cover
def cli():
    pass


@click.command(help="List all files backed up for this bucket")
def list_files():
    global gcs
    print(gcs.get_files())


@click.command(help="Download an existing file from the bucket")
@click.argument('local_path', type=click.Path(exists=True))
@click.option('--remote_path', default=None, help="name of the file in the bucket")
def upload_file(local_path, remote_path):
    print(local_path, remote_path)
    gcs.upload_file(local_path, remote_path)


@click.command(help="Uploads a new file in the backup bucket")
@click.argument('remote_path')
@click.argument('local_path', type=click.Path(exists=False))
def download_file(local_path, remote_path):
    gcs.download_file(remote_path, local_path)


@click.command(help="Deletes a file in the backup bucket")
@click.argument('remote_path')
def delete_file(remote_path):
    deleted = gcs.delete_file(remote_path)
    if deleted:
        print("File '%s' removed" % remote_path)
    else:
        print("Could not find file '%s' to remove" % remote_path)


cli.add_command(list_files)  # pragma: no cover
cli.add_command(upload_file)  # pragma: no cover
cli.add_command(download_file)  # pragma: no cover
cli.add_command(delete_file)  # pragma: no cover


def main():  # pragma: no cover
    data_center = get_from_environment(CS_DATA_CENTER)
    project_name = get_from_environment(CS_PROJECT_NAME)
    env_name = get_from_environment(CS_ENV_NAME)
    credentials = get_from_environment(CS_GOOGLE_SERVICE_ACCOUNT_PATH)
    credentials = os.path.abspath(os.path.join(HERE, '..', credentials))

    # Needed to login for google-cloud-storage
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

    bucket_name = make_bucket_name(data_center=data_center, project_name=project_name, env_name=env_name)

    global gcs
    gcs = GoogleColdlineStorage(bucket_name=bucket_name)

    cli()


if __name__ == '__main__':  # pragma: no cover
    main()
