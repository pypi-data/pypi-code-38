import operator
from ..defs import defs

def extract_price(it):
    if not it or not it.get('products', []):
        return None
    ret = {}
    meta = it['meta']
    ret['meta'] = {}
    ret['meta'].update(meta)
    ret['meta']['key_map'] = None
    ret['result'] = it.get('result', {})
    ret['callback'] = meta.get('callback', None)
    ret['callback_params'] = meta.get('callback_params', None)

    products = it.get('products', [])
    ret['products'] = list(map(
        lambda p: {
            'product_id': p[defs.KEY_PRODUCT_ID],
            'product_price': int(100 * p[defs.KEY_APPSTORE_PRICE])
        },
        products
    ))
    return ret
