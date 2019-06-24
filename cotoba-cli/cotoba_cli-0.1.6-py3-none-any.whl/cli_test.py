import os
import re
import json
import csv
import sys

import click

from cotoba_cli import platform
from cotoba_cli import config
from cotoba_cli.cognito import get_cognito_user

REGEX_TALK_HISTORY = '--history-?(?P<type>[^ ]*)'
REGEX_TALK_HISTORY_NUMBER = '--history-?(?P<type>[^ ]*) ' \
                            '(?P<history_size>[0-9]+)'


@click.group(help='Talk API Interface and test scenario.')
@click.option('--endpoint-url', type=str, help='Endpoint URL', default=None)
@click.pass_context
def cli_test(context, endpoint_url):
    if not context.obj:
        context.obj = {}
    if not endpoint_url:
        if os.environ.get('COTOBA_ENDPOINT_URL'):
            endpoint_url = os.environ.get('COTOBA_ENDPOINT_URL')
        elif config.load()['default'].get('endpoint-url'):
            endpoint_url = config.load()['default'].get('endpoint-url')
        else:
            click.echo('endpoint-url is not set.', err=True)
            sys.exit(1)

    context.obj['endpoint_url'] = endpoint_url


@cli_test.command(help='Repeat utterance and response.')
@click.option('--bot-id', 'bot_id', type=str, required=True, help='Bot ID.')
@click.option('--user-id', type=str, required=True, help='User ID.')
@click.option('--topic', type=str, help='Topic ID.')
# @click.option('--dev-key', type=str, help='Developer-Key.')
# @click.option('--api-key', type=str, help='Api-Key.')
@click.option('--log-level',
              type=click.Choice(['none', 'error', 'warning', 'info', 'debug']),
              default='none',
              help='Detail level of information to be added to the log.')
