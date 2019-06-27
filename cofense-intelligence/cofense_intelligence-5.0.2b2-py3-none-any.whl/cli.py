from __future__ import unicode_literals, absolute_import
'''
 Copyright 2013-2019 Cofense, Inc.  All rights reserved.

 This software is provided by PhishMe, Inc. ("Cofense") on an "as is" basis and any express or implied warranties,
 including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
 disclaimed in all aspects.  In no event will Cofense be liable for any direct, indirect, special, incidental or
 consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
 this software is pursuant to, and permitted only in accordance with, the agreement between you and Cofense.
'''

import argparse
import datetime
import sys
import os
from importlib import import_module
import json
import time
import logging

from jinja2 import Environment, PackageLoader

from cofense_intelligence.output import JsonFileOutput, CefFileOutput, CsvFileOutput, StixFileOutput, TextFileOutput
from cofense_intelligence.core import CFIntelSync
from cofense_intelligence.api import IntelligenceAPI


def valid_date(date):
    try:
        return datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentError('Not a valid date: {}'.format(date))


def valid_token(token):
    if len(token) != 32 and not isinstance(token, str):
        raise argparse.ArgumentError('Invalid authentication token. Ensure it is the correct user or password token')
    return token


def valid_name(integration_name):
    if not integration_name.isidentifier():
        raise RuntimeError('Invalid name, must be a valid python identifier See: https://docs.python.org/3.3/reference/lexical_analysis.html#identifiers')
    try:
        import_module(integration_name)
    except ImportError:
        pass
    else:
        raise RuntimeError('Name conflicts with the name of an existing Python package')

    return True


def setup_logger(args):
    if args.log_file == 'stdout':
        logging.basicConfig()
    else:
        logging.basicConfig(filename=args.log_file)

    logger = logging.getLogger()

    if args.log_level == 'info':
        logger.setLevel(logging.INFO)
    elif args.log_level == 'debug':
        logger.setLevel(logging.DEBUG)
    elif args.log_level == 'crit':
        logger.setLevel(logging.CRITICAL)
    elif args.log_level == 'warn':
        logger.setLevel(logging.WARN)

    return logger


def run_integration(args):

    integrations = {'json': JsonFileOutput,
                    'cef': CefFileOutput,
                    'csv': CsvFileOutput,
                    'stix': StixFileOutput,
                    'txt': TextFileOutput}

    if args.format == 'cef':
        fmt = 'cef'
    elif args.format == 'stix':
        fmt = 'stix'
    else:
        fmt = 'json'

    integration = integrations[args.format]

    logger = setup_logger(args)

    logger.debug("CLI logger has been configured")

    config = {'CF_USER': args.username,
              'CF_PASS': args.password,
              'INTEL_FORMAT': fmt,
              'THREAT_TYPE': args.intel_type,
              'BASE_DIR': args.base_dir,
              'INTEGRATION': integration,
              'ARGS': args}

    if args.proxy:
        logger.debug('Adding proxy data')
        proxy_config = {'PROXY_URL': args.proxy_addr}
        if args.proxy_user or args.proxy_pass:
            logger.debug('Adding proxy authentication data')
            proxy_config['PROXY_AUTH'] = True
            proxy_config['PROXY_USER'] = args.proxy_user
            proxy_config['PROXY_PASS'] = args.proxy_pass
        logger.debug('Updating the config with proxy data')
        config.update(proxy_config)

    if args.begin_date:
        logger.debug('Setting INIT_DATE')
        config['INIT_DATE'] = int(time.mktime(args.begin_date.timetuple()))
        logger.debug('INIT_DATE set to {}'.format(config['INIT_DATE']))

    if args.no_jitter:
        logger.debug('Turning off Jitter')
        config['JITTER'] = False

    if args.no_lock:
        logger.debug('Turning off lock file')
        config['USE_LOCK'] = False

    logger.debug('Creating the cofense handler')
    cf_handler = CFIntelSync(**config)

    logger.info('Running the integration...')
    cf_handler.run()
    logger.info('Integration complete.')


