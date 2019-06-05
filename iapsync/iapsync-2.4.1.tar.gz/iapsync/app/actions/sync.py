import sys
import shutil
import subprocess
from lxml import etree
import hashlib
import urllib
import operator
import functools
from pathlib import Path, PurePath
from iapsync.defs import defs
from iapsync.config import config
from iapsync.remote.fetch import get_products
from iapsync.convert.convert import convert_product, fix_appstore_product
from iapsync.model.product import AppStoreProduct, XML_NAMESPACE, Product
from iapsync.model.price import extract_price
from iapsync.validate import validate
from iapsync.utils.transporter import transporter_path


def convert_product_data(data, options):
    def conv(d):
        ret = {}
        ret.update(d)
        ret['products'] = list(map(
            lambda p: convert_product(Product(p), options).wrapped(),
            ret['products']
        ))
        return ret
    return list(map(conv, data))


def filter_product_data(data, options):
    def filt(d):
        ret = {}
        ret.update(d)
        products = list(filter(
            lambda pp: pp[defs.KEY_PRODUCT_ID] not in options['excludes'] and validate.validate(pp),
            d['products']))
        ret['products'] = products
        return ret
    return list(map(filt, data))



def is_product_changed(product_elem, product_dict, price_only=False):
    pm = AppStoreProduct(product_elem)
    # cleared_for_sale, type is always checked
    cleared_for_sale_now = pm.cleared_for_sale()
    cleared_for_sale_next = product_dict[defs.KEY_CLEARED_FOR_SALE]
    if cleared_for_sale_next and not cleared_for_sale_now:
        return True
    if cleared_for_sale_now and not cleared_for_sale_next:
        return True

    type_now = pm.type() if pm.type() else ''
    type_next = product_dict[defs.KEY_TYPE] if product_dict[defs.KEY_TYPE] else ''
    if type_now.strip() != type_next.strip():
        print('type changed from: "%s" to: "%s"' % (type_now, type_next))
        return True

    price_tier_now = pm.price_tier()
    price_tier_next = int(product_dict[defs.KEY_WHOLESALE_PRICE_TIER])
    if price_tier_now != price_tier_next:
        print('price_tier changed from: "%s" to: "%s"' % (price_tier_now, price_tier_next))
        return True

    # only care about price tier
    if price_only:
        return False

    review_notes_now = pm.review_notes() if pm.review_notes() else ''
    review_notes_next = product_dict[defs.KEY_REVIEW_NOTES] if product_dict[defs.KEY_REVIEW_NOTES]  else ''
    if review_notes_next.strip() != review_notes_now.strip():
        print('review note changed from: "%s" to: "%s"' % (review_notes_now, review_notes_next))
        return True

    locales = product_dict['locales']
    for lc in locales:
        title_now = pm.title(lc) if pm.title(lc) else ''
        title_next = product_dict[lc][defs.KEY_TITLE] if product_dict[lc][defs.KEY_TITLE] else ''
        if title_next.strip() != title_now.strip():
            print('title changed from(%s): "%s" to: "%s"' % (lc, title_now, title_next))
            return True

        desc_now = pm.description(lc) if pm.description(lc) else ''
        desc_next = product_dict[lc][defs.KEY_DESCRIPTION] if product_dict[lc][defs.KEY_DESCRIPTION] else ''
        if desc_next.strip() != desc_now.strip():
            print('desc changed from(%s): "%s" to: "%s"' % (lc, desc_now, desc_next))
            return True

    return False


def fix_appstore_screenshots(in_app_purchases, opts):
    nspc = opts['nspc']
    screenshot_dir = opts['screenshot_dir']
    existing_iaps = in_app_purchases.xpath(
        'x:in_app_purchase',
        namespaces=nspc
    )

    if not existing_iaps or len(existing_iaps) <= 0:
        return

    # bundled default screenshot
    DEFAULT_SCREENSHOT_PATH = config.DEFAULT_SCREENSHOT_PATH
    screenshot_file = Path(DEFAULT_SCREENSHOT_PATH)
    md5 = hashlib.md5(open(screenshot_file.as_posix(), 'rb').read()).hexdigest()
    size = screenshot_file.stat().st_size

    for p in existing_iaps:
        pid = p.xpath(
            'x:product_id',
            namespaces=nspc
        )[0].text

        size_node = p.xpath(
            'x:review_screenshot/x:size',
            namespaces=nspc
        )[0]
        md5_node = p.xpath(
            'x:review_screenshot/x:checksum[@type="md5"]',
            namespaces=nspc
        )[0]
        name_node = p.xpath(
            'x:review_screenshot/x:file_name',
            namespaces=nspc
        )[0]
        screenshot_name = '%s.%s' % (pid, 'png')
        name_node.text = screenshot_name
        md5_node.text = str(md5)
        size_node.text = str(size)
        screenshot_path = screenshot_dir.joinpath(screenshot_name).as_posix()
        shutil.copy(DEFAULT_SCREENSHOT_PATH, screenshot_path)