@click.option('--directory', type=str, help='Output file directory.')
@click.pass_context
def talk(
        context,
        bot_id,
        user_id,
        topic,
        # dev_key,
        # api_key,
        log_level,
        directory
):
    platform.show_talk_mode_description()
    config_dict = config.load()['default']
    endpoint_url = context.obj['endpoint_url']
    cognito_user = get_cognito_user()
    # 「exit」が入力されるまで発話 - 応答 を繰り返す
    while 1:
        input_utterance = input('> ')
        if input_utterance == '':
            continue

        if input_utterance == 'exit':
            click.echo('Exit talk mode.')
            break

        result = re.match(REGEX_TALK_HISTORY, input_utterance)
        if 'history' in input_utterance:
            history_type = None if result is None else result.group('type')
            result = re.match(REGEX_TALK_HISTORY_NUMBER, input_utterance)
            if result is not None and result.group('history_size').isnumeric():
                history_size = int(result.group('history_size'))
            else:
                history_size = None
            histories = platform.get_conversations_history(
                cognito_user,
                bot_id,
                user_id,
                history_size,
                endpoint_url)
            if len(histories) == 0:
                click.echo('No histories.')
                continue
            number_message = 'all' if history_size is None \
                else 'the last {}'.format(str(min(history_size,
                                                  len(histories)
                                                  )))
            if history_type == 'in':
                history_message_type = 'utterance'
            elif history_type == 'out':
                history_message_type = 'response'
            else:
                history_message_type = 'utterance and response'
            message = f'Show {number_message} {history_message_type} histories'
            click.echo(message)
            click.echo()
            for history in histories:
                if history_type != 'out':
                    click.secho(history[0], fg='bright_blue')
                if history_type != 'in':
                    click.secho(history[1], fg='bright_green')
                click.echo()
            continue
        is_show_topic = ' --show-topic' in input_utterance
        is_show_metadata = ' --show-meta' in input_utterance
        result = re.match(
            '(.*)( --show-topic| --show-metadata)(.*)',
            input_utterance)
        if result:
            # show-topic、show-meta両方指定を想定
            input_utterance = result.group(1) + result.group(3)
            result = re.match(
                '(.*)( --show-topic| --show-metadata)(.*)',
                input_utterance)
            if result:
                input_utterance = result.group(1) + result.group(3)

        if '--topic' in input_utterance:
            # オプションでトピック指定時はトピックを抽出
            result = re.match(
                '(.*)( --topic | --topic=)(.*)',
                input_utterance)
            input_utterance = result.group(1)
            topic = result.group(3)

        try:
            response_obj = platform.ask_bot(
                bot_id=bot_id,
                user_id=user_id,
                utterance=input_utterance,
                topic=topic,
                metadata=None,
                log_level=log_level,
                locale=config_dict.get('locale'),
                endpoint_url=endpoint_url
            )
        except Exception as e:
            click.secho(str(e.args), fg='red')
            return

        res = response_obj.get_response_body()
        if res == 'Internal Server Error':
            click.secho(res, fg='red')
            return

        if res.get('response'):
            click.secho(res.get('response'), fg='bright_magenta')

        if is_show_topic:
            response_topic = res.get('topic')
            response_topic = response_topic or ''
            click.echo('topic:' + click.style(
                response_topic, fg='bright_magenta'))
        if is_show_metadata:
            response_meta = res.get('metadata')
            text = response_meta or ''
            if isinstance(response_meta, dict):
                text = json.dumps(response_meta,
                                  ensure_ascii=False)
            click.echo('metadata:' + click.style(
                text, fg='bright_magenta'))
        if directory:
            csv_file_path = os.path.join(directory, bot_id + '_talk.csv')
            is_exists = os.path.exists(csv_file_path)
            with open(csv_file_path, 'a', newline='',
                      encoding='utf-8') as f:
                # ヘッダ部を設定
                fieldnames = [
                    'timestamp',
                    'topic(response)',
                    'utterance',
                    'response text',
                    'metadata'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not is_exists:
                    # ファイル非存在のみヘッダ部書き込み
                    writer.writeheader()
                row = {
                    "timestamp": response_obj.get_request_time(),
                    "topic(response)": res.get('topic'),
                    "utterance": input_utterance,
                    "response text": res.get('response'),
                    "metadata": res.get('metadata')
                }
                writer.writerow(row)


@cli_test.command(help='Compare expected with response.')
@click.option('--bot-id', 'bot_id', type=str, required=True, help='Bot ID.')
@click.option('--file', 'test_file',
              type=str, required=True, help='Test JSON file.')
@click.option('--directory', type=str, help='Output file directory.')
@click.pass_context
def compare(
        context,
        bot_id,
        test_file,
        directory
):
    endpoint_url = context.obj['endpoint_url']
    config_dict = config.load()['default']
    if not os.path.isfile(test_file):
        click.echo(test_file + ' is not found.', err=True)
        sys.exit(1)
    with open(test_file, encoding='utf-8') as f:
        try:
            df = json.load(f)
        except json.JSONDecodeError as e:
            click.echo(str(e), err=True)
            sys.exit(1)
        test_list = df.get('test')
    if test_list is None:
        click.echo('Test data is empty.', err=True)
        sys.exit(1)
    for test_elm in test_list:
        utterance = test_elm.get('request').get('utterance')
        topic = test_elm.get('request').get('topic')
        metadata = test_elm.get('request').get('metadata')
        user_id = test_elm.get('request').get('userId')
        locale = test_elm.get('request').get('locale') or config_dict['locale']
        request_config = test_elm.get('request').get('config')
        if request_config is not None:
            log_level = request_config.get('logLevel')
        else:
            log_level = None
        if utterance is None:
            click.secho('utterance is required.', fg='red', err=True)
            click.echo('---------------')
            continue
        if user_id is None:
            click.secho('userId is required.', fg='red', err=True)
            click.echo('---------------')
            continue
        try:
            response_obj = platform.ask_bot(
                bot_id=bot_id,
                user_id=user_id,
                utterance=utterance,
                topic=topic,
                metadata=metadata,
                log_level=log_level,
                locale=locale,
                endpoint_url=endpoint_url
            )
            res = response_obj.get_response_body()
        except Exception as e:
            click.echo(str(e.args), err=True)
            sys.exit(1)
        click.echo('utterance:' + utterance)
        click.secho('response:' +
                    res.get('response'),
                    fg='bright_magenta')
        expected = test_elm.get('expected')

        # 期待値の配列から完全一致のものがあるか判定していく
        target_compare_list = [
            "response",
            "topic",
            "metadata"
        ]
        result_map = {}
        for target in target_compare_list:
            expected_list = expected.get(target)
            result = 'NG'
            for expected_elm in expected_list:
                if res.get(target) == expected_elm:
                    result = 'OK'
                    break
            click.echo('compare_result[{0}]:{1}'.format(target, result))
            result_map[target] = result
        click.echo('---------------')

        # ディレクトリ未指定時はCLI実行ディレクトリに格納
        directory = directory or './'
        if not os.path.exists(directory):
            os.mkdir(directory)
        csv_file_path = os.path.join(directory, bot_id + '_compare.csv')
        is_exists = os.path.exists(csv_file_path)
        with open(csv_file_path, 'a', newline='', encoding='utf-8') as f:
            # ヘッダ部を設定
            fieldnames = [
                'timestamp',
                'utterance',
                'response text',
                'expected response text',
                'response text result',
                'topic',
                'expected topic',
                'topic result',
                'metadata',
                'expected metadata',
                'metadata result'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not is_exists:
                # ファイル非存在のみヘッダ部書き込み
                writer.writeheader()
            row = {
                'timestamp': response_obj.get_request_time(),
                'utterance': utterance,
                'response text': res.get('response'),
                'expected response text': expected.get('response'),
                'response text result': result_map.get('response'),
                'topic': res.get('topic'),
                'expected topic': expected.get('topic'),
                'topic result': result_map.get('topic'),
                'metadata': res.get('metadata'),
                'expected metadata': expected.get('metadata'),
                'metadata result': result_map.get('metadata')
            }
            writer.writerow(row)