def execute():
    parser = argparse.ArgumentParser(description='Cofense Intelligence API Tool')

    subparsers = parser.add_subparsers()

    # Set up Run parsing
    run_parser = subparsers.add_parser('run',
                                       help='run Cofense Intelligence Integration')
    run_parser.add_argument('--username', '-u',
                            default=os.environ.get('COFENSE_USER'),
                            type=valid_token,
                            help='Cofense API username token, if not provided will use COFENSE_USER environment variable')
    run_parser.add_argument('--password', '-p',
                            default=os.environ.get('COFENSE_PASSWORD'),
                            type=valid_token,
                            help='Cofense API password token, if not provided will use COFENSE_PASSWORD environment variable')
    run_parser.add_argument('-f', '--format', choices=['json', 'cef', 'stix', 'csv', 'txt'], default='json', help='File output format')
    run_parser.add_argument('-d', '--begin-date', type=valid_date, help='Integration begin date')
    run_parser.add_argument('--no-jitter', action='store_true', help='Do not use jitter to delay run')
    run_parser.add_argument('--intel-type', choices=['malware', 'phish', 'all'], default='malware', help='ThreatReport Intelligence type (default Malware)')
    run_parser.add_argument('--log-level', choices=['debug', 'info', 'warn', 'error', 'crit'], help='Logging level set', default='info')
    run_parser.add_argument('--log-file', help='Log file to write to', default='stdout')
    run_parser.add_argument('--no-lock', action='store_true', help='Do not use lock file')
    run_parser.add_argument('--proxy', action='store_true', help='Use proxy for api requests')
    run_parser.add_argument('--proxy-addr', help='Set proxy address, if using different plain and ssl proxies specify ssl proxy')
    run_parser.add_argument('--proxy-user', help='Proxy username')
    run_parser.add_argument('--proxy-pass', help='Proxy password')
    run_parser.add_argument('--base-dir', default=os.getcwd(), help='Base directory to run from')
    run_parser.add_argument('--txt-domain-major', action='store_true', default=True)
    run_parser.add_argument('--txt-domain-major-file', default='cofense_major_domain.txt')
    run_parser.add_argument('--txt-ip-major', action='store_true', default=True)
    run_parser.add_argument('--txt-ip-major-file', default='cofense_major_ip.txt')
    run_parser.add_argument('--txt-url-major', action='store_true', default=True)
    run_parser.add_argument('--txt-url-major-file', default='cofense_major_url.txt')
    run_parser.add_argument('--txt-malicious-md5', action='store_true', default=True)
    run_parser.add_argument('--txt-malicious-md5-file', default='cofense_major_md5.txt')
    run_parser.add_argument('--txt-domain-moderate', action='store_true', default=False)
    run_parser.add_argument('--txt-domain-moderate-file', default='cofense_moderate_domain.txt')
    run_parser.add_argument('--txt-ip-moderate', action='store_true', default=False)
    run_parser.add_argument('--txt-ip-moderate-file', default='cofense_moderate_ip.txt')
    run_parser.add_argument('--txt-url-moderate', action='store_true', default=False)
    run_parser.add_argument('--txt-url-moderate-file', default='cofense_moderate_url.txt')
    run_parser.add_argument('--txt-domain-minor', action='store_true', default=False)
    run_parser.add_argument('--txt-domain-minor-file', default='cofense_minor_domain.txt')
    run_parser.add_argument('--txt-ip-minor', action='store_true', default=False)
    run_parser.add_argument('--txt-ip-minor-file', default='cofense_minor_ip.txt')
    run_parser.add_argument('--txt-url-minor', action='store_true', default=False)
    run_parser.add_argument('--txt-url-minor-file', default='cofense_minor_url.txt')
    run_parser.set_defaults(func=run_integration)

    # set up create_integration parsing
    create_parser = subparsers.add_parser('create', help='create custom Cofense Integration')
    create_parser.add_argument('name', help='Integration name')
    create_parser.add_argument('--target', default=os.getcwd(), help='Target directory for integration module')
    create_parser.set_defaults(func=create_integration)

    # Search parsing
    search_parser = subparsers.add_parser('search', help='search for Cofense Threat Intelligence reports. Output will be Threat ID, Threat Type and Brand or Malware Family')
    search_parser.add_argument('params', nargs='*', help='Search key value params (formatted key=value). See https://threathq.com/docs/rest_api_reference.html#threat for available params')
    search_parser.add_argument('--username', '-u',
                            default=os.environ.get('COFENSE_USER'),
                            type=valid_token,
                            help='Cofense API username token, if not provided will use COFENSE_USER environment variable')
    search_parser.add_argument('--password', '-p',
                            default=os.environ.get('COFENSE_PASSWORD'),
                            type=valid_token,
                            help='Cofense API password token, if not provided will use COFENSE_PASSWORD environment variable')
    search_parser.add_argument('-v', '--verbose', action='store_true', help='Output the full json of the threat report')
    search_parser.add_argument('-f', '--file', action='store_true', help='Output full json of each threat report to a file in a "results" directory')

    search_parser.set_defaults(func=search)

    # Submit a phish
    submit_parser = subparsers.add_parser('submit', help='Submit a phishing url and search for any Threat Reports containing it')
    submit_parser.add_argument('url', help='URL being submitted')
    submit_parser.add_argument('--username', '-u',
                            default=os.environ.get('COFENSE_USER'),
                            type=valid_token,
                            help='Cofense API username token, if not provided will use COFENSE_USER environment variable')
    submit_parser.add_argument('--password', '-p',
                            default=os.environ.get('COFENSE_PASSWORD'),
                            type=valid_token,
                            help='Cofense API password token, if not provided will use COFENSE_PASSWORD environment variable')
    submit_parser.add_argument('-v', '--verbose', action='store_true', help='Output the full json of the threat report')
    submit_parser.add_argument('-f', '--file', action='store_true', help='Output full json of each threat report to a file in a "results" directory')
    submit_parser.add_argument('--feed', help="Specific feed to submit to")
    submit_parser.set_defaults(func=submit)

    if len(sys.argv) == 1:
        parser.print_help()
        parser.error('Missing action')
        sys.exit(1)

    args = parser.parse_args()

    args.func(args)