def fix_appstore_products(in_app_purchases, options):
    nspc = options['nspc']
    params = options['params']
    limits = params['limits']
    existing_iaps = in_app_purchases.xpath(
        'x:in_app_purchase',
        namespaces=nspc
    )

    if not existing_iaps or len(existing_iaps) <= 0:
        return

    for p in existing_iaps:
        pp = AppStoreProduct(p)
        fix_appstore_product(pp, limits)


def update_product(elem, p, options):
    price_only = options.get('price_only', False)

    pm = AppStoreProduct(elem)
    if not is_product_changed(elem, p, price_only):
        return False

    print('update: id: %s, name: %s' % (p[defs.KEY_PRODUCT_ID], p[p['locales'][0]][defs.KEY_TITLE]))

    locales = p['locales']
    # print('update: now: %s, next: %s' % (pm, Product(Product.create_node(p))))
    pm.set_price_tier(p[defs.KEY_WHOLESALE_PRICE_TIER])
    pm.set_cleared_for_sale(p[defs.KEY_CLEARED_FOR_SALE])
    pm.set_reference_name(p[defs.KEY_REFERENCE_NAME])
    pm.set_review_notes(p[defs.KEY_REVIEW_NOTES])
    for lc in locales:
        pm.set_title(p[lc][defs.KEY_TITLE], lc)
        pm.set_description(p[lc][defs.KEY_DESCRIPTION], lc)

    return True

def find_product(in_app_purchases, product_dict, nspc):
    res_set = in_app_purchases.xpath(
        'x:in_app_purchase[x:product_id[text()=$pid]]',
        namespaces=nspc,
        pid=product_dict[defs.KEY_PRODUCT_ID]
    )
    return res_set[0] if len(res_set) > 0 else None


def append_product(in_app_purchases, product_dict):
    node = AppStoreProduct.create_node(product_dict)
    in_app_purchases.append(node)


