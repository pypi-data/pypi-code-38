import logging
import os
import ssl
import time

import requests
import urllib3
from pyfiglet import Figlet
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3 import Retry
from pathlib import Path

from onedesk.auth.auth import get_token
from onedesk.automaton.automaton import export_automata, import_automaton, get_automaton_list_for_client, \
    delete_automata, automaton_exists, submit_automaton_for_approval, approve_automaton, get_automaton_version_latest, \
    get_automaton_list_for_category
from onedesk.category.category import get_category_list_for_client, \
    get_category_tree, delete_category, create_parent
from onedesk.client.client import get_client
from util.arguments import parser
from util.arguments import version
from util.models import Category, Automaton, ExportedAutomaton
from util.util import get_directory_tree, write_json_file, clean_file_name

f = Figlet(font='slant')
ch = logging.StreamHandler()
formatter = logging.Formatter('{asctime} {levelname} {name} {filename} {lineno} | {message}', style='{')
ch.setFormatter(formatter)
logger = logging.getLogger('main')
logger.addHandler(ch)


def do_export(args):
    print(f.renderText('Export Start !!'))
    start_time = time.time()

    # create export path on local file system
    try:
        directory = Path(args.directory)
        directory.mkdir(parents=True, exist_ok=True)
        logger.info('Exporting to local directory: %s', directory.absolute())
    except Exception:
        logger.error('Failed to create export directory: %s', args.directory)
        raise SystemExit

    # create session object
    s = requests.Session()
    # this argument defaults to false, if provided it will be true
    # a user who specifies this argument wants to NOT verify certificates so we negate the value
    s.verify = not args.ignorecert

    if int(args.retry) > 0:
        # session retry config
        retries = Retry(total=int(args.retry),
                        backoff_factor=0.2,
                        status_forcelist=[500, 502, 503, 504],
                        method_whitelist=False)
        s.mount('https://', HTTPAdapter(max_retries=retries))
        s.mount('http://', HTTPAdapter(max_retries=retries))

    # get token for session and add to headers
    token = get_token(s, args.instance, args.username, args.password)
    s.headers = {'authorization': 'bearer ' + token}

    # get the given client, otherwise defaults to IPsoft
    client = get_client(s, args.instance, args.client)

    category_tree = get_category_tree(s, args.instance, client, args.category)

    for node in tqdm(category_tree, desc='Exporting automata to {}'.format(directory)):
        if type(node.val) is Automaton:
            node_path = Path(directory, node.path)

            try:
                logger.debug('Creating directory %s', node_path.parent.absolute())
                node_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                logger.error('Failed to create export directory: %s', node_path)
                raise SystemExit

            data = export_automata(s, args.instance, node.val.json())

            if data is None:
                continue

            write_json_file(node_path.with_suffix('.json'), data)

    print(f.renderText('FINISH !! --- {0:.3g} seconds'.format((time.time() - start_time))))