def submit(args):
    print("Submitting Phishing URL: " + args.url)

    api_handler = IntelligenceAPI(auth=(args.username, args.password))
    status_code, content = api_handler.submit_phish(args.url, feed_id=args.feed)

    if status_code != 200:
        raise RuntimeError("Unable to submit Phish. Status Code: " + str(status_code))

    print("Phish submitted")

    threat_reports = api_handler.threat_search(urlSearch=args.url)

    for report in threat_reports:

        if not args.verbose or not args.file:
            print("Threat ID | Threat Type | Malware Family / Brand")
            print_summary(report)
        if args.verbose:
            print_full(report)
        if args.file:
            write_to_file(report)


def create_integration(args):
    print('creating integration: ' + args.name)

    valid_name(args.name)
    camel_case_name = ''.join(char for char in args.name.title() if char != '_')

    target_dir = args.target

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    env = Environment(loader=PackageLoader('cofense_intelligence', 'templates'))
    template = env.get_template('integration_template.py-ptl')
    output_file = template.render(integration_name=args.name, camel_case_name=camel_case_name)

    with open(args.name + '.py', 'w') as outfile:
        outfile.write(output_file)


def search(args):
    params = {}

    for pair in args.params:
        try:
            key, value = pair.split('=', 1)
        except ValueError:
            raise RuntimeError('Parameter [{}] could not be unpacked. Ensure params are passed as key=value pairs'.format(pair))

        params[key] = value

    auth = (args.username, args.password)

    api_handler = IntelligenceAPI(auth=auth)

    threat_reports = api_handler.threat_search(**params)

    if not args.verbose or not args.file:
        print("Threat ID | Threat Type | Malware Family / Brand")

    for report in threat_reports:
        if not args.verbose or not args.file:
            print_summary(report)
        if args.verbose:
            print_full(report)
        if args.file:
            write_to_file(report)


def print_summary(report):
    threat_id = report.threat_id
    threat_type = report.threat_type

    if threat_type == 'MALWARE':
        desc = report.malware_families
    else:
        desc = report.brands

    print(threat_id, ' | ', 'threat_type', ' | ', desc)


def print_full(report):
   print(report.json)


def write_to_file(report):
    results_dir = os.path.join(os.getcwd(), 'reports')
    results_file = os.path.join(results_dir, str(report.threat_id) + '.json')

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    with open(results_file, 'w') as report_file:
        json.dump(report.json, report_file)


if __name__ == '__main__':
    execute()





