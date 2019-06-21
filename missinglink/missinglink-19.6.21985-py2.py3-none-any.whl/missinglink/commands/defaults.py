# -*- coding: utf-8 -*-
import click
from missinglink.core import default_params

from .commons import output_result


def dict_to_table(d):
    keys = []
    values = []
    for k, v in d.items():
        keys.append(k)
        values.append(v)

    return [{'key': k, 'value': v} for k, v in d.items()]


@click.group('defaults', hidden=True)
def defaults_commands():
    pass


@defaults_commands.command('ls')
@click.pass_context
def defaults_commands_ls(ctx, **kwargs):
    output_result(ctx, dict_to_table(default_params.get_defaults()))


@defaults_commands.command('set')
@click.pass_context
@click.argument('key', type=str, required=True)
@click.argument('value', type=str, required=True)
def defaults_commands_set(ctx, **kwargs):
    default_params.set_default(kwargs['key'], kwargs['value'])
    output_result(ctx, dict_to_table(default_params.get_defaults()))


@defaults_commands.command('del')
@click.pass_context
@click.argument('key', type=str, required=True)
def defaults_commands_del(ctx, **kwargs):
    default_params.del_default(kwargs['key'])
    output_result(ctx, dict_to_table(default_params.get_defaults()))


@defaults_commands.command('get')
@click.pass_context
@click.argument('key', type=str, required=True)
def defaults_commands_del(ctx, **kwargs):
    val = default_params.get_default(kwargs['key'])
    output_result(ctx, {'key': kwargs['key'], 'value': val})
