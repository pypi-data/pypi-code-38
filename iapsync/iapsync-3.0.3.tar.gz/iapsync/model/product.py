__author__ = 'wansongHome'
import hashlib
from datetime import date, timedelta, timezone, datetime
from lxml import etree
from copy import deepcopy

from pathlib import PurePath, Path
from ..defs import defs

XML_NAMESPACE = 'http://apple.com/itunes/importer'

YESTODAY = (date.today() + timedelta(days = -1)).strftime('%Y-%m-%d')
TODAY = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d')
print('Asia/Shanghai date: %s' % TODAY)

__template_str = '''
<in_app_purchase xmlns="%s">
    <product_id>111111111111111</product_id>
    <reference_name>11111111111111111</reference_name>
    <type>not-sure-yet</type>
    <products>
        <product>
            <cleared_for_sale>true</cleared_for_sale>
            <intervals>
                <interval>
                    <start_date>%s</start_date>
                    <wholesale_price_tier>1</wholesale_price_tier>
                </interval>
            </intervals>
        </product>
    </products>
    <locales>
        <locale name="en-US">
            <title>11111111111111</title>
            <description>11111111111111</description>
        </locale>
        <locale name="zh-Hans">
            <title>11111111111</title>
            <description>111111111111</description>
        </locale>
    </locales>
    <review_screenshot>
        <size>111111111111</size>
        <file_name>111111111111</file_name>
        <checksum type="md5">111111111111111</checksum>
    </review_screenshot>
    <review_notes>1111111111111111</review_notes>
</in_app_purchase>
''' % (XML_NAMESPACE, YESTODAY)

TEMPLATE_NODE = etree.fromstring(__template_str)

