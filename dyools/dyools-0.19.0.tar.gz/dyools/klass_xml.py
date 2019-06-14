from __future__ import (absolute_import, division, print_function, unicode_literals)

from lxml import etree


class XmlNode(object):
    def __init__(self, node):
        if not isinstance(node, list):
            node = [node]
        self.__nodes = node

    def add(self, node):
        if not isinstance(node, list):
            node = [node]
        self.__nodes.extend(node)

    def attrib(self, attr, value):
        for node in self.__nodes:
            node.attrib[attr] = value

    def text(self, value):
        for node in self.__nodes:
            node.text = value

    @property
    def nodes(self):
        return self.__nodes

    def __iter__(self):
        return iter(self.__nodes)


class Xml(object):
    SEPARATOR = '=' * 10

    def __init__(self, arch, separator=False):
        self.arch = arch
        self.separator = separator
        if separator:
            assert arch.count(separator) == 2, 'The separator is not in the architecture'
            arch = self._extract_lines()
        self.root = etree.fromstring(arch)

    def _extract_lines(self):
        result = ''
        ok = False
        for line in self.arch.split('\n'):
            if result:
                result += '\n'
            if self.separator.strip() == line.strip():
                if not ok:
                    ok = True
                    continue
                else:
                    break
            if ok:
                result += line
        return result

    def _full_path(self, xpath, node):
        node = node.getparent()
        if xpath.startswith('//'):
            xpath = xpath[1:]
        items = [xpath]
        while node:
            s = '{}'.format(node.tag)
            if node.attrib.get('name'):
                s += '[@name="{}"]'.format(node.attrib['name'])
            items.append(s)
            node = node.getparent()
        return '//' + '/'.join(items[::-1])

    def _xpath(self, *tags, **attrs):
        nodes = []
        for xpath in self.get_xpath_expr(*tags, **attrs):
            for node in self.root.xpath(xpath):
                nodes.append(node)
        return XmlNode(nodes)

    def nodes(self, *tags, **attrs):
        return self._xpath(*tags, **attrs)

    def all_nodes(self):
        return [node for node in self.root.xpath('//*')]

    def get_xpath_expr(self, *tags, **attrs):
        _prefix = attrs.pop('_prefix', '//')
        expressions = []
        if not tags:
            tags = ['*']
        for tag in tags:
            if attrs:
                xpath = '{}{}[{}]'.format(_prefix, tag,
                                          ' and '.join(['@{}="{}"'.format(k, v) for k, v in attrs.items()]))
            else:
                xpath = '{}{}'.format(_prefix, tag)
            expressions.append(xpath)
        return expressions

    def query(self, tag, attr, attrs={}, only_parent=False, child_of=False, under=False):
        def parent_node(node):
            is_under = False
            initial = value = node.attrib.get(attr)
            path = tag
            while node.getparent() is not None:
                node = node.getparent()
                path = '{}.{}'.format(node.tag, path)
                if node.tag == tag and node.attrib.get(attr):
                    value = '{}.{}'.format(node.attrib.get(attr), value)
                if node.tag == under:
                    is_under = True
            return initial, value, path, is_under

        nodes = []
        for node in self._xpath(tag):
            ok = True
            for k, v in attrs.items():
                if not isinstance(v, (list, tuple)):
                    v = [v]
                if node.attrib.get(k) not in v:
                    ok = False
            if ok:
                nodes.append(node)
        res = [parent_node(node) for node in nodes]
        if only_parent:
            res = filter(lambda s: not s[1].count('.'), res)
        if child_of:
            res = filter(lambda s: s[1].startswith('{}.'.format(child_of)), res)
            res = map(lambda s: (s[0], s[1], s[2][len(child_of) + 1:], s[3]), res)
        if under:
            res = filter(lambda s: s[3], res)
        return list(map(lambda r: [r[0], r[1], r[2]], res))

    def xpath(self, *tags, **attrs):
        return [etree.tostring(node).strip() for node in self._xpath(*tags, **attrs)]

    def expr(self, *tags, **attrs):
        result = []
        for xpath in self.get_xpath_expr(*tags, **attrs):
            for node in self.root.xpath(xpath):
                result.append(['Xpath', xpath])
                result.append(['Expression', self._full_path(xpath, node)])
        return result

    def expr_with_arch(self, *tags, **attrs):
        result = []
        for xpath in self.get_xpath_expr(*tags, **attrs):
            for node in self.root.xpath(xpath):
                result.append(['Xpath', xpath])
                result.append(['Expression', self._full_path(xpath, node)])
                result.append(['Architecture', self.pretty(node).strip()])
        return result

    def _to_string(self, node=None, pretty_print=False):
        if node is None:
            node = self.root
        try:
            return etree.tostring(node, pretty_print=pretty_print, encoding='utf-8').decode('utf-8')
        except:
            return etree.tostring(node, pretty_print=pretty_print, encoding='utf-8')

    def to_string(self, node=None):
        if node is None:
            node = self.root
        return self._to_string(node, pretty_print=False)

    def pretty(self, node=None):
        if node is None:
            node = self.root
        return self._to_string(node, pretty_print=True)

    def __len__(self):
        return len(self.all_nodes())
