# -*- coding:utf-8 -*-
__author__ = 'denishuang'
import copy
from lxml import etree

MATCHES_DEMO = {
    "$e": "//div[@class=\"box\"]",
    "title": {"$e": "./h1/text()"},
    "shitis": {
        "$es": "./div[@class=\"shiti\"]",
        "title": "./h3/text()",
        "imgage": "./a/img/@data-remote",
        "options": {
            "$es": "./ul/li/label",
            "text": "./text()"
        },
        "answer": "./ul/li[@class=\"help\"]/b/text()"
    }
}

import json


def extra_html_data(matches, element):
    ms = copy.deepcopy(matches)
    r = {}
    e = element
    # print element.tag, json.dumps(ms, indent=2)
    if "$es" in ms:
        p = ms.pop("$es")
        # print p
        try:
            es = element.xpath(p)
            # print "find $es: %d" % len(es)
        except Exception, e:
            raise Exception(u"XPathEvelError: %s %s" % (p,e))
        return [extra_html_data(ms, e) for e in es]
    if "$e" in ms:
        p = ms.pop("$e")
        # print p
        try:
            es = element.xpath(p)
            # print "find $e"
        except Exception, e:
            raise Exception(u"XPathEvelError: %s %s" % (p,e))
        if len(es) == 0:
            return
        e = es[0]
        if len(ms) == 0:
            if isinstance(e, basestring):
                return e
            if p.endswith("text()"):
                t = "".join(e)
            else:
                t = "".join([se.text for se in e])
            return t

    for k, v in ms.iteritems():
        r[k] = extra_html_data(isinstance(v, basestring) and {"$e": v} or v, e)
    return r
