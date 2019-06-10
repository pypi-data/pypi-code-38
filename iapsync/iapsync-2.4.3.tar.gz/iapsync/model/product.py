__author__ = 'wansongHome'
import hashlib
from lxml import etree
from copy import deepcopy
from datetime import date, timedelta

from pathlib import PurePath, Path
from ..defs import defs

XML_NAMESPACE = 'http://apple.com/itunes/importer'

YESTODAY = (date.today() + timedelta(days = -1)).strftime('%Y-%m-%d')

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
    def get_screenshot_info(p_dict):
        screenshot_file = Path(p_dict[defs.KEY_REVIEW_SCREENSHOT])
        md5 = hashlib.md5(open(screenshot_file.as_posix(), 'rb').read()).hexdigest()
        return {
            'size': screenshot_file.stat().st_size,
            'md5': md5,
            'name': PurePath(p_dict[defs.KEY_REVIEW_SCREENSHOT]).name,
        }

    def create_node(p_dict):
        ret = deepcopy(TEMPLATE_NODE)
        pm = AppStoreProduct(ret)

        pm.set_product_id(p_dict[defs.KEY_PRODUCT_ID])
        pm.set_reference_name(p_dict[defs.KEY_REFERENCE_NAME])
        pm.set_price_tier(p_dict[defs.KEY_WHOLESALE_PRICE_TIER])
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

    def __init__(self, p_elem, namespace = XML_NAMESPACE):
        self.elem = p_elem
        self.namespaces = {'x': namespace}

    def locales(self):
        return self.elem.xpath(
            'x:locales/x:locale/@name',
            namespaces=self.namespaces
        )


    def price_tier(self):
        text = self.elem.xpath(
            'x:products/x:product/x:intervals/x:interval/x:wholesale_price_tier',
            namespaces = self.namespaces
        )[0].text
        return int(text)

    def set_price_tier(self, value):
        node = self.elem.xpath(
            'x:products/x:product/x:intervals/x:interval/x:wholesale_price_tier',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

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

    def price_tier(self):
        return self.p_dict.get(defs.KEY_WHOLESALE_PRICE_TIER)

    def set_price_tier(self, value):
        self.p_dict[defs.KEY_WHOLESALE_PRICE_TIER] = value

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
