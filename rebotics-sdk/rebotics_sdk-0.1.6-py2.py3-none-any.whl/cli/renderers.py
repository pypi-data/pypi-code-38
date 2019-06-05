import json
from datetime import datetime

import click
import pytz
from dateutil import parser as date_parser
from prettytable import PrettyTable


def format_full_table(results, max_column_length=30):
    if not isinstance(results, list):
        results = [results]
    table = PrettyTable()
    for i, item in enumerate(results):
        if i == 0:
            fields_to_render = []
            for field, value in item.items():
                if not (isinstance(value, dict) or isinstance(value, list)):
                    if isinstance(value, str):
                        if len(value) < max_column_length:
                            fields_to_render.append(field)
                    elif isinstance(value, int):
                        fields_to_render.append(field)

            table.field_names = fields_to_render

        table.add_row([
            item[field] for field in table.field_names
        ])
    click.echo(table)


def format_processing_action_output(processing_actions_list, format_):
    if format_ == 'json':
        click.echo(json.dumps(processing_actions_list, indent=2))
    elif format_ == 'id':
        click.echo(" ".join([str(item['id']) for item in processing_actions_list]))
    else:
        try:
            format_processing_action_table(processing_actions_list)
        except:
            format_full_table(processing_actions_list)


def format_processing_action_table(processing_actions_list):
    table = PrettyTable()
    table.field_names = ['#', 'id', 'store', 'user', 'status',
                         'created', 'last_requeue', 'last_requeue ago', 'time in queue']
    now = datetime.now(pytz.utc)
    for i, processing_action in enumerate(processing_actions_list):
        created_datetime = date_parser.parse(processing_action['created'])
        last_requeue_datetime = date_parser.parse(processing_action['last_requeue'])

        time_in_queue = now - last_requeue_datetime
        if processing_action['status'] in ['error', 'done', 'interrupted']:
            processing_start_time = processing_action.get('processing_start_time')
            processing_finish_time = processing_action.get('processing_finish_time')
            if processing_finish_time is None and processing_finish_time is None:
                time_in_queue = 'unknown'
            else:
                start_time = date_parser.parse(processing_start_time)
                finish_time = date_parser.parse(processing_finish_time)
                time_in_queue = finish_time - start_time
        table.add_row([
            i,
            processing_action['id'],
            '#{store_id}'.format(**processing_action),
            '{username}'.format(**processing_action['user']),
            processing_action['status'],
            created_datetime.strftime('%c'),
            last_requeue_datetime.strftime('%c'),
            str(now - last_requeue_datetime),
            str(time_in_queue),
        ])
    click.echo(table)
