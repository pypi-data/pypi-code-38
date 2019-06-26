from ..defs import defs

def validate(p):
    return True
    # 此处不需要根据价格过滤了，因为不支持的价格都会有一个缺省值，并且配置为不可销售
    if not p.get(defs.KEY_PRICE_PLAN):
        return False
    if p[defs.KEY_WHOLESALE_PRICE_TIER] == -1:
        print('ignore: id: %s, name: %s' % (p[defs.KEY_PRODUCT_ID], p[p['locales'][0]][defs.KEY_TITLE]))
        return False
    product_type = p[defs.KEY_TYPE]
    price_tier = p[defs.KEY_WHOLESALE_PRICE_TIER]
    if product_type != defs.CONST_NON_CONSUMABLE and price_tier <= 0:
        return False
    return True

