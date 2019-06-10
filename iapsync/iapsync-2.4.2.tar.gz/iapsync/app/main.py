#! /usr/bin/env python3

import argparse
from iapsync.model.product import XML_NAMESPACE
from iapsync.app.actions import actions
from iapsync.utils.args import extract_params
from iapsync.utils.mail import send_notify_mail
import pkg_resources

_APP_VER = pkg_resources.get_distribution('iapsync').version

def main():
    ''' Entry point '''
    parser = argparse.ArgumentParser(
        description='''iapsync({appVersion})
    关于mode：
        -m sync: fetch from api defined by --config-file, generate itmsp package, for uploading to itunesconnect
        -m verify: first do the work of sync mode, then verify generated itmsp package by sync mode
        -m upload: first do the work of verify, then upload generated itmsp package to itunes connect by sync mode
        '''.format(appVersion=_APP_VER),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-c', '--config-file')
    parser.add_argument('-m', '--mode', choices=['sync', 'verify', 'upload'])
    parser.add_argument('-e', '--env', default='all', type=str, choices=['dev', 'sim', 'prod'])
    parser.add_argument('--force-update', default=False, type=bool)
    parser.add_argument('--send-mail', default=False, type=bool)
    parser.add_argument('--skip-appstore', default=False, type=bool)
    parser.add_argument('--itms', default='', type=str, help='path to iTMSTransporter binary')
    parser.add_argument('--price-only', default=False, type=bool)
    parser.add_argument('--fix-screenshots', default=False, type=bool)
    parser.add_argument('--ceil-price', default=False, type=bool)
    parser.add_argument('--dry-run', default=False, type=bool)
    parser.add_argument('-v', '--verbose', default=False, type=bool)
    parser = parser.parse_args()
    params = extract_params(parser)
    steps = actions[parser.mode]
    agg_ret = None
    for step in steps:
        agg_ret = step(params, {'namespaces': {'x': XML_NAMESPACE}}, agg_ret)
    # 邮件通知
    print('mode: %s' % params['mode'])
    if params['mode'] == 'upload' or params['send_mail']:
        print('Send mail...')
        send_notify_mail(agg_ret, params)
    else:
        print('No send mail.')