class AppStoreProduct:
    @staticmethod
    def create_node(p_dict):
        ret = deepcopy(TEMPLATE_NODE)
        pm = AppStoreProduct(ret)

        pm.set_product_id(p_dict[defs.KEY_PRODUCT_ID])
        pm.set_reference_name(p_dict[defs.KEY_REFERENCE_NAME])
        pm.set_price_plan(p_dict[defs.KEY_PRICE_PLAN])
        pm.set_type(p_dict[defs.KEY_TYPE])
        locs = p_dict['locales']
        for loc in locs:
            pm.set_title(p_dict[loc][defs.KEY_TITLE], loc)
            pm.set_description(p_dict[loc][defs.KEY_DESCRIPTION], loc)

        screenshot_file = Path(p_dict[defs.KEY_REVIEW_SCREENSHOT])
        md5 = hashlib.md5(open(screenshot_file.as_posix(), 'rb').read()).hexdigest()
        pm.set_screenshot_md5(md5)
        pm.set_screenshot_size(screenshot_file.stat().st_size)
        pm.set_screenshot_name(PurePath(p_dict[defs.KEY_REVIEW_SCREENSHOT]).name)
        pm.set_review_notes(p_dict[defs.KEY_REVIEW_NOTES])
        pm.set_cleared_for_sale(p_dict[defs.KEY_CLEARED_FOR_SALE])
        return ret

    @classmethod
    def mkpath_if_needed_cls(cls, base, paths):
        namespaces = {'x': XML_NAMESPACE }
        cur = base
        for p in paths:
            part = cur.xpath('x:%s' % p, namespaces=namespaces)
            if not part:
                part = etree.SubElement(cur, '{%s}%s' % (XML_NAMESPACE, p))
                cur = part
            else:
                cur = part[0]


    @classmethod
    def query_cls(cls, root, paths):
        ''' 添加命名空间，返回xpath查询结果（数组类型） '''
        with_nsp = ['x:{}'.format(p) for p in paths]
        query_str = '/'.join(with_nsp)
        return root.xpath(query_str, namespaces={'x': XML_NAMESPACE})

    @classmethod
    def upsert_cls(cls, root, paths, text):
        ''' query，然后设置text值 '''
        cls.mkpath_if_needed_cls(root, paths)
        for n in cls.query_cls(root, paths):
            n.text = str(text)


    def __init__(self, p_elem):
        self.elem = p_elem
        self.namespaces = {'x': XML_NAMESPACE}

    def mkpath_if_needed(self, paths):
        AppStoreProduct.mkpath_if_needed_cls(self.elem, paths)

    def query(self, paths):
        return AppStoreProduct.query_cls(self.elem, paths)

    def upsert(self, paths, text):
        ''' query，然后设置text值 '''
        AppStoreProduct.upsert_cls(self.elem, paths, text)

    def locales(self):
        return self.elem.xpath(
            'x:locales/x:locale/@name',
            namespaces=self.namespaces
        )

    def price_plan(self):
        intervals = self.elem.xpath(
            'x:products/x:product/x:intervals/x:interval',
            namespaces = self.namespaces
        )
        if not intervals:
            return []
        ret = []
        for intv in intervals:
            start_date = intv.xpath(
                    'x:start_date',
                    namespaces=self.namespaces
                    )[0].text
            value = intv.xpath(
                    'x:wholesale_price_tier',
                    namespaces=self.namespaces
                    )[0].text
            end_date_maybe = intv.xpath(
                    'x:end_date',
                    namespaces=self.namespaces
                    )
            item = { 'start_date': start_date, 'tierId': int(value) }
            if end_date_maybe:
                item['end_date'] = end_date_maybe[0].text
            ret.append(item)
        return ret

    def set_price_plan(self, price_plan):
        self.mkpath_if_needed(['products', 'product', 'intervals'])
        interval_container = self.query(['products', 'product', 'intervals'])[0]
        intervals = self.query(['products', 'product', 'intervals', 'interval'])
        existing_cnt = len(intervals) if intervals else 0
        for ii, plan in enumerate(price_plan):
            if ii >= existing_cnt:
                n = etree.SubElement(interval_container, '{%s}interval' % XML_NAMESPACE)
            else:
                n = intervals[ii]
            AppStoreProduct.upsert_cls(n, ['start_date'], plan['startDate'])
            AppStoreProduct.upsert_cls(n, ['wholesale_price_tier'], plan['priceTier']['tier']['id'])
            if plan.get('endDate'):
                AppStoreProduct.upsert_cls(n, ['end_date'], plan['endDate'])
        # 删除多余的
        for ii in range(len(price_plan), existing_cnt):
            to_rm = intervals[ii]
            to_rm.getparent().remove(to_rm)


    def is_price_plan_equal(self, next_plan):
        now_plan = self.price_plan()
        if not now_plan:
            raise ValueError('当前价格区间是空的')
        if not next_plan:
            raise ValueError('更新价格区间是空的')
        # 找到起始区间
        ii = 0
        while ii < len(now_plan) and now_plan[ii].get('end_date') and now_plan[ii]['end_date'] <= TODAY:
            ii += 1
        if ii >= len(now_plan):
            raise ValueError('当前价格区间不合法')
        jj = 0
        while jj < len(next_plan) and next_plan[jj].get('endDate') and next_plan[jj]['endDate'] <= TODAY:
            jj += 1
        if jj >= len(next_plan):
            raise ValueError('更新价格区间不合法')

        if now_plan[ii]['tierId'] != next_plan[jj]['priceTier']['tier']['id']:
            return False
        if now_plan[ii].get('end_date', -1) != next_plan[jj].get('endDate', -1):
            return False
        ii += 1
        jj += 1
        if len(now_plan) - ii != len(next_plan) - jj:
            return False
        # FIXME: 更智能的比较
        while ii < len(now_plan):
            now_item = now_plan[ii]
            next_item = next_plan[jj]
            if now_item['start_date'] != next_item['startDate']:
                return False
            if now_item.get('end_date', -1) != next_item.get('endDate', -1):
                return False
            if now_item['tierId'] != next_item['priceTier']['tier']['id']:
                return False
            ii += 1
            jj += 1
        return True


    def screenshot_md5(self):
        return self.elem.xpath(
            'x:review_screenshot/x:checksum',
            namespaces = self.namespaces
        )[0].text

    def set_screenshot_md5(self, value):
        node = self.elem.xpath(
            'x:review_screenshot/x:checksum',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def screenshot_size(self):
        text = self.elem.xpath(
            'x:review_screenshot/x:size',
            namespaces = self.namespaces
        )[0].text
        return int(text)

    def set_screenshot_size(self, value):
        node = self.elem.xpath(
            'x:review_screenshot/x:size',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def screenshot_name(self):
        return self.elem.xpath(
            'x:review_screenshot/x:file_name',
            namespaces = self.namespaces
        )[0].text

    def set_screenshot_name(self, value):
        node = self.elem.xpath(
            'x:review_screenshot/x:file_name',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def set_product_id(self, value):
        node = self.elem.xpath(
            'x:product_id',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def type(self):
        node = self.elem.xpath(
            'x:type',
            namespaces = self.namespaces
        )[0]
        return node.text

    def set_type(self, value):
        node = self.elem.xpath(
            'x:type',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def reference_name(self):
        node = self.elem.xpath(
            'x:reference_name',
            namespaces = self.namespaces
        )[0]
        return node.text

    def set_reference_name(self, value):
        node = self.elem.xpath(
            'x:reference_name',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def title(self, locale):
        node = self.elem.xpath(
            'x:locales/x:locale[@name = $loc]/x:title',
            namespaces = self.namespaces,
            loc = locale
        )
        return node[0].text if node and len(node) else ''

    def set_title(self, value, locale):
        locs = self.elem.xpath(
            'x:locales',
            namespaces = self.namespaces
        )
        if not locs or len(locs) <= 0:
            etree.SubElement(self.elem, '{%s}locales' % XML_NAMESPACE)
            self.set_title(value, locale)
            return

        locale_nodes = self.elem.xpath(
            'x:locales/x:locale[@name = $loc]',
            namespaces = self.namespaces,
            loc = locale
        )
        if not locale_nodes or len(locale_nodes) <= 0:
            new_loc = etree.Element('{%s}locale' % XML_NAMESPACE)
            new_loc.set('name', locale)
            locs[0].append(new_loc)
            self.set_title(value, locale)

        nodes = self.elem.xpath(
            'x:locales/x:locale[@name = $loc]/x:title',
            namespaces = self.namespaces,
            loc = locale
        )
        if not nodes or len(nodes) <= 0:
            the_loc = locale_nodes[0]
            etree.SubElement(the_loc, '{%s}title' % XML_NAMESPACE)
            self.set_title(value, locale)
            return

        node = nodes[0]
        node.text = str(value)

    def description(self, locale):
        node = self.elem.xpath(
            'x:locales/x:locale[@name = $loc]/x:description',
            namespaces = self.namespaces,
            loc = locale
        )
        return node[0].text if node and len(node) else ''

    def set_description(self, value, locale):
        locs = self.elem.xpath(
            'x:locales',
            namespaces = self.namespaces
        )

        if not locs or len(locs) <= 0:
            etree.SubElement(self.elem, '{%s}locales' % XML_NAMESPACE)
            self.set_description(value, locale)
            return

        locale_nodes = self.elem.xpath(
            'x:locales/x:locale[@name = $loc]',
            namespaces = self.namespaces,
            loc = locale
        )
        if not locale_nodes or len(locale_nodes) <= 0:
            new_loc = etree.Element('{%s}locale' % XML_NAMESPACE)
            new_loc.set('name', locale)
            locs[0].append(new_loc)
            self.set_description(value, locale)

        nodes = self.elem.xpath(
            'x:locales/x:locale[@name = $loc]/x:description',
            namespaces = self.namespaces,
            loc = locale
        )
        if not nodes or len(nodes) <= 0:
            the_loc = locale_nodes[0]
            etree.SubElement(the_loc, '{%s}description' % XML_NAMESPACE)
            self.set_description(value, locale)
            return

        node = nodes[0]
        node.text = str(value)

    def review_notes(self):
        node = self.elem.xpath(
            'x:review_notes',
            namespaces = self.namespaces
        )
        return node[0].text if node and len(node) else ''

    def set_review_notes(self, value):
        nodes = self.elem.xpath(
            'x:review_notes',
            namespaces = self.namespaces
        )
        if not nodes or len(nodes) <= 0:
            node = etree.SubElement(self.elem, '{%s}review_notes' % XML_NAMESPACE)
        else:
            node = nodes[0]
        node.text = str(value)

    def cleared_for_sale(self):
        text = self.elem.xpath(
            'x:products/x:product/x:cleared_for_sale',
            namespaces = self.namespaces
        )[0].text
        return str(text) == 'true'

    def set_cleared_for_sale(self, value):
        node = self.elem.xpath(
            'x:products/x:product/x:cleared_for_sale',
            namespaces = self.namespaces
        )[0]
        node.text = 'true' if value else 'false'

    def __str__(self):
        return str(etree.tostring(self.elem, encoding = 'utf-8'), 'utf-8')


class Product:
    def __init__(self, p_dict):
        self.p_dict = p_dict

    def locales(self):
        return self.p_dict.get('locales')

    def raw_id(self):
        return self.p_dict[defs.KEY_PRODUCT_RAW_ID]

    def id(self):
        return self.p_dict[defs.KEY_PRODUCT_ID]

    def env(self):
        return self.p_dict[defs.KEY_ENV]

    def price_plan(self):
        return self.p_dict.get(defs.KEY_PRICE_PLAN)

    def appstore_price(self):
        self.p_dict[defs.KEY_APPSTORE_PRICE]

    def type(self):
        return self.p_dict[defs.KEY_TYPE]

    def set_type(self, value):
        self.p_dict[defs.KEY_TYPE] = value

    def reference_name(self):
        return self.p_dict[defs.KEY_REFERENCE_NAME]

    def set_reference_name(self, value):
        self.p_dict[defs.KEY_REFERENCE_NAME] = value

    def title(self, locale):
        loc = self.p_dict.get(locale)
        if not loc:
            return None
        return loc.get(defs.KEY_TITLE)

    def set_title(self, value, locale):
        loc = self.p_dict.get(locale)
        if not loc:
            return
        loc[defs.KEY_TITLE] = value

    def description(self, locale):
        loc = self.p_dict.get(locale)
        if not loc:
            return None
        return loc.get(defs.KEY_DESCRIPTION)

    def set_description(self, value, locale):
        loc = self.p_dict.get(locale)
        if not loc:
            return
        loc[defs.KEY_DESCRIPTION] = value

    def review_notes(self):
        return self.p_dict.get(defs.KEY_REVIEW_NOTES)

    def set_review_notes(self, value):
        self.p_dict[defs.KEY_REVIEW_NOTES] = value

    def cleared_for_sale(self):
        return self.p_dict.get(defs.KEY_CLEARED_FOR_SALE)

    def set_cleared_for_sale(self, value):
        self.p_dict[defs.KEY_CLEARED_FOR_SALE] = value

    def validity(self):
        return self.p_dict[defs.KEY_VALIDITY]

    def validityType(self):
        return self.p_dict[defs.KEY_VALIDITY_TYPE]

    def wrapped(self):
        return self.p_dict

    def __str__(self):
        return str(self.p_dict, 'utf-8')
