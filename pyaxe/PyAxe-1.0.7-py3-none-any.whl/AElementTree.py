import re
from xml.etree import ElementTree

def getChildText(node, childTag, allowEmpty=False):
    childNode = node.find(childTag)
    if childNode is None or childNode.text is None or childNode.text == '':
        if allowEmpty:
            return ''
        else:
            raise RuntimeError('子节点 <%s> 不存在，或者内容为空' % childTag)
    return childNode.text


def getAttributeText(node, attribute, allowEmpty=False):
    try:
        text = node.attrib[attribute]
        if text == '':
            raise KeyError
        return text
    except KeyError:
        if allowEmpty:
            return ''
        else:
            raise RuntimeError('属性 %s 不存在，或者内容为空' % attribute)


def isTrueStr(s):
    return s in ('1', 'true')


def isFalseStr(s):
    return s in ('0', 'false')


def strToBool(s):
    if s not in ('0', '1', 'false', 'true'):
        raise RuntimeError('有效值为 0/1/false/true')
    if isTrueStr(s):
        return True
    else:
        return False


def getChildValue(node, childTag, optional=False, defaultValue=None, valueTransform=None):
    """
    :param optional: 若为True，表示可选（即该子节点可以不存在）
    :param defaultValue: 若optional为True，并且子节点不存在，则返回defaultValue
    :param valueTransform: 若不为None，则表示字符串将经过此函数转换
    """
    childNode = node.find(childTag)
    if childNode is None:
        if optional:
            return defaultValue
        else:
            raise RuntimeError('子节点 <%s> 不存在' % childTag)

    value = childNode.text

    if valueTransform is None:
        return value

    try:
        return valueTransform(value)
    except Exception as e:
        raise RuntimeError('子节点 <%s> 的值 %s 不是有效的 %s 值: %s' % (childTag, value, valueTransform.__name__, e))


def getAttributeValue(node, attribute, optional=False, defaultValue=None, valueTransform=None):
    """
    :param optional: 若为True，表示可选（即该属性可以不存在）
    :param defaultValue: 若optional为True，并且属性不存在，则返回defaultValue
    :param valueTransform: 若不为None，则表示字符串将经过此函数转换
    """
    if attribute not in node.attrib:
        if optional:
            return defaultValue
        else:
            raise RuntimeError('属性 %s 不存在' % attribute)

    value = node.attrib[attribute]

    if valueTransform is None:
        return value

    try:
        return valueTransform(value)
    except Exception as e:
        raise RuntimeError('属性 <%s> 的值 %s 不是有效的 %s 值: %s' % (attribute, value, valueTransform.__name__, e))


def getChildBool(node, childTag, optional=False, defaultValue=False):
    def bool(s):
        return strToBool(s)
    return getChildValue(node, childTag, optional, defaultValue, bool)


def getAttributeBool(node, attribute, optional=False, defaultValue=False):
    def bool(s):
        return strToBool(s)
    return getAttributeValue(node, attribute, optional, defaultValue, bool)


class SimpleParser:
    """ Parse XML file into structure """
    def __init__(self, filePath):
        self._filePath = filePath

    def _parse(self, rootNode):
        raise NotImplementedError

    def parse(self):
        try:
            rootNode = ElementTree.ElementTree(file=self.filePath).getroot()
            self._parse(rootNode)
        except Exception as e:
            raise RuntimeError('文件 %s，解析失败：%s' % (self.filePath, e))

    @property
    def filePath(self):
        return self._filePath


class SimpleConfigNode:
    def __init__(self, ownerConfig):
        self.ownerConfig = ownerConfig


class SimpleConfig(SimpleParser):
    """ Parse XML file into structure
    :param nodes a tuple of (name, cls)
    """
    def __init__(self, nodes, filePath='Config.xml'):
        self._filePath = filePath
        self._nodes = nodes

    def _parse(self, rootNode):
        for node in self._nodes:
            name = node[0]
            cls = node[1]
            xmlNode = rootNode.find(name)
            if xmlNode is None:
                raise RuntimeError('<%s> 节点不存在' % name)
            instance = cls(self)
            try:
                instance.parseNode(xmlNode)
            except Exception as e:
                raise RuntimeError('<%s> 节点：%s' % (name, e))
            setattr(self, name, instance)


def getNamespace(node):
    """{http://www.w3.org/2001/XMLSchema}schema -> {http://www.w3.org/2001/XMLSchema}"""
    m = re.match('\{.*\}', node.tag)
    return m.group(0) if m else ''
