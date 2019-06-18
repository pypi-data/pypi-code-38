import requests
import time
from datetime import date, timedelta, timezone, datetime
from functools import reduce
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import pprint
from ..defs import defs
from iapsync.config.config import APPSYNC_URL

def _format_time(t):
    formatted_time = datetime.fromtimestamp(
            int(t),
            timezone(timedelta(hours=8))).strftime('%Y-%m-%d')
    return formatted_time

pp = pprint.PrettyPrinter(indent=4)

def access_list(obj, key_path):
    key_paths = key_path.split('.')
    ret = obj
    for k in key_paths:
        ret = ret[k]
    return ret

# FIXME: wansong, 固定修改tuple第五个参数，容易收到api更新的影响
def add_query(url_str, params):
    obj = list(urlparse(url_str))
    new_query = {}
    if obj[4]:
        query = dict(parse_qsl(obj[4]))
        new_query.update(query)
    new_query.update(params)
    obj[4] = urlencode(new_query)
    return urlunparse(obj)

def get_price_plan_url(api_env):
    url = APPSYNC_URL.get(api_env, None)
    if not url:
        return None
    return url + '/api/appstore/calc-price-plan'

def get_products(api_meta, options):
    metas = api_meta if isinstance(api_meta, list) else [api_meta]
    ret = []
    for mt in metas:
        env = mt['env']
        api = mt['api']
        k_m = mt['key_map']
        # 如果target_env=all则获取全部环境的数据；否则只获取对应环境的
        api_env=env.split('.')[0]
        # 历史原因，有两个app的'env'字段的格式不是api_env.app_name：名师课app(api_env)，斩雅思app(live, dev.live)
        if api_env not in ['dev', 'sim', 'prod']:
            if env == 'live':
                api_env = 'prod'
            else:
                raise ValueError("'env' 字段不合法：%s" % env)

        if options['target_env'] != 'all' and api_env != options['target_env']:
            continue
        by_env = {'meta': mt, 'api_env': api_env, 'products': []}
        ret.append(by_env)
        api2 = add_query(api, { 'allPromotions': 1 })
        print('api: %s, api2: %s' % (api, api2))
        json = requests.get(api2).json()
        if not isinstance(json, list) and not isinstance(json, dict):
            continue
        product_list = access_list(json, mt['key_path'])

        api_price_plan = get_price_plan_url(api_env)
        if not api_price_plan:
            raise ValueError('No api_price_plan for this api_env(%s)' % api_env)
        # FIXME: wansong, 添加原价字段，目前是写死的CONST_PRICE = 'price'
        formatted = list(
            {
                'productId': k_m[defs.KEY_PRODUCT_RAW_ID](p),
                'acceptZero': k_m[defs.KEY_TYPE](p) == defs.CONST_NON_CONSUMABLE,
                'origPrice': float(p[defs.CONST_PRICE]),
                'promotions': p.get('allPromotions', [])}
            for p in product_list
            )
        resp = requests.post(api_price_plan, json=formatted).json()
        if not resp or resp.get('code') != 0:
            raise ValueError('Failed to get price plan')
        price_plan_info = resp['data']
        by_env['price_mapping_id'] = price_plan_info['priceMapping']['id']
        max_tier = price_plan_info['priceMapping']['data'][-1]
        # 构造价格计划、可供销售的哈希表
        price_plans_by_id = {}
        for plan in price_plan_info['pricePlans']:
            formatted_plan = []
            for item in plan['pricePlan']:
                appstore_plan = {}
                appstore_plan['start_date'] = _format_time(item['startDate'])
                # 没有tier说明AppStore不支持该价格，此处直接忽略，appsync会预测时候以后价格又有更改并安排定时同步
                if not item.get('priceTier'):
                    continue
                appstore_plan['priceTier'] = item['priceTier']
                if item.get('endDate'):
                    appstore_plan['end_date'] = _format_time(item['endDate'])
                formatted_plan.append(appstore_plan)
            # 如果当前的价格不支持，就设置不可销售，并且使用最大的tier值（至少有一个合法的interval保证可以上传成功）
            if not formatted_plan:
                formatted_plan = [{
                    'start_date': _format_time(int(time.time())),
                    'priceTier': max_tier
                    }]
            price_plans_by_id[plan['productId']] = {
                'plan': formatted_plan,
                'forSale': plan.get('nowTier', None) is not None
                }

        for p in product_list:
            if options.get('verbose'):
                print('fetched product:')
                pp.pprint(p)
                print('\n')
            raw_id = k_m[defs.KEY_PRODUCT_RAW_ID](p)
            is_for_sale = price_plans_by_id[raw_id]['forSale'] and (
                k_m[defs.KEY_CLEARED_FOR_SALE](p) if k_m[defs.KEY_CLEARED_FOR_SALE] else True)
            # 这个env用于商品id前缀
            new_item = {
                defs.KEY_ENV: env,
                defs.KEY_PRODUCT_RAW_ID: k_m[defs.KEY_PRODUCT_RAW_ID](p),
                defs.KEY_REFERENCE_NAME: k_m[defs.KEY_REFERENCE_NAME](p),
                defs.KEY_TYPE: k_m[defs.KEY_TYPE](p),
                defs.KEY_REVIEW_SCREENSHOT:
                    k_m[defs.KEY_REVIEW_SCREENSHOT](p) if k_m[defs.KEY_REVIEW_SCREENSHOT] else None,
                defs.KEY_REVIEW_NOTES:
                    k_m[defs.KEY_REVIEW_SCREENSHOT](p) if k_m[defs.KEY_REVIEW_SCREENSHOT] else mt['review_notes'],
                defs.CONST_PRICE: k_m[defs.CONST_PRICE](p),
                defs.KEY_CLEARED_FOR_SALE: is_for_sale,
                defs.KEY_VALIDITY: k_m[defs.KEY_VALIDITY](p) if k_m.get(defs.KEY_VALIDITY, None) else None,
                defs.KEY_VALIDITY_TYPE:
                    k_m[defs.KEY_VALIDITY_TYPE](p) if k_m.get(defs.KEY_VALIDITY_TYPE, None) else None,
                    defs.KEY_PRICE_PLAN: price_plans_by_id.get(k_m[defs.KEY_PRODUCT_RAW_ID](p), {'plan': None})['plan'],
                defs.CONST_PROMOTIONS: p.get('allPromotions', []),
                # FIXME: wansong, 添加原价字段，目前是写死的CONST_PRICE = 'price'
                defs.CONST_ORIG_PRICE: p[defs.CONST_PRICE]
            }
            locates = mt['locales']
            new_item['locales'] = locates
            for lc in locates:
                desc = {
                    defs.KEY_TITLE: k_m[lc][defs.KEY_TITLE](p),
                    defs.KEY_DESCRIPTION: k_m[lc][defs.KEY_DESCRIPTION](p),
                }
                new_item[lc] = desc
            by_env['products'].append(new_item)
            if options.get('verbose'):
                print('properties extract:')
                pp.pprint(new_item)
                print('\n')
    return ret

