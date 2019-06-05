# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    base_library.py
   Author :       Zhang Fan
   date：         2018/11/3
   Description :
-------------------------------------------------
"""
__author__ = 'Zhang Fan'

from lxml import etree


def get_once(result, index=0, default=None):
    if result and len(result) > index:
        if index >= 0 or len(result) >= -index:
            return result[index]
    return default


# region xpath原始查询代码
def xpath(node, code, index: None or int = None):
    result = node.xpath(code)
    if isinstance(index, int):
        return get_once(result, index)
    return result


# endregion

# region xpath原始查询代码
def css(node, code, index: None or int = None):
    result = node.cssselect(code)
    if isinstance(index, int):
        return get_once(result, index)
    return result


# endregion

# region 比较判断

def is_element(obj):
    return isinstance(obj, (etree._Element, etree._ElementUnicodeResult, etree._Comment, etree._ElementStringResult))


def is_node_element(obj):
    # 判断对象是否为元素节点
    return isinstance(obj, etree._Element)


def is_text_element(obj):
    # 判断对象是否为文本节点
    return isinstance(obj, (etree._ElementUnicodeResult, etree._ElementStringResult))


def is_comment(obj):
    return isinstance(obj, etree._Comment)


# endregion

# region 转换获取

def to_etree(text):
    return etree.HTML(text)


def to_string(node):
    if isinstance(node, list):
        result = []
        for s in node:
            s = to_string(s)
            if s:
                result.append(s)
        return result
    else:
        return node.xpath('string(.)') or ''


def get_text(node):
    if isinstance(node, list):
        result = []
        for s in node:
            s = get_text(s)
            if s:
                result.append(s)
        return result
    else:
        return get_once(node.xpath('./text()'))


def get_attr(node, attr, default=None):
    return get_once(node.xpath('./@' + attr), default)


def get_html(node, encoding='utf8', method='xml', with_tail=False):
    bhtml = etree.tostring(node, encoding=encoding, method=method, with_tail=with_tail)
    if encoding:
        return bhtml.decode(encoding)
    return bhtml.decode()


# endregion

# region 高级查询

def _parser_attr(**attrs):
    if len(attrs) == 0:
        return ''

    fmt = '[{}]'
    attr_fmt_all = '@{}'
    attr_fmt = '@{}="{}"'
    not_fmt = 'not({})'
    text_fmt = 'text()="{}"'

    search_attrs = []  # 查询属性
    not_attrs = []  # 排除属性

    for key, value in attrs.items():
        if value is None:  # 排除无效属性值
            continue

        # 判断是否为排除属性
        _not = False
        if value is False:
            _not = True

        # 去除前端下划线,并标记为排除
        if key[0] == '_':
            _not = True
            key = key[1:]

        # 去除class_尾部下划线
        if key == 'class_':
            key = 'class'

        # 将key:value转换为xpath查询格式
        if value is True or value is False:
            attr_text = 'text()' if key == 'text' else attr_fmt_all.format(key)
        else:
            attr_text = text_fmt.format(value) if key == 'text' else attr_fmt.format(key, value)

        search_attrs.append(attr_text) if not _not else not_attrs.append(attr_text)

    # 检查排除属性
    if not_attrs:
        not_attrs = ' or '.join(not_attrs)
        not_attrs = not_fmt.format(not_attrs)
        search_attrs.append(not_attrs)

    # 连接属性
    search_attrs = ' and '.join(search_attrs)

    if search_attrs:
        return fmt.format(search_attrs)
    return ''


def _find(node, prefix, name=None, class_=None, text=None, index: None or int = None, **attrs):
    fmt = '{prefix}{name}{attr_text}'
    attr_text = _parser_attr(class_=class_, text=text, **attrs)
    code = fmt.format(prefix=prefix, name=name or 'node()', attr_text=attr_text)
    return xpath(node, code, index)


def find(node, name=None, class_=None, text=None, deep=True, index: None or int = None, **attrs):
    '''
    查询节点
    :param node: 原始节点
    :param name: 元素名, 如果不是str类型则查找所有元素, *表示标签元素, node()表示所有元素
    :param class_: class属性
    :param text: 文本值
    :param deep: 是否深度查询孙节点
    :param index: 取出第几个结果
    :param attrs: 属性名前加下划线_会排除这个属性, 如_id=True表示不存在id的元素, 属性值为True, 表示这个属性匹配任意值
    :return: index存在时: 成功返回etree._Element节点, 失败返回None, index不存在时:返回包含etree._Element节点的列表
    '''
    prefix = './/' if deep else './'
    return _find(node, prefix, name=name, class_=class_, text=text, index=index, **attrs)


# endregion

# region 节点树

def find_pre(node, name=None, class_=None, text=None, index: None or int = None, **attrs):
    # 返回当前节点前面的所有同级元素节点
    return _find(node, 'preceding-sibling::', name=name, class_=class_, text=text, index=index, **attrs)


def find_pre_node(node, name=None, class_=None, text=None, index: None or int = None, **attrs):
    # 返回当前节点前面的所有同级元素节点
    return _find(node, 'preceding-sibling::', name=name or '*', class_=class_, text=text, index=index, **attrs)


def find_next(node, name=None, class_=None, text=None, index: None or int = None, **attrs):
    # 返回当前节点后面的所有同级元素节点
    return _find(node, 'following-sibling::', name=name, class_=class_, text=text, index=index, **attrs)


def find_next_node(node, name=None, class_=None, text=None, index: None or int = None, **attrs):
    # 返回当前节点后面的所有同级元素节点
    return _find(node, 'following-sibling::', name=name or '*', class_=class_, text=text, index=index, **attrs)


def find_child(node, name=None, class_=None, text=None, index: None or int = None, **attrs):
    # 返回当前节点的所有子元素节点
    return _find(node, 'child::', name=name, class_=class_, text=text, index=index, **attrs)


def find_child_node(node, name=None, class_=None, text=None, index: None or int = None, **attrs):
    # 返回当前节点的所有子元素节点
    return _find(node, 'child::', name=name or '*', class_=class_, text=text, index=index, **attrs)


def find_parent(node):
    return get_once(node.xpath('parent::*'))


def find_ancestor(node, name=None, class_=None, text=None, index: None or int = None, **attrs):
    return _find(node, 'ancestor::', name=name, class_=class_, text=text, index=index, **attrs)
# endregion