def run(params, opts, agg_ret):
    namespaces = opts['namespaces']

    api_meta = params['api_meta']
    defaults = params['defaults']
    excludes = params['excludes']
    limits = params['limits']
    APP_SKU = params.get('APP_SKU', None)
    APPLE_ID = params['itc_conf'].get('APPLE_ID', None)
    BUNDLE_ID = params['itc_conf']['BUNDLE_ID']
    APPSTORE_PACKAGE_NAME = params['APPSTORE_PACKAGE_NAME']
    username = params['username']
    password = params['password']

    DEFAULT_SCREENSHOT_PATH = config.DEFAULT_SCREENSHOT_PATH
    if defaults and defaults.get('DEFAULT_SCREENSHOT_PATH'):
        DEFAULT_SCREENSHOT_PATH = defaults.get('DEFAULT_SCREENSHOT_PATH')

    app_store_dir = Path(config.APPSTORE_META_DIR).joinpath(BUNDLE_ID + '-' + params['env'])
    skip_appstore = params.get('skip_appstore', False)
    if not skip_appstore:
        # clear APPSTORE_META dir
        if app_store_dir.exists():
            shutil.rmtree(app_store_dir.as_posix())
        app_store_dir.mkdir(parents = True)
        itms = params['itms'] if params['itms'] else transporter_path
        cmd = [itms, '-m', 'lookupMetadata',
               '-u', username,
               '-p', password,
               '-destination', app_store_dir.as_posix(),
               '-subitemtype', 'InAppPurchase',
               ]
        if APPLE_ID is not None:
            cmd.append('-apple_id')
            cmd.append(APPLE_ID)
        elif APP_SKU is not None:
            cmd.append('-vendor_id')
            cmd.append(APP_SKU)
        else:
            sys.exit('Neither APPLE_ID nor APP_SKU exists!')
        # 下载App Store元数据
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as err:
            print('获取App Store数据失败：%s.' % err.returncode)
            raise err
        print('下载App Store元数据完成.')


    # clear tmp dir
    tmp_dir = Path(config.TMP_DIR).joinpath(BUNDLE_ID + '-' + params['env'])
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir.as_posix())
    tmp_dir.mkdir(parents = True)

    # 初始化etree
    metadata_path = app_store_dir.joinpath(APPSTORE_PACKAGE_NAME).joinpath(config.APPSTORE_METAFILE)
    try:
        f = open(metadata_path.as_posix(), mode='rb')
        doc_tree = etree.parse(f)

    except OSError:
        print('io 错误：%s' % sys.exc_info()[0])
        raise
    except:
        print('拷贝元数据失败：%s.' % sys.exc_info()[0])
        raise

    # 访问etree/.../in_app_purchases
    software_metadata_q = doc_tree.xpath('/x:package/x:software/x:software_metadata', namespaces = namespaces)
    if len(software_metadata_q) != 1:
        err = 'xpath fail: package/software/software_metadata should point to a single tag, but found: %d' % len(software_metadata_q)
        raise TypeError(err)
    software_metadata = software_metadata_q[0]

    # patch fix ITMS-90723
    versions = software_metadata.xpath('x:versions', namespaces = namespaces)
    for v in versions:
        v.getparent().remove(v)

    in_app_purchases_q = software_metadata.xpath('x:in_app_purchases', namespaces = namespaces)
    if len(in_app_purchases_q) <= 0:
        in_app_purchases = etree.SubElement(software_metadata, '{%s}in_app_purchases' % XML_NAMESPACE)
    else:
        in_app_purchases = in_app_purchases_q[0]

    new_package_path = tmp_dir.joinpath(APPSTORE_PACKAGE_NAME)
    options = {
        'default_screenshot': DEFAULT_SCREENSHOT_PATH,
        'screenshot_dir': new_package_path.as_posix()
    }
    options.update(limits)
    options.update(params)
    options['excludes'] = excludes

    # 下载后台商品数据
    # 转换，计算价格阶梯，必须先于filter，后者排出阶梯=-1的商品
    data = convert_product_data(get_products(api_meta, options), options)
    data = filter_product_data(data, options)
    if not data or len(data) <= 0:
        print('nothing to do, no products fetched')
        sys.exit(0)

    # copy screenshots，顺序相关，必须在update_product之前运行，不然无法计算size, md5
    new_package_path.mkdir(parents=True)
    for data_item in data:
        products = data_item.get('products', [])
        if len(products) <= 0:
            continue

        for pp in products:
            screenshot_path = new_package_path.joinpath('%s.%s' % (pp[defs.KEY_PRODUCT_ID], 'png')).as_posix()
            screenshot_url = pp[defs.KEY_REVIEW_SCREENSHOT]
            if screenshot_url:
                try:
                    urllib.request.urlretrieve(screenshot_url, screenshot_path)
                except:
                    shutil.copy(DEFAULT_SCREENSHOT_PATH, screenshot_path)
            else:
                pp[defs.KEY_REVIEW_SCREENSHOT] = screenshot_path
                shutil.copy(DEFAULT_SCREENSHOT_PATH, screenshot_path)

    # merge in_app_purchases
    for data_item in data:
        products = data_item.get('products', [])
        if len(products) <= 0:
            continue
        updated = []
        added = []
        for p in products:
            e = find_product(in_app_purchases, p, namespaces)
            if e is None:
                if p[defs.KEY_PRODUCT_ID] not in excludes:
                    print('new: id: %s, name: %s' % (p[defs.KEY_PRODUCT_ID], p[p['locales'][0]][defs.KEY_TITLE]))
                    append_product(in_app_purchases, p)
                    added.append(p)
            else:
                did_update = update_product(e, p, params)
                if did_update:
                    updated.append(p)
        data_item['result'] = {'updated': updated, 'added': added}

    # appstore screenshot may used to be edited manually, which cannot pass verify
    # : screenshot name and stats not persistent, fix by writing them
    if params.get('fix_screenshots'):
        fix_appstore_screenshots(in_app_purchases, {'nspc': namespaces, 'screenshot_dir': new_package_path})

    if params.get('force_update'):
        fix_appstore_products(in_app_purchases, {'nspc': namespaces, 'params': params})

    # save things
    new_metafile_path = new_package_path.joinpath(config.APPSTORE_METAFILE)
    doc_tree.write(new_metafile_path.as_posix(), pretty_print=True, xml_declaration = True, encoding='utf-8')
    return extract_price(data)


