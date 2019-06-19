import requests
import json
from iapsync.model.price import extract_price
from iapsync.defs import defs
from iapsync.config.config import APPSYNC_URL

# 不用了
def upload(data, params):
    itc_conf = params['itc_conf']
    bundle_id=itc_conf['BUNDLE_ID']
    for itraw in data:
        it = extract_price(itraw)
        if not it:
            continue
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


def upload_snapshot(data, params):
    itc_conf = params['itc_conf']
    bundle_id=itc_conf['BUNDLE_ID']
    for by_env in data:
        if not by_env:
            continue
        products = by_env.get('products', [])
        if not products:
            continue
        url = APPSYNC_URL.get(by_env['api_env'])
        if not url:
            continue
        body = {}
        body['priceMappingId'] = by_env['price_mapping_id']
        body['bundleId'] = bundle_id
        body['products'] = []
        for p in products:
            item = {}
            item['productId'] = p[defs.KEY_PRODUCT_ID]
            item['origPrice'] = p[defs.CONST_ORIG_PRICE]
            item['discountPrice'] = p[defs.CONST_PRICE]
            item['promotions'] = p[defs.CONST_PROMOTIONS]
            if p.get(defs.KEY_PRICE_PLAN):
                item['pricePlan'] = p[defs.KEY_PRICE_PLAN]
            body['products'].append(item)
        resp = requests.post(url + '/api/appstore/product', json=body).json()
        if not resp or resp.get('code') != 0:
            raise ValueError('Failed to upload product snapshot')


def handle(data, params):
    upload_snapshot(data, params)
