#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import pandas as pd
from redash_dynamic_query import RedashDynamicQuery
from datetime import datetime
import configparser
import os

def get_config(config_path):
    parser = configparser.RawConfigParser()
    config = os.path.expanduser(config_path)

    parser.read([config])

    rv = {}
    for section in parser.sections():
        for key, value in parser.items(section):
            rv['%s.%s' % (section, key)] = value
    return rv

@click.command()
@click.option('-q', '--query_id', nargs=1, required=True, type=int)
@click.option('-p', '--parameters', nargs=2, type=(str, str), multiple=True)
@click.option('-o', '--output', required=True, nargs=1, type=str)
@click.option('-c', '--config', default='~/.rqdrc', nargs=1, type=str)
@click.option('-d', '--download_only', is_flag=True)
def cmd(query_id, parameters, output, config, download_only):
    if download_only == True:
        download_query(query_id, output, config)
    else:
        execute_query(query_id, parameters, output, config)

def execute_query(query_id, parameters, output, config):
    query_paremters = {}
    for key, value in parameters:
        query_paremters[key] = value

    bind = {}
    if(parameters != ()):
        for key, value in parameters:
            bind.update([(key, value)])

    cfg = get_config(config)
    encoding = 'utf-8'
    if('redash.encoding' in cfg):
        encoding = cfg['redash.encoding']

    redash = RedashDynamicQuery(
        endpoint=cfg['redash.endpoint'],
        apikey=cfg['redash.apikey'],
        data_source_id=cfg['redash.data_source_id'],
        max_age=0,
        max_wait=1200,
    )

    result = redash.query(query_id=query_id, bind=bind)
    data = result['query_result']['data']
    columns = [column['name'] for column in data['columns']]
    query_df = pd.DataFrame(data['rows'], columns=columns)
    query_df.to_csv(output, mode='w', index=False, header=True, encoding=encoding)

def download_query(query_id, output, config):
    cfg = get_config(config)
    encoding = 'utf-8'
    if('redash.encoding' in cfg):
        encoding = cfg['redash.encoding']

    redash = RedashDynamicQuery(
        endpoint=cfg['redash.endpoint'],
        apikey=cfg['redash.apikey'],
        data_source_id=cfg['redash.data_source_id'],
        max_age=0,
        max_wait=1200,
    )

    result = redash._api_queries(query_id=query_id)
    latest_query_data_id = result['latest_query_data_id']

    result = redash._api_query_results_json(query_id, latest_query_data_id)
    data = result['query_result']['data']
    columns = [column['name'] for column in data['columns']]
    query_df = pd.DataFrame(data['rows'], columns=columns)
    query_df.to_csv(output, mode='w', index=False, header=True, encoding=encoding)

def main():
    cmd()
