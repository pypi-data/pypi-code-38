# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    Element.py
   Author :       Zhang Fan
   date：         2018/11/3
   Description :
-------------------------------------------------
"""
__author__ = 'Zhang Fan'

from zxpath2 import base_library
from zxpath2.Element_List import Element_List
from zxpath2.Text_Element import Text_Element


class Element():
    def __init__(self, src):
        self.name = 'comment' if base_library.is_comment(src) else src.tag.lower()
        self.base = src
        self.id = id(src)

        self._string = None
        self._text = None
        self._attrs = None

    # region 原始xpath代码查询
    def xpath(self, code, index: None or int = None):
        result = base_library.xpath(self.base, code=code, index=index)
        return self._build_Element(result)

    # endregion

    # region 原始css代码查询
    def css(self, code, index: None or int = None):
        result = base_library.css(self.base, code=code, index=index)
        return self._build_Element(result)

    # endregion

    # region 查询函数
    def find(self, name=None, class_=None, text=None, deep=True, index: None or int = None, **attrs):
        result = base_library.find(self.base, name=name, class_=class_, text=text, deep=deep, index=index, **attrs)
        return self._build_Element(result)

    # endregion

    # region 判断
    @property
    def is_element(self):
        return True

    @property
    def is_node_element(self):
        return True

    @property
    def is_text_element(self):
        return False

    @property
    def is_comment(self):
        return base_library.is_comment(self.base)

    def child_in(self, node):
        return self._child_in(node, check_me=False)

    def _child_in(self, node, check_me=False):
        assert isinstance(node, Element)

        if check_me:
            if node.id == self.id:
                return True

        for ancestor in node.ancestors:
            if ancestor.id == self.id:
                return True

        return False

    # endregion

    # region 转换-获取函数
    @property
    def string(self):
        # 返回此节点下所有的文本的组合
        return self.get_string()

    @property
    def text(self):
        # 返回此节点下文本
        return self.get_text()

    @property
    def tail(self):
        # 返回此节点的尾巴文本
        return self.get_tail()

    @property
    def html(self):
        return self.get_html()

    def get_string(self):
        if self._string is None:
            result = base_library.to_string(self.base)
            self._string = str(result)
        return self._string

    def get_text(self):
        if self._text is None:
            result = base_library.get_text(self.base)
            self._text = self._build_Element(result) if result else ''
        return self._text

    def get_tail(self):
        return self.base.tail or ''

    def get_html(self, encoding='utf8', method='xml', with_tail=False):
        return base_library.get_html(self.base, encoding=encoding, method=method, with_tail=with_tail)

    def get_attr(self, attr, default=None):
        value = self.attrs.get(attr)
        if value is None:
            return default
        return str(value)

    @property
    def attrs(self):
        if self._attrs is None:
            self._attrs = dict(self.base.attrib)
        return self._attrs

    # endregion

    # region 修改
    def change_text(self, text):
        # 修改节点的主要文本
        self.base.text = text

    def change_tail(self, text):
        # 修改节点的尾巴文本
        self.base.tail = text

    # endregion

    # region 删除
    def remove_attr(self, key):
        self.base.attrib.pop(key, '')
        self._attrs = None

    def remove_all_attr(self):
        self.base.attrib.clear()
        self._attrs = None

    def remove_self(self):
        base_library.find_parent(self.base).remove(self.base)
        self._string = None
        self._text = None
        self._attrs = None

    def remove(self, element):
        assert isinstance(element, Element), '只能删除zxpath2.Element对象'
        self.base.remove(element.base)
        self._string = None
        self._text = None
        self._attrs = None

    # endregion

    # region 节点树

    def find_pre(self, name=None, class_=None, text=None, index: None or int = None, **attrs):
        # 返回当前节点前面的所有同级对象
        result = base_library.find_pre(self.base, name=name, class_=class_, text=text, index=index, **attrs)
        return self._build_Element(result)

    def find_pre_node(self, name=None, class_=None, text=None, index: None or int = None, **attrs):
        # 返回当前节点前面的所有同级元素节点
        result = base_library.find_pre_node(self.base, name=name, class_=class_, text=text, index=index, **attrs)
        return self._build_Element(result)

    def find_next(self, name=None, class_=None, text=None, index: None or int = None, **attrs):
        # 返回当前节点后面的所有同级对象
        result = base_library.find_next(self.base, name=name, class_=class_, text=text, index=index, **attrs)
        return self._build_Element(result)

    def find_next_node(self, name=None, class_=None, text=None, index: None or int = None, **attrs):
        # 返回当前节点后面的所有同级元素节点
        result = base_library.find_next_node(self.base, name=name, class_=class_, text=text, index=index, **attrs)
        return self._build_Element(result)

    def find_child(self, name=None, class_=None, text=None, index: None or int = None, **attrs):
        # 返回当前节点的所有子对象
        result = base_library.find_child(self.base, name=name, class_=class_, text=text, index=index, **attrs)
        return self._build_Element(result)

    def find_child_node(self, name=None, class_=None, text=None, index: None or int = None, **attrs):
        # 返回当前节点的所有子元素节点
        result = base_library.find_child_node(self.base, name=name, class_=class_, text=text, index=index, **attrs)
        return self._build_Element(result)

    def find_parent(self):
        result = base_library.find_parent(self.base)
        return self._build_Element(result)

    def find_ancestor(self, name=None, class_=None, text=None, index: None or int = None, **attrs):
        result = base_library.find_ancestor(self.base, name=name, class_=class_, text=text, index=index, **attrs)
        return self._build_Element(result)

    @property
    def pre(self):
        result = base_library.find_pre(self.base, index=0)
        return self._build_Element(result)

    @property
    def pres(self):
        result = base_library.find_pre(self.base)
        return self._build_Element(result)

    @property
    def pre_node(self):
        result = base_library.find_pre_node(self.base, index=0)
        return self._build_Element(result)

    @property
    def pres_node(self):
        result = base_library.find_pre_node(self.base)
        return self._build_Element(result)

    @property
    def next(self):
        result = base_library.find_next(self.base, index=0)
        return self._build_Element(result)

    @property
    def nexts(self):
        result = base_library.find_next(self.base)
        return self._build_Element(result)

    @property
    def next_node(self):
        result = base_library.find_next_node(self.base, index=0)
        return self._build_Element(result)

    @property
    def nexts_node(self):
        result = base_library.find_next_node(self.base)
        return self._build_Element(result)

    @property
    def child(self):
        result = base_library.find_child(self.base, index=0)
        return self._build_Element(result)

    @property
    def childs(self):
        result = base_library.find_child(self.base)
        return self._build_Element(result)

    @property
    def child_node(self):
        result = base_library.find_child_node(self.base, index=0)
        return self._build_Element(result)

    @property
    def childs_node(self):
        result = base_library.find_child_node(self.base)
        return self._build_Element(result)

    @property
    def parent(self):
        result = base_library.find_parent(self.base)
        return self._build_Element(result)

    @property
    def ancestor(self):
        result = base_library.find_ancestor(self.base, index=0)
        return self._build_Element(result)

    @property
    def ancestors(self):
        result = base_library.find_ancestor(self.base)
        return self._build_Element(result)

    # endregion

    def __call__(self, name=None, class_=None, text=None, deep=True, index: None or int = None, **attrs):
        result = base_library.find(self.base, name=name, class_=class_, text=text, deep=deep, index=index, **attrs)
        return self._build_Element(result)

    def _build_Element(self, result):
        if isinstance(result, list):
            return Element_List([self._build_Element(node) for node in result])
        if not result is None:
            if isinstance(result, str):
                return Text_Element(result)
            return Element(result)

    def __getattr__(self, name):
        # 让这个对象能使用 obj.xxx 来获取属性或搜索一个节点
        if name == 'class_':
            name = 'class'
        result = self.__dict__.get(name)
        if result is None:
            result = self.get_attr(name, default=None)
        if result is None:
            result = self.find(name, deep=True, index=0)
        return result

    def __getitem__(self, name):
        # 让这个对象能使用 obj['xxx'] 来获取属性
        return self.attrs[name]

    def __str__(self):
        text = self.text or self.html
        return '<{}>:{}'.format(self.name, text if len(text) <= 20 else '{}...'.format(text[:17]))

    def __contains__(self, node):
        return self._child_in(node, check_me=True)

    def __eq__(self, other):
        return isinstance(other, Element) and self.id == other.id


def load(src):
    if base_library.is_element(src):
        assert not src is None, 'etree对象为None'
    else:
        assert isinstance(src, str), '只能传入etree对象或一个html结构的str类型, 你传入的是{}'.format(type(src))
        assert src, '不能传入空字符串'
        src = base_library.to_etree(src)
    return Element(src)
