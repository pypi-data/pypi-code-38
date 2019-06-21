# -*- coding: utf-8 -*-
import os
import click
import subprocess

from ..main import bash

def _download_dump(folder, bucket):
    print('--> Getting dump name ', end = '', flush=True)
    link = "s3://" + bucket + "/" + folder + "/"
    gnl = subprocess.Popen(['aws', 's3', 'ls', link], stdout=subprocess.PIPE)
    gnr = subprocess.Popen(['tail', '-n', '1'], stdin=gnl.stdout, stdout=subprocess.PIPE)
    gnl.stdout.close()
    gnr.wait()
    gn = subprocess.Popen(['awk', '{ print $4 }',], stdin=gnr.stdout, stdout=subprocess.PIPE)
    gnr.stdout.close()
    output = gn.communicate()[0]
    gn.wait()
    if output:
        link += output.decode('UTF-8')[:-1]
        print ('\33[92m' + 'Success!' + '\x1b[0m')
    else:
        print ('\33[91m' + 'Error!' + '\x1b[0m')
        print('Goodbye!')
        return False
    print('--> Downloading dump ', end = '', flush=True)
    gd = subprocess.Popen(['aws', 's3', 'cp', link, '.'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    gd.wait()
    if gd.communicate()[1]:
        print ('\33[91m' + 'Error!' + '\x1b[0m')
    else:
        print ('\33[92m' + 'Success!' + '\x1b[0m')
    return output.decode('UTF-8')[:-1]

@bash.command()
@click.argument('folder')
@click.argument('bucket', default='e2-production')
def download_dump(folder, bucket):
    """
    Download DB dump from aws.
    """
    _download_dump(folder, bucket)
    print('Goodbye!')
