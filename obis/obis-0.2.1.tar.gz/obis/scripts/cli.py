#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cli.py

The module that implements the CLI for obis.


Created by Chandrasekhar Ramakrishnan on 2017-01-27.
Copyright (c) 2017 Chandrasekhar Ramakrishnan. All rights reserved.
"""
import json
import os
import sys
from datetime import datetime

import click

from ..dm.command_result import CommandResult
from ..dm.utils import cd
from .data_mgmt_runner import DataMgmtRunner
from .click_util import click_echo


def click_progress(progress_data):
    if progress_data['type'] == 'progress':
        click_echo(progress_data['message'])


def click_progress_no_ts(progress_data):
    if progress_data['type'] == 'progress':
        click.echo("{}".format(progress_data['message']))


def add_params(params):
    def _add_params(func):
        for param in reversed(params):
            func = param(func)
        return func
    return _add_params


@click.group()
@click.version_option(version=None)
@click.option('-q', '--quiet', default=False, is_flag=True, help='Suppress status reporting.')
@click.option('-s', '--skip_verification', default=False, is_flag=True, help='Do not verify cerficiates')
@click.option('-d', '--debug', default=False, is_flag=True, help="Show stack trace on error.")
@click.pass_context
def cli(ctx, quiet, skip_verification, debug):
    ctx.obj['quiet'] = quiet
    if skip_verification:
        ctx.obj['verify_certificates'] = False
    ctx.obj['debug'] = debug


def init_data_impl(ctx, repository, desc):
    """Shared implementation for the init_data command."""
    if repository is None:
        repository = "."
    click_echo("init_data {}".format(repository))
    desc = desc if desc != "" else None
    return ctx.obj['runner'].run("init_data", lambda dm: dm.init_data(desc), repository)


def init_analysis_impl(ctx, parent, repository, description):
    click_echo("init_analysis {}".format(repository))
    if parent is not None and os.path.isabs(parent):
        click_echo('Error: The parent must be given as a relative path.')
        return -1
    if repository is not None and os.path.isabs(repository):
        click_echo('Error: The repository must be given as a relative path.')
        return -1
    description = description if description != "" else None
    parent_dir = os.getcwd() if parent is None else os.path.join(os.getcwd(), parent)
    analysis_dir = os.path.join(os.getcwd(), repository)
    parent = os.path.relpath(parent_dir, analysis_dir)
    parent = '..' if parent is None else parent
    return ctx.obj['runner'].run("init_analysis", lambda dm: dm.init_analysis(parent, description), repository)


# settings commands


class SettingsGet(click.ParamType):
    name = 'settings_get'

    def convert(self, value, param, ctx):
        try:
            split = list(filter(lambda term: len(term) > 0, value.split(',')))
            return split
        except:
            self._fail(param)

    def _fail(self, param):
            self.fail(param=param, message='Settings must be in the format: key1, key2, ...')


class SettingsClear(SettingsGet):
    pass


class SettingsSet(click.ParamType):
    name = 'settings_set'

    def convert(self, value, param, ctx):
        try:
            value = self._encode_json(value)
            settings = {}
            split = list(filter(lambda term: len(term) > 0, value.split(',')))
            for setting in split:
                setting_split = setting.split('=')
                if len(setting_split) != 2:
                    self._fail(param)
                key = setting_split[0]
                value = setting_split[1]
                settings[key] = self._decode_json(value)
            return settings
        except:
            self._fail(param)

    def _encode_json(self, value):
        encoded = ''
        SEEK = 0
        ENCODE = 1
        mode = SEEK
        for char in value:
            if char == '{':
                mode = ENCODE
            elif char == '}':
                mode = SEEK
            if mode == SEEK:
                encoded += char
            elif mode == ENCODE:
                encoded += char.replace(',', '|')
        return encoded

    def _decode_json(self, value):
        return value.replace('|', ',')

    def _fail(self, param):
            self.fail(param=param, message='Settings must be in the format: key1=value1, key2=value2, ...')


def _join_settings_set(setting_dicts):
    joined = {}
    for setting_dict in setting_dicts:
        for key, value in setting_dict.items():
            joined[key] = value
    return joined


def _join_settings_get(setting_lists):
    joined = []
    for setting_list in setting_lists:
        joined += setting_list
    return joined


def _access_settings(ctx, prop=None, value=None, set=False, get=False, clear=False):
    is_global = ctx.obj['is_global']
    runner = ctx.obj['runner']
    resolver = ctx.obj['resolver']
    is_data_set_property = False
    if 'is_data_set_property' in ctx.obj:
        is_data_set_property = ctx.obj['is_data_set_property']
    runner.config(resolver, is_global, is_data_set_property, prop=prop, value=value, set=set, get=get, clear=clear)


def _set(ctx, settings):
    settings_dict = _join_settings_set(settings)
    for prop, value in settings_dict.items():
        _access_settings(ctx, prop=prop, value=value, set=True)
    return CommandResult(returncode=0, output='')


def _get(ctx, settings):
    settings_list = _join_settings_get(settings)
    if len(settings_list) == 0:
        settings_list = [None]
    for prop in settings_list:
        _access_settings(ctx, prop=prop, get=True)
    return CommandResult(returncode=0, output='')


def _clear(ctx, settings):
    settings_list = _join_settings_get(settings)
    if len(settings_list) == 0:
        settings_list = [None]
    for prop in settings_list:
        _access_settings(ctx, prop=prop, clear=True)
    return CommandResult(returncode=0, output='')


## get all settings

@cli.group()
@click.option('-g', '--is_global', default=False, is_flag=True, help='Get global or local.')
@click.pass_context
def settings(ctx, is_global):
    """ Get all settings.
    """
    ctx.obj['is_global'] = is_global


@settings.command('get')
@click.pass_context
def settings_get(ctx):
    runner = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    settings = runner.get_settings()
    settings_str = json.dumps(settings, indent=4, sort_keys=True)
    click.echo("{}".format(settings_str))


## repository: repository_id, external_dms_id, data_set_id

@cli.group()
@click.option('-g', '--is_global', default=False, is_flag=True, help='Set/get global or local.')
@click.pass_context
def repository(ctx, is_global):
    """ Get/set settings related to the repository.
    """
    runner = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.obj['is_global'] = is_global
    ctx.obj['runner'] = runner
    ctx.obj['resolver'] = 'repository'


@repository.command('set')
@click.argument('settings', type=SettingsSet(), nargs=-1)
@click.pass_context
def repository_set(ctx, settings):
    return ctx.obj['runner'].run("repository_set", lambda dm: _set(ctx, settings))


@repository.command('get')
@click.argument('settings', type=SettingsGet(), nargs=-1)
@click.pass_context
def repository_get(ctx, settings):
    return ctx.obj['runner'].run("repository_get", lambda dm: _get(ctx, settings))


@repository.command('clear')
@click.argument('settings', type=SettingsClear(), nargs=-1)
@click.pass_context
def repository_clear(ctx, settings):
    return ctx.obj['runner'].run("repository_clear", lambda dm: _clear(ctx, settings))


## data_set: type, properties


@cli.group('data_set')
@click.option('-g', '--is_global', default=False, is_flag=True, help='Set/get global or local.')
@click.option('-p', '--is_data_set_property', default=False, is_flag=True, help='Configure data set property.')
@click.pass_context
def data_set(ctx, is_global, is_data_set_property):
    """ Get/set settings related to the data set.
    """
    runner = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.obj['is_global'] = is_global
    ctx.obj['is_data_set_property'] = is_data_set_property
    ctx.obj['runner'] = runner
    ctx.obj['resolver'] = 'data_set'


@data_set.command('set')
@click.argument('settings', type=SettingsSet(), nargs=-1)
@click.pass_context
def data_set_set(ctx, settings):
    return ctx.obj['runner'].run("data_set_set", lambda dm: _set(ctx, settings))


@data_set.command('get')
@click.argument('settings', type=SettingsGet(), nargs=-1)
@click.pass_context
def data_set_get(ctx, settings):
    return ctx.obj['runner'].run("data_set_get", lambda dm: _get(ctx, settings))


@data_set.command('clear')
@click.argument('settings', type=SettingsClear(), nargs=-1)
@click.pass_context
def data_set_clear(ctx, settings):
    return ctx.obj['runner'].run("data_set_clear", lambda dm: _clear(ctx, settings))


## object: object_id


@cli.group()
@click.option('-g', '--is_global', default=False, is_flag=True, help='Set/get global or local.')
@click.pass_context
def object(ctx, is_global):
    """ Get/set settings related to the object.
    """
    runner = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.obj['is_global'] = is_global
    ctx.obj['runner'] = runner
    ctx.obj['resolver'] = 'object'


@object.command('set')
@click.argument('settings', type=SettingsSet(), nargs=-1)
@click.pass_context
def object_set(ctx, settings):
    return ctx.obj['runner'].run("object_set", lambda dm: _set(ctx, settings))


@object.command('get')
@click.argument('settings', type=SettingsGet(), nargs=-1)
@click.pass_context
def object_get(ctx, settings):
    return ctx.obj['runner'].run("object_get", lambda dm: _get(ctx, settings))


@object.command('clear')
@click.argument('settings', type=SettingsClear(), nargs=-1)
@click.pass_context
def object_clear(ctx, settings):
    return ctx.obj['runner'].run("object_clear", lambda dm: _clear(ctx, settings))


## collection: collection_id


@cli.group()
@click.option('-g', '--is_global', default=False, is_flag=True, help='Set/get global or local.')
@click.pass_context
def collection(ctx, is_global):
    """ Get/set settings related to the collection.
    """
    runner = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.obj['is_global'] = is_global
    ctx.obj['runner'] = runner
    ctx.obj['resolver'] = 'collection'


@collection.command('set')
@click.argument('settings', type=SettingsSet(), nargs=-1)
@click.pass_context
def collection_set(ctx, settings):
    return ctx.obj['runner'].run("collection_set", lambda dm: _set(ctx, settings))


@collection.command('get')
@click.argument('settings', type=SettingsGet(), nargs=-1)
@click.pass_context
def collection_get(ctx, settings):
    return ctx.obj['runner'].run("collection_get", lambda dm: _get(ctx, settings))


@collection.command('clear')
@click.argument('settings', type=SettingsClear(), nargs=-1)
@click.pass_context
def collection_clear(ctx, settings):
    return ctx.obj['runner'].run("collection_clear", lambda dm: _clear(ctx, settings))


## config: fileservice_url, git_annex_hash_as_checksum, hostname, openbis_url, user, verify_certificates


@cli.group()
@click.option('-g', '--is_global', default=False, is_flag=True, help='Set/get global or local.')
@click.pass_context
def config(ctx, is_global):
    """ Get/set configurations.
    """
    runner = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.obj['is_global'] = is_global
    ctx.obj['runner'] = runner
    ctx.obj['resolver'] = 'config'


@config.command('set')
@click.argument('settings', type=SettingsSet(), nargs=-1)
@click.pass_context
def config_set(ctx, settings):
    return ctx.obj['runner'].run("config_set", lambda dm: _set(ctx, settings))


@config.command('get')
@click.argument('settings', type=SettingsGet(), nargs=-1)
@click.pass_context
def config_get(ctx, settings):
    return ctx.obj['runner'].run("config_get", lambda dm: _get(ctx, settings))


@config.command('clear')
@click.argument('settings', type=SettingsClear(), nargs=-1)
@click.pass_context
def config_clear(ctx, settings):
    return ctx.obj['runner'].run("config_clear", lambda dm: _clear(ctx, settings))


# repository commands: status, sync, commit, init, addref, removeref, init_analysis

## commit

_commit_params = [
    click.option('-m', '--msg', default="obis commit", help='A message explaining what was done.'),
    click.option('-a', '--auto_add', default=True, is_flag=True, help='Automatically add all untracked files.'),
    click.option('-i', '--ignore_missing_parent', default=True, is_flag=True, help='If parent data set is missing, ignore it.'),
    click.argument('repository', type=click.Path(exists=True, file_okay=False), required=False),
]


@repository.command("commit", short_help="Commit the repository to git and inform openBIS.")
@click.pass_context
@add_params(_commit_params)
def repository_commit(ctx, msg, auto_add, ignore_missing_parent, repository):
    return ctx.obj['runner'].run("commit", lambda dm: dm.commit(msg, auto_add, ignore_missing_parent), repository)

@cli.command(short_help="Commit the repository to git and inform openBIS.")
@click.pass_context
@add_params(_commit_params)
def commit(ctx, msg, auto_add, ignore_missing_parent, repository):
    ctx.obj['runner'] = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.invoke(repository_commit, msg=msg, auto_add=auto_add, ignore_missing_parent=ignore_missing_parent, repository=repository)

## init

_init_params = [
    click.argument('repository', type=click.Path(exists=False, file_okay=False), required=False),
    click.argument('description', default=""),
]

@repository.command("init", short_help="Initialize the folder as a data repository.")
@click.pass_context
@add_params(_init_params)
def repository_init(ctx, repository, description):
    return init_data_impl(ctx, repository, description)

@cli.command(short_help="Initialize the folder as a data repository.")
@click.pass_context
@add_params(_init_params)
def init(ctx, repository, description):
    ctx.obj['runner'] = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.invoke(repository_init, repository=repository, description=description)

## init analysis

_init_analysis_params = [
    click.option('-p', '--parent', type=click.Path(exists=False, file_okay=False)),
]
_init_analysis_params += _init_params

@repository.command("init_analysis", short_help="Initialize the folder as an analysis folder.")
@click.pass_context
@add_params(_init_analysis_params)
def repository_init_analysis(ctx, parent, repository, description):
    return init_analysis_impl(ctx, parent, repository, description)

@cli.command(name='init_analysis', short_help="Initialize the folder as an analysis folder.")
@click.pass_context
@add_params(_init_analysis_params)
def init_analysis(ctx, parent, repository, description):
    ctx.obj['runner'] = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.invoke(repository_init_analysis, parent=parent, repository=repository, description=description)

## status

_status_params = [
    click.argument('repository', type=click.Path(exists=True, file_okay=False), required=False),
]

@repository.command("status", short_help="Show the state of the obis repository.")
@click.pass_context
@add_params(_status_params)
def repository_status(ctx, repository):
    return ctx.obj['runner'].run("repository_status", lambda dm: dm.status(), repository)

@cli.command(short_help="Show the state of the obis repository.")
@click.pass_context
@add_params(_status_params)
def status(ctx, repository):
    ctx.obj['runner'] = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.invoke(repository_status, repository=repository)

## sync

_sync_params = [
    click.option('-i', '--ignore_missing_parent', default=True, is_flag=True, help='If parent data set is missing, ignore it.'),
    click.argument('repository', type=click.Path(exists=True, file_okay=False), required=False),
]

def _repository_sync(dm, ignore_missing_parent):
    dm.ignore_missing_parent = ignore_missing_parent
    return dm.sync()

@repository.command("sync", short_help="Sync the repository with openBIS.")
@click.pass_context
@add_params(_sync_params)
def repository_sync(ctx, ignore_missing_parent, repository):
    return ctx.obj['runner'].run("sync", lambda dm: _repository_sync(dm, ignore_missing_parent), repository)

@cli.command(short_help="Sync the repository with openBIS.")
@click.pass_context
@add_params(_sync_params)
def sync(ctx, ignore_missing_parent, repository):
    ctx.obj['runner'] = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.invoke(repository_sync, ignore_missing_parent=ignore_missing_parent, repository=repository)

## addref

_addref_params = [
    click.argument('repository', type=click.Path(exists=True, file_okay=False), required=False),
]

@repository.command("addref", short_help="Add the given repository as a reference to openBIS.")
@click.pass_context
@add_params(_addref_params)
def repository_addref(ctx, repository):
    return ctx.obj['runner'].run("addref", lambda dm: dm.addref(), repository)

@cli.command(short_help="Add the given repository as a reference to openBIS.")
@click.pass_context
@add_params(_addref_params)
def addref(ctx, repository):
    ctx.obj['runner'] = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.invoke(repository_addref, repository=repository)

# removeref

_removeref_params = [
    click.option('-d', '--data_set_id', help='Remove ref by data set id, in case the repository is not available anymore.'),
    click.argument('repository', type=click.Path(exists=True, file_okay=False), required=False),
]

@repository.command("removeref", short_help="Remove the reference to the given repository from openBIS.")
@click.pass_context
@add_params(_removeref_params)
def repository_removeref(ctx, data_set_id, repository):
    if data_set_id is not None and repository is not None:
        click_echo("Only provide the data_set id OR the repository.")
        return -1
    return ctx.obj['runner'].run("removeref", lambda dm: dm.removeref(data_set_id=data_set_id), repository)


@cli.command(short_help="Remove the reference to the given repository from openBIS.")
@click.pass_context
@add_params(_removeref_params)
def removeref(ctx, data_set_id, repository):
    ctx.obj['runner'] = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.invoke(repository_removeref, data_set_id=data_set_id, repository=repository)


# data set commands: download / clone

## download

_download_params = [
    click.option('-c', '--content_copy_index', type=int, default=None, help='Index of the content copy to download from.'),
    click.option('-f', '--file', help='File in the data set to download - downloading all if not given.'),
    click.option('-s', '--skip_integrity_check', default=False, is_flag=True, help='Skip file integrity check with checksums.'),
    click.argument('data_set_id'),
]

@data_set.command("download", short_help="Download files of a linked data set.")
@add_params(_download_params)
@click.pass_context 
def data_set_download(ctx, content_copy_index, file, data_set_id, skip_integrity_check):
    return ctx.obj['runner'].run("download", lambda dm: dm.download(data_set_id, content_copy_index, file, skip_integrity_check))

@cli.command(short_help="Download files of a linked data set.")
@add_params(_download_params)
@click.pass_context
def download(ctx, content_copy_index, file, data_set_id, skip_integrity_check):
    ctx.obj['runner'] = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.invoke(data_set_download, content_copy_index=content_copy_index, file=file, data_set_id=data_set_id, skip_integrity_check=skip_integrity_check)

## clone

_clone_move_params = [
    click.option('-u', '--ssh_user', default=None, help='User to connect to remote systems via ssh'),
    click.option('-c', '--content_copy_index', type=int, default=None, help='Index of the content copy to clone from in case there are multiple copies'),
    click.option('-s', '--skip_integrity_check', default=False, is_flag=True, help='Skip file integrity check with checksums.'),
    click.argument('data_set_id'),
]

@data_set.command("clone", short_help="Clone the repository found in the given data set id.")
@click.pass_context
@add_params(_clone_move_params)
def data_set_clone(ctx, ssh_user, content_copy_index, data_set_id, skip_integrity_check):
    return ctx.obj['runner'].run("clone", lambda dm: dm.clone(data_set_id, ssh_user, content_copy_index, skip_integrity_check))

@cli.command(short_help="Clone the repository found in the given data set id.")
@click.pass_context
@add_params(_clone_move_params)
def clone(ctx, ssh_user, content_copy_index, data_set_id, skip_integrity_check):
    ctx.obj['runner'] = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.invoke(data_set_clone, ssh_user=ssh_user, content_copy_index=content_copy_index, data_set_id=data_set_id, skip_integrity_check=skip_integrity_check)


## move

@data_set.command("move", short_help="Move the repository found in the given data set id.")
@click.pass_context
@add_params(_clone_move_params)
def data_set_move(ctx, ssh_user, content_copy_index, data_set_id, skip_integrity_check):
    return ctx.obj['runner'].run("move", lambda dm: dm.move(data_set_id, ssh_user, content_copy_index, skip_integrity_check))

@cli.command(short_help="Move the repository found in the given data set id.")
@click.pass_context
@add_params(_clone_move_params)
def move(ctx, ssh_user, content_copy_index, data_set_id, skip_integrity_check):
    ctx.obj['runner'] = DataMgmtRunner(ctx.obj, halt_on_error_log=False)
    ctx.invoke(data_set_move, ssh_user=ssh_user, content_copy_index=content_copy_index, data_set_id=data_set_id, skip_integrity_check=skip_integrity_check)


def main():
    cli(obj={})


if __name__ == '__main__':
    main()
