# -*- coding: utf-8 -*-
import os
import click
import subprocess

from ..main import bash

from .download_dump import _download_dump
from ..utils import manage_error
from ..parameters import DatabaseParameter


def echo_success():
    click.secho('Success!', fg='green', blink=True, bold=True)


@manage_error
def drop_db(database, display_mode):
    click.echo('--> Droping DB (if exists) ', nl=False)
    pd = subprocess.Popen(['dropdb', '--if-exists', database],
                          stdout=display_mode, stderr=display_mode)
    rcode = pd.wait()
    if rcode:
        raise Exception(pd.stderr.read().decode())
    echo_success()


@manage_error
def create_db(database, display_mode):
    click.echo('--> Creating DB ', nl=False)
    pc = subprocess.Popen(['createdb', database],
                          stdout=display_mode, stderr=display_mode)
    rcode = pc.wait()
    if rcode:
        raise Exception(pc.stderr.read().decode())
    echo_success()


@manage_error
def restore_db(database, dump, display_mode, verbose):
    click.echo('--> Restoring DB ', nl=False)
    pg = subprocess.Popen(['gunzip', '-c', dump], stdout=subprocess.PIPE,
                          stderr=display_mode)
    pp = subprocess.Popen(['psql', '-d', database],
                          stdin=pg.stdout, stdout=display_mode,
                          stderr=display_mode)
    pg.stdout.close()
    restore_logs = []
    for line in pp.stdout:
        restore_logs.append(line.decode().strip("\n"))
    if verbose:
        click.echo("\n")
        click.echo("\n".join(restore_logs))
        click.echo("\n")
    rcode = pp.wait()
    if rcode:
        raise Exception(pp.stderr.read().decode())
    echo_success()


@manage_error
def clean_data(database, display_mode):
    click.echo('--> Cleaning Data ', nl=False)
    auto_clean_path = os.path.join(
        os.path.dirname(__file__),
        '../templates/auto_clean.sql')
    pa = subprocess.Popen(['psql', '-d', database, '-f', auto_clean_path],
                          stdout=display_mode, stderr=display_mode)
    rcode = pa.wait()
    if rcode:
        raise Exception(pa.stderr.read().decode())
    echo_success()


@manage_error
def _remove_dump(dump, display_mode):
    rm = subprocess.Popen(['rm', dump],
                          stdout=display_mode, stderr=display_mode)
    rcode = rm.wait()
    if rcode:
        raise Exception(rm.stderr.read().decode())


@bash.command()
@click.argument('database', type=DatabaseParameter())
@click.argument('dump', default=False)
@click.option('-v', '--verbose',
              help="Show all information available.", is_flag=True)
@click.option('-r', '--remove_dump',
              help="Remove dump after restore.", is_flag=True)
@click.option('-b', '--bucket',
              help="Bucket for AWS.", default='e2-production')
def restoredb(database, dump, verbose, remove_dump, bucket):
    """
    Restore a DB, droping it if exists, and runs auto-clean.
    """
    display_mode = subprocess.PIPE
    if not dump:
        remove_dump = True
        dump = _download_dump(database, bucket)

    # Drop DB
    drop_db(database, display_mode)

    # Create DB
    create_db(database, display_mode)

    # Restore DB
    restore_db(database, dump, display_mode, verbose)

    # Clean Data
    clean_data(database, display_mode)

    if remove_dump:
        _remove_dump(dump, display_mode)

    click.echo('Goodbye!')
