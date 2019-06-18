# -*- coding:utf-8 -*-
from django.template.defaultfilters import urlencode

__author__ = 'denishuang'
from django_szuprefix.utils import datautils, statutils
from django.template import Library, Node
from django.utils import six
register = Library()


@register.filter(is_safe=True)
def phonemask(value):
    return datautils.phone_mask(six.text_type(value))

@register.filter(is_safe=True)
def range_number(value):
    return range(value)


@register.filter(is_safe=True)
def get(obj, key):
    try:
        return obj[key]
    except:
        return obj.get(key)

@register.filter(is_safe=True)
def getattr(obj, key):
    try:
        return getattr(obj,key)
    except:
        return None


@register.filter('range')
def do_range(value):
    return range(1, value+1)

@register.filter('jsondumps')
def json_dumps(value):
    import json
    return json.dumps(value)

@register.filter('jsonloads')
def json_loads(value):
    import json
    return json.loads(value)

@register.filter(name='replace')
def do_replace(value, arg):
    arg_list = arg.split(",")
    if len(arg_list) != 2:
        return False
    return value.replace(arg_list[0].strip(), arg_list[1].strip())


class StatObjectNode(Node):
    def __init__(self, parser, token,nodelist):
        self.nodelist = nodelist
        bits = token.split_contents()
        self.obj = bits[1]
        if bits[-2] == 'as':
            self.as_var = bits[-1]

    def render(self, context):
        c={}
        if self.as_var:
            c[self.as_var] = statutils.StatObject(context[self.obj])
        with context.push(**c):
            return self.nodelist.render(context)


@register.tag
def statobject(parser, token):
    nodelist = parser.parse(('endstatobject',))
    parser.delete_first_token()
    return StatObjectNode(parser, token, nodelist=nodelist)

@register.filter('stat_by_fields')
def stat_by_fields(qset,fields):
    ss=statutils.StructorStat(qset,fields.split(","))
    return ss.stat()


@register.filter(name='zero_default')
def when_zero_default_zero(value, str):
    if value:
        return value
    else:
        if value == 0:
            return 0
        else:
            return str


@register.filter(name="urlencode")
def html_urlencode(value):
    if value:
        return urlencode(value)


def match(obj, cond):
    opr_unequal = "!="
    opr_equal = "="
    if opr_unequal in cond:
        field, value = cond.split(opr_unequal)
        if value != unicode(obj.get(field)):
            return True
    else:
        field, value = cond.split(opr_equal)
        if value == unicode(obj.get(field)):
            return True
    return False

@register.filter(is_safe=True)
def myfilter(data,conds):
    if isinstance(conds, basestring):
        conds = conds.split(",")
    r = data
    for cond in conds:
        f = lambda x:match(x,cond)
        r= filter(f,r)
    return r

@register.filter(is_safe=True)
def sum_key(data, key):
    return sum([x[key] for x in data])

@register.filter(is_safe=True)
def count_keys(data, conds):
    return sum_key(myfilter(data,conds),"C")

@register.filter(is_safe=True)
def percentage(val1, val2):
    return 1.0*val1/val2*100.0

@register.filter(is_safe=True)
def wx_avatar(value):
    if value is None:
        return ""
    if value.endswith("/0"):
        return "%s/100" % value[:-2]
    return "%s64" % value

