import re
import json


def jsonp_to_json(jsonp_text, format='str'):
    """
    将Jsonp格式以Json格式解析出来
    :param jsonp_text: 要解析的Jsonp文本
    :param format: 要解析为的格式, 可以是str或dict
    :return:
    """
    text_wihtout_new_line = re.sub('\s', '', jsonp_text)
    jsn = re.findall('.*\(({.*})\)[;]{0,1}', text_wihtout_new_line)[0]
    jsn_dict = json.loads(jsn)
    if format == 'dict':
        return jsn_dict
    elif format == 'str':
        return json.dumps(jsn_dict, indent=2, ensure_ascii=False)
    else:
        raise ValueError


def _plot(node, plot='', level=0):
    if isinstance(node, str):
        plot += (' ' * 2) * (level + 1) + '|-- ' + node + '\n'
    elif isinstance(node, dict):
        for k in node:
            v = node[k]
            plot = _plot(plot=plot, node=k, level=level)
            plot = _plot(plot=plot, node=v, level=level + 1)
    elif isinstance(node, (list, tuple)):
        node = sorted(node, key=lambda e: not isinstance(e, str))
        for i, e in enumerate(node):
            plot = _plot(plot=plot, node=e, level=level + 1)
    else:
        plot = _plot(plot=plot, node=node.__str__(), level=level + 1)

    return plot


def plot_json_tree(d):
    print(_plot(d))