def do_import(args):
    print(f.renderText('Import Start !!'))
    start_time = time.time()

    # given directory to use as root
    directory = Path(args.directory)

    if not directory.exists():
        logger.error('Given directory does not exist! {}'.format(args.directory))
        raise SystemExit(1)

    # if given a specific category add that to the root
    # if args.category is not None:
    #     directory = directory / args.category
    #     if not directory.exists():
    #         logger.error("Given directory and category does not exist! {}".format(directory))
    #         raise SystemExit(1)

    logger.info('Importing automata from directory %s', directory.absolute())

    directory_tree = get_directory_tree(directory)

    # create session object
    s = requests.Session()
    # this argument defaults to false, if provided it will be true
    # a user who specifies this argument wants to NOT verify certificates so we negate the value
    s.verify = not args.ignorecert

    if int(args.retry) > 0:
        # session retry config
        retries = Retry(total=int(args.retry),
                        backoff_factor=0.2,
                        status_forcelist=[500, 502, 503, 504],
                        method_whitelist=False)
        s.mount('https://', HTTPAdapter(max_retries=retries))
        s.mount('http://', HTTPAdapter(max_retries=retries))

    # get token for session
    token = get_token(s, args.instance, args.username, args.password)
    s.headers = {'authorization': 'bearer ' + token}

    # get client
    client = get_client(s, args.instance, args.client)

    for node in tqdm(directory_tree, desc='Importing node tree into {}'.format(args.instance)):
        if type(node.val) is ExportedAutomaton:
            logger.debug('<Importing automaton: [{} > {}]'.format(node.path, node.val.name))
            existing_automaton = automaton_exists(s, args.instance, client, node.val.name)
            if existing_automaton:
                delete_automata(s, args.instance, existing_automaton)  # TODO make this not suck
                # node.val.id = existing_automaton['id']
                # update_automaton(s, args.instance, node.val)
                # continue

            # get or create parent category
            parent = create_parent(s, args.instance, client, node.path)
            if parent is None:
                logger.error('Skipping automaton because parent could not be found')
                continue

            # import automata into parent category
            automata = import_automaton(s, args.instance, parent.json(), node.val.name, node.val.json())

            if automata is None:
                continue

            # have to do this to try to get an automata object that the update endpoint will take
            automata = get_automaton_list_for_category(s, args.instance, parent)
            for automaton in automata:
                # update version to make it 'live'
                if automaton['name'] == node.val.name:
                    # new_version = automaton['latestAutomatonVersion']
                    # automaton['latestAutomatonVersion'] = None
                    # new_version['@id'] = None
                    # new_version['versionId'] = None
                    # new_version['versionNumber'] = None
                    # new_version['automaton'] = None
                    # new_version['serializedFlow'] = None
                    # new_version['live'] = True
                    # automaton['automatonVersion'] = new_version
                    # updated = update_automaton(s, args.instance, automaton)
                    latest = get_automaton_version_latest(s, args.instance, automaton)
                    submitted = submit_automaton_for_approval(s, args.instance, latest)
                    if submitted is None:
                        logger.error('Failed to submit automaton %s for approval', node.val.name)
                        continue
                    approved = approve_automaton(s, args.instance, submitted)
                    if approved:
                        logger.debug('Successfully imported and approved %s', node.val.name)
                    else:
                        logger.debug('Failed to approve automaton %s', node.val.name)

    print(f.renderText('FINISH !! --- {0:.3g} seconds'.format((time.time() - start_time))))


def do_wipe(args):
    print(f.renderText('Wipe Start !!'))
    start_time = time.time()

    # create session object
    s = requests.Session()
    # this argument defaults to false, if provided it will be true
    # a user who specifies this argument wants to NOT verify certificates so we negate the value
    s.verify = not args.ignorecert

    if int(args.retry) > 0:
        # session retry config
        retries = Retry(total=int(args.retry),
                        backoff_factor=0.2,
                        status_forcelist=[500, 502, 503, 504],
                        method_whitelist=False)
        s.mount('https://', HTTPAdapter(max_retries=retries))
        s.mount('http://', HTTPAdapter(max_retries=retries))

    # get token for session
    token = get_token(s, args.instance, args.username, args.password)
    s.headers = {'authorization': 'bearer ' + token}

    client = get_client(s, args.instance, args.client)
    automata_list = get_automaton_list_for_client(s, args.instance, client)
    category_list = get_category_list_for_client(s, args.instance, client)

    for automaton in tqdm(automata_list, desc='Deleting automata in {} {}'.format(args.instance, client['name'])):
        delete_automata(s, args.instance, automaton)

    for category in tqdm(category_list, desc='Deleting categories {} {}'.format(args.instance, client['name'])):
        delete_category(s, args.instance, category)

    print(f.renderText('FINISH !! --- {0:.3g} seconds'.format((time.time() - start_time))))


def main():
    print(f.renderText('clicmod v{}'.format(version)))

    # pars args
    subparsers = parser.add_subparsers()
    export_parser = subparsers.add_parser('export', help="Export automata from the given client/category")
    export_parser.set_defaults(func=do_export)
    import_parser = subparsers.add_parser('import', help="Import automata to the given client/category")
    import_parser.set_defaults(func=do_import)
    wipe_parser = subparsers.add_parser('wipe', help="Delete all automata and categories in the given client/category")
    wipe_parser.set_defaults(func=do_wipe)
    args = parser.parse_args()
    logger.setLevel(logging._nameToLevel[args.log])

    # for troubleshooting 
    logger.debug(ssl.OPENSSL_VERSION)

    # disable because it gets annoying
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # do something!
    args.func(args)


if __name__ == '__main__':
    main()
