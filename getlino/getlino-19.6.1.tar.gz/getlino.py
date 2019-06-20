#!python
# Copyright 2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
#
# Create a new Lino production site on this server
# This is meant as template for a script to be adapted to your system.
# This is not meant to be used as is.

from __future__ import print_function
from __future__ import absolute_import
import os
import subprocess

from argh import dispatch_command, arg, CommandError

def create_virtualenv(virtualenvs,envname):
    import virtualenv
    virtualenvs_folder = os.path.expanduser(virtualenvs)
    venv_dir = os.path.join(virtualenvs_folder, envname)
    virtualenv.create_environment(venv_dir)
    command = ". {}/{}/bin/activate".format(virtualenvs_folder, envname)
    os.system(command)

import sys

def install(package, sys_executable=None):
    if sys_executable:
        command = ". {}/bin/activate".format(sys_executable)
        os.system(command)
        subprocess.call(["{}/bin/python".format(sys_executable), "-m", "pip", "install", package])
    else:
        subprocess.call([sys.executable, "-m", "pip", "install", package])

@dispatch_command
@arg('-mode',help="Prod or Dev mode")
@arg('-projects_root',  default='/usr/local/lino',help="The path of the main project folder")
@arg('-prjname',help="The project name")
@arg('-appname',help="The application name")
@arg('-projects_prefix',help="The project prefix")
@arg('-arch_dir',help="The path of the backups folder")
@arg('-envdir',  help="The name of the python virtualenv")
@arg('-reposdir', help="The name of the repositories")
@arg('-usergroup', help="The name of the usergroup")

def main(mode='dev',
         projects_root='/usr/local/lino',
         projects_prefix='prod_sites',
         arch_dir='/var/backups/lino',
         envdir='env', reposdir='repositories',
         usergroup='www-data',
         prjname='prjname',
         appname='appname'):
    out = subprocess.Popen(['groups | grep ' + usergroup],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
    stdout,stderr = out.communicate()
    if str(stdout):
        print("OK you belong to the {0} user group.".format(usergroup))
    else:
        print("ERROR: you don't belong to the {0} user group.".format(usergroup))
        print("Maybe you want to run:")
        # echo sudo usermod -a -G $USERGROUP `whoami`
        print("echo sudo adduser `whoami` {0}".format(usergroup))
        return

    if not os.path.exists(projects_root):
        print("Oops, {0} does not exist.".format(projects_root))
        return ''

    prjdir=os.path.join(projects_root,prjname)
    if os.path.exists(prjdir):
        print("Oops, a directory {0} exists already. Delete it yourself if you dare!".format(prjdir))
        return
    print('Create a new production site into {0} using Lino {1} ...'.format(prjdir,appname))
    print('Are you sure? [y/N] ')
    answer = input()
    if answer not in  ['Yes','y','Y']:
        return

    os.system('mkdir {0}'.format(prjdir))
    os.system('cd {0}'.format(prjdir))
    install('virtualenv')
    create_virtualenv(prjdir,envdir)
    sys_executable= os.path.join(os.path.expanduser(prjdir), envdir)
    install('cookiecutter',sys_executable=sys_executable)
    print(sys_executable)
    command = ". {}/bin/activate".format(sys_executable)
    os.system(command)
    os.system('cd {0}'.format(prjdir))
    os.system("cookiecutter https://github.com/lino-framework/cookiecutter-startsite")
