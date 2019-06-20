from datetime import datetime
from ..defs import defs

def pad_or_trim(s, max, min):
    ll = len(s)
    if ll < min:
        return s + '*' * (min - ll)
    if ll > max:
        return s[:max]
    return s


def fix_title(product, options):
    locales = product.locales()
    for lc in locales:
        t = product.title(lc)
        fixed = pad_or_trim(t, options['NAME_MAX'], options['NAME_MIN'])
        product.set_title(fixed, lc)
    return product


def fix_description(product, options):
    locales = product.locales()
    for lc in locales:
        t = product.description(lc)
        fixed = pad_or_trim(t, options['DESC_MAX'], options['DESC_MIN'])
        product.set_description(fixed, lc)
    return product

def fix_review(product, options):
    r = product.review_notes()
    fixed = pad_or_trim(r, options['REVIEW_MAX'], options['REVIEW_MIN'])
    product.set_review_notes(fixed)
    return product

def fix_reference_name(product, options):
    t = product.reference_name()
    fixed = pad_or_trim(t, options['REF_NAME_MAX'], options['REF_NAME_MIN'])
    product.set_reference_name(fixed)
    return product

def add_validity(product, options):
    if product.type() != defs.CONST_SUBSCRIPTION:
        return product

    validity_type = product.validityType()
    validity = product.validity()
    if validity is None or validity_type is None:
        return product

    if int(validity_type) == 1:
        validity_desc = '有效期%d天。' % int(validity)
    elif int(validity_type == 2):
        validity_desc = '有效期至%s。' % datetime.fromtimestamp(int(validity)).strftime('%Y-%m-%d')
    else:
        return product

    locales = product.locales()
    for lc in locales:
        t = product.description(lc)
        with_validity = '%s%s' % (validity_desc, t)
        fixed = pad_or_trim(
            with_validity,
            options['DESC_MAX'],
            options['DESC_MIN'])
        product.set_description(fixed, lc)
    return product


def product_id(p, options):
    env = p.env()
    raw_id = p.raw_id()
    p.wrapped()[defs.KEY_PRODUCT_ID] = '%s.%s' % (env, str(raw_id))
    return p


def convert_product(product, options):
    converters = [product_id, fix_description, add_validity, fix_title, fix_review, fix_reference_name]
    ret = product
    for t in converters:
        ret = t(ret, options)
    return ret


def check_title(p, lc, options):
    t = p.title(lc)
    return options['NAME_MIN'] <= len(t) <= options['NAME_MAX']


def check_desc(p, lc, options):
    d = p.description(lc)
    return options['DESC_MIN'] <= len(d) <= options['DESC_MAX']


def check_review_note(p, options):
    r = p.review_notes()
    return options['REVIEW_MIN'] <= len(r) <= options['REVIEW_MAX']


def fix_appstore_product(p, options):
    lcs = p.locales()
    for lc in lcs:
        if not check_title(p, lc, options):
            fix_title(p, options)
        if not check_desc(p, lc, options):
            fix_description(p, options)

    if not check_review_note(p, options):
        fix_review(p, options)

    return p
