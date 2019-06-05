#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import click
from goss import Github
from goss import __version__
from goss.app import utils
#  from goss.app import run
from goss.app.logger import Logger
import configparser
import os
import pyperclip
import json
import base64
import requests


#  @run.run.command()
@click.option('--method', '-m', default = 'GET',
    help = 'GET/POST/PUT/DELETE for repository. Default is GET')
@click.option('--orga', '-o', help = 'If want create organization repository. Is required')
@click.option('--download', '-D', is_flag = True, help = 'Download file')
@click.option('--yes', '-y', is_flag = True, default = False, help = 'All questions answered yes')
@click.option('--output', '-O', help = 'Download name. Default is file name')
@click.option('--repo', '-r', required = True, help = 'Repository name')
@click.argument('path', default="/")
@click.pass_context
def release(ctx, repo, path, orga, method, download, output, yes):
    '''
    Get/Create/Delete/Download your Release/Asset

    More usage see : goss --help
    '''
    g = ctx.obj
    if not g:
        click.echo('You have not logged in yet, please run goss-cli to login')
        ctx.exit()
    print('ww')

    #  method = method.lower()

    #  method_function = {
        #  'get': 
            #  }

    #  owner = orga if orga else g.owner

    #  method_function[method](owner, repo)

    #  def _get():


