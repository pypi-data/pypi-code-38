import requests
import json
import operator
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from ..config import config


def upload(data, params):
    itc_conf = params['itc_conf']
    bundle_id=itc_conf['BUNDLE_ID']
    for it in data:
        products = it.get('products', [])
        result = it.get('result', {})
        it['result'] = result
        if len(products) <= 0:
            continue
        payload = {'products': json.dumps(products), 'bundleId': bundle_id}
        callback = it.get('callback', None)
        params = it.get('callback_params', {})
        if not callback:
            continue
        try:
            print('callback: %s' % callback)
            print('callback_params: %s' % params)
            print('callback_payload: %s' % payload)
            if params.get('dry_run'):
                continue
            resp = requests.put(callback, params=params, json=payload)
            result['response'] = resp
            if resp and 200 <= resp.status_code < 400:
                print('resp data: %s\n\n\n' % resp.json())
            else:
                print('resp: %s\n\n\n' % resp)
        except:
            print('callback failed: %s' % callback)
            result['response'] = 'failed to upload to backend'

def handle(data, params):
    # mutating
    upload(data, params)
