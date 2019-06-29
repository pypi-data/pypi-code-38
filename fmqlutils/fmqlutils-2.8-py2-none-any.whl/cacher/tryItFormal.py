#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
from fmqlutils.cacher.cacherUtils import FMQLReplyStore, zipAllReplies

def a():

    replyStore = FMQLReplyStore("/data/vista/999/DataV1RawToZip/")
    flTyp = "50_67"
    iter = replyStore.iterator(onlyTypes=[flTyp])
    for flJSON in iter.next():
        print "First", len(flJSON["results"])
        break
    lastReplyOfType = replyStore.lastReplyOfType(flTyp)
    print "Last Reply of Type", len(lastReplyOfType["results"]), lastReplyOfType["fmql"], lastReplyOfType.keys()
    print json.dumps(lastReplyOfType["results"][0], indent=4)

a()

def b():
    dir = "/data/vista/999/DataV1RawToZip/"
    zipAllReplies(dir)

# b()



